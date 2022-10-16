import time
import hashlib
import json
from typing import Union
import requests
from django.conf import settings
from pyclick.models import ClickTransaction
from pyclick.status import SUCCESS, ALREADY_PAID


class ApiHelper:
    endpoint = 'https://api.click.uz/v2/merchant'

    def __init__(self, data):
        self.data = data
        self.transaction_id = data.get('transaction_id', None)
        self.timestamps = int(time.time())
        self.merchant_user_id = settings.CLICK_SETTINGS['merchant_user_id']
        self.service_id = settings.CLICK_SETTINGS['service_id']
        self.token = hashlib.sha1('{timestamps}{secret_key}'.format(
            timestamps=self.timestamps, secret_key=settings.CLICK_SETTINGS['secret_key']
        ).encode('utf-8')).hexdigest()

    @classmethod
    def get_extra_data(cls, transaction: ClickTransaction):
        extra_data = {}
        try:
            extra_data = json.loads(transaction.extra_data)
        except Exception:
            pass
        return extra_data

    @classmethod
    def save_extra_data(cls, transaction: ClickTransaction, extra_data: dict):
        transaction.extra_data = json.dumps(extra_data)
        transaction.save()

    def post(self, url: str, data: dict):
        response = requests.post(self.endpoint + url, json=data, headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Auth': '{}:{}:{}'.format(self.merchant_user_id, self.token, self.timestamps)
        })
        return response

    def get(self, url: str):
        response = requests.get(self.endpoint + url, headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Auth': '{}:{}:{}'.format(self.merchant_user_id, self.token, self.timestamps)
        })
        return response

    def delete(self, url: str):
        response = requests.delete(self.endpoint + url, headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Auth': '{}:{}:{}'.format(self.merchant_user_id, self.token, self.timestamps)
        })
        return response

    @classmethod
    def make_error_response(cls, status_code: int) -> dict:
        return {
            'status': -1 * status_code,
            'status_note': 'Http request error [{}]'.format(status_code)
        }

    @classmethod
    def get_transaction(cls, transaction_id: int) -> Union[ClickTransaction, dict]:
        try:
            transaction = ClickTransaction.objects.get(id=int(transaction_id))
            return transaction
        except ClickTransaction.DoesNotExist:
            return {
                'error': -5001,
                'error_note': 'Transaction not found'
            }

    def create_invoice(self):
        transaction = self.get_transaction(self.transaction_id)
        if isinstance(transaction, ClickTransaction):
            invoice = self.post('/invoice/create', {
                'service_id': self.service_id,
                'amount': float(transaction.amount),
                'phone_number': self.data['phone_number'],
                'merchant_trans_id': self.transaction_id
            })
            if invoice.status_code == 200:
                _json = invoice.json()
                extra_data = self.get_extra_data(transaction)
                extra_data['payment'] = {
                    'type': 'phone_number',
                    'phone_number': self.data['phone_number'],
                    'invoice': _json
                }
                self.save_extra_data(transaction, extra_data)
                if _json['error_code'] == SUCCESS:
                    transaction.change_status(ClickTransaction.PROCESSING)
                else:
                    transaction.change_status(ClickTransaction.ERROR)
                transaction.message = json.dumps(_json)
                transaction.save()
                return _json
            return self.make_error_response(invoice.status_code)
        else:
            return transaction

    def check_invoice(self):
        transaction = self.get_transaction(self.transaction_id)
        if isinstance(transaction, ClickTransaction):
            check_invoice = self.get('/invoice/status/{service_id}/{invoice_id}'.format(
                service_id=self.service_id,
                invoice_id=self.data['invoice_id']
            ))
            if check_invoice.status_code == 200:
                _json = check_invoice.json()
                if _json['status'] > 0:
                    transaction.change_status(ClickTransaction.CONFIRMED)
                elif _json['status'] == -99:
                    transaction.change_status(ClickTransaction.CANCELED)
                elif _json['status'] < 0:
                    transaction.change_status(ClickTransaction.ERROR)
                transaction.message = json.dumps(_json)
                transaction.save()
                return _json
            return self.make_error_response(check_invoice.status_code)
        else:
            return transaction

    def check_payment_status(self):
        transaction = self.get_transaction(self.transaction_id)
        if isinstance(transaction, ClickTransaction):
            check_payment = self.get('/payment/status/{service_id}/{payment_id}'.format(
                service_id=self.service_id,
                payment_id=transaction.click_paydoc_id
            ))
            if check_payment.status_code == 200:
                _json = check_payment.json()
                if _json['payment_status'] and _json['payment_status'] == 2:
                    transaction.change_status(ClickTransaction.CONFIRMED)
                elif _json['payment_status'] and _json['payment_status'] < 0:
                    transaction.change_status(ClickTransaction.ERROR)
                transaction.message = json.dumps(_json)
                transaction.save()
                return _json
            return self.make_error_response(check_payment.status_code)
        else:
            return transaction

    def create_card_token(self):
        transaction = self.get_transaction(self.transaction_id)
        if isinstance(transaction, ClickTransaction):
            if transaction.status == ClickTransaction.CONFIRMED:
                return {
                    'error': ALREADY_PAID,
                    'error_note': 'Transaction already paid'
                }
            data = {
                'service_id': self.service_id,
                'card_number': self.data['card_number'],
                'expire_date': self.data['expire_date'],
                'temporary': self.data['temporary']
            }
            response = self.post('/card_token/request', data=data)
            if response.status_code == 200:
                _json = response.json()
                extra_data = self.get_extra_data(transaction)
                extra_data['payment'] = {
                    'type': 'card_number',
                    'card_number': self.data['card_number'],
                    'temporary': self.data['temporary'],
                    'card_token': _json
                }
                self.save_extra_data(transaction, extra_data)
                if _json['error_code'] == 0:
                    transaction.change_status(ClickTransaction.PROCESSING)
                else:
                    transaction.change_status(ClickTransaction.ERROR)
                transaction.message = json.dumps(_json)
                transaction.save()
                return _json
            return self.make_error_response(response.status_code)
        else:
            return transaction

    def verify_card_token(self):
        transaction = self.get_transaction(self.transaction_id)
        if isinstance(transaction, ClickTransaction):
            if transaction.status != ClickTransaction.PROCESSING:
                return {
                    'error': -5001,
                    'error_note': 'Transaction is not ready'
                }
            data = {
                'service_id': self.service_id,
                'card_token': self.data['card_token'],
                'sms_code': self.data['sms_code']
            }
            response = self.post('/card_token/verify', data)
            if response.status_code == 200:
                _json = response.json()
                if not _json['error_code'] == 0:
                    transaction.change_status(ClickTransaction.ERROR)
                transaction.message = json.dumps(_json)
                transaction.save()
                return _json
            return self.make_error_response(response.status_code)
        else:
            return transaction

    def payment_with_token(self):
        transaction = self.get_transaction(self.transaction_id)
        if isinstance(transaction, ClickTransaction):
            if transaction.status != ClickTransaction.PROCESSING:
                return {
                    'error': -5001,
                    'error_note': 'Transaction is not ready'
                }
            data = {
                "service_id": self.service_id,
                "card_token": self.data['card_token'],
                "amount": str(transaction.amount),
                "transaction_parameter": self.transaction_id
            }
            response = self.post('/card_token/payment', data=data)
            if response.status_code == 200:
                _json = response.json()
                if _json['error_code'] == 0:
                    transaction.change_status(ClickTransaction.CONFIRMED)
                else:
                    transaction.change_status(ClickTransaction.ERROR)
                transaction.click_paydoc_id = _json['payment_id']
                transaction.save()
                transaction.message = json.dumps(_json)
                transaction.save()
                return _json
            return self.make_error_response(response.status_code)
        else:
            return transaction

    def delete_card_token(self):
        data = {
            'service_id': self.service_id,
            'card_token': self.data['card_token']
        }
        response = self.delete('/card_token/{service_id}/{card_token}'.format(**data))
        if response.status_code == 200:
            return response.json()
        return self.make_error_response(response.status_code)

    def cancel_payment(self):
        transaction = self.get_transaction(self.transaction_id)
        if isinstance(transaction, ClickTransaction):
            data = {
                'service_id': self.service_id,
                'payment_id': transaction.click_paydoc_id
            }
            response = self.delete('/payment/reversal/{service_id}/{payment_id}'.format(**data))
            if response.status_code == 200:
                _json = response.json()
                if _json['error_code'] == 0:
                    transaction.change_status(ClickTransaction.CANCELED)
                transaction.message = json.dumps(_json)
                transaction.save()
                return _json
            return self.make_error_response(response.status_code)
        return transaction


class Services(ApiHelper):
    def __init__(self, data, service_type):
        self.data = data
        self.service_type = service_type
        super().__init__(self.data)

    def api(self):
        if self.service_type == 'create_invoice':
            return self.create_invoice()
        elif self.service_type == 'check_invoice':
            return self.check_invoice()
        elif self.service_type == 'check_payment_status':
            return self.check_payment_status()
        elif self.service_type == 'create_card_token':
            return self.create_card_token()
        elif self.service_type == 'verify_card_token':
            return self.verify_card_token()
        elif self.service_type == 'payment_with_token':
            return self.payment_with_token()
        elif self.service_type == 'delete_card_token':
            return self.delete_card_token()
        elif self.service_type == 'cancel_payment':
            return self.cancel_payment()
        else:
            return {
                'error': -1000,
                'error_note': 'Service type could not be detected'
            }
