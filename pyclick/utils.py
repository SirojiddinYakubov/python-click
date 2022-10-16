import hashlib
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView, Response
from pyclick.authorization import authorization
from pyclick.models import ClickTransaction
from pyclick.serializers import ClickTransactionSerializer
from pyclick.status import (PREPARE, COMPLETE, AUTHORIZATION_FAIL_CODE, AUTHORIZATION_FAIL, ACTION_NOT_FOUND,
                            ORDER_NOT_FOUND, INVALID_AMOUNT, ALREADY_PAID, TRANSACTION_NOT_FOUND, TRANSACTION_CANCELLED,
                            SUCCESS)


class PyClickMerchantAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    VALIDATE_CLASS = None

    def post(self, request):
        serializer = ClickTransactionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        METHODS = {
            PREPARE: self.prepare,
            COMPLETE: self.complete
        }

        merchant_trans_id = serializer.validated_data['merchant_trans_id']
        amount = serializer.validated_data['amount']
        action = serializer.validated_data['action']
        if authorization(**serializer.validated_data) is False:
            return Response({
                "error": AUTHORIZATION_FAIL_CODE,
                "error_note": AUTHORIZATION_FAIL
            })

        assert self.VALIDATE_CLASS
        check_order = self.VALIDATE_CLASS().check_order(order_id=merchant_trans_id, amount=amount)
        if check_order is True:
            result = METHODS[action](**serializer.validated_data)
            return Response(result)
        return Response({"error": check_order})

    @classmethod
    def order_load(cls, order_id):
        if int(order_id) > 1000000000:
            return None
        transaction = get_object_or_404(ClickTransaction, id=int(order_id))
        return transaction

    @classmethod
    def click_webhook_errors(cls, click_trans_id: str,
                             service_id: str,
                             merchant_trans_id: str,
                             amount: str,
                             action: str,
                             sign_time: str,
                             sign_string: str,
                             error: str,
                             merchant_prepare_id: str = None) -> dict:

        merchant_prepare_id = merchant_prepare_id if action and action == '1' else ''
        created_sign_string = '{}{}{}{}{}{}{}{}'.format(
            click_trans_id, service_id, settings.CLICK_SETTINGS['secret_key'],
            merchant_trans_id, merchant_prepare_id, amount, action, sign_time)
        encoder = hashlib.md5(created_sign_string.encode('utf-8'))
        created_sign_string = encoder.hexdigest()
        if created_sign_string != sign_string:
            return {
                'error': AUTHORIZATION_FAIL_CODE,
                'error_note': _('SIGN CHECK FAILED!')
            }

        if action not in [PREPARE, COMPLETE]:
            return {
                'error': ACTION_NOT_FOUND,
                'error_note': _('Action not found')
            }

        order = cls.order_load(merchant_trans_id)
        if not order:
            return {
                'error': ORDER_NOT_FOUND,
                'error_note': _('Order not found')
            }

        if abs(float(amount) - float(order.amount) > 0.01):
            return {
                'error': INVALID_AMOUNT,
                'error_note': _('Incorrect parameter amount')
            }

        if order.status == ClickTransaction.CONFIRMED:
            return {
                'error': ALREADY_PAID,
                'error_note': _('Already paid')
            }

        if action == COMPLETE:
            if merchant_trans_id != merchant_prepare_id:
                return {
                    'error': TRANSACTION_NOT_FOUND,
                    'error_note': _('Transaction not found')
                }

        if order.status == ClickTransaction.CANCELED or int(error) < 0:
            return {
                'error': TRANSACTION_CANCELLED,
                'error_note': _('Transaction cancelled')
            }
        return {
            'error': SUCCESS,
            'error_note': 'Success'
        }

    @classmethod
    def prepare(cls, click_trans_id: str,
                service_id: str,
                click_paydoc_id: str,
                merchant_trans_id: str,
                amount: str,
                action: str,
                sign_time: str,
                sign_string: str,
                error: str,
                error_note: str,
                *args, **kwargs) -> dict:
        """
        :param click_trans_id:
        :param service_id:
        :param click_paydoc_id:
        :param merchant_trans_id:
        :param amount:
        :param action:
        :param sign_time:
        :param sign_string:
        :param error:
        :param error_note:
        :param args:
        :param kwargs:
        :return:
        """
        result = cls.click_webhook_errors(click_trans_id, service_id, merchant_trans_id,
                                          amount, action, sign_time, sign_string, error)
        order = cls.order_load(merchant_trans_id)
        if result['error'] == '0':
            order.status = ClickTransaction.WAITING
            order.save()
        result['click_trans_id'] = click_trans_id
        result['merchant_trans_id'] = merchant_trans_id
        result['merchant_prepare_id'] = merchant_trans_id
        result['merchant_confirm_id'] = merchant_trans_id
        return result

    @classmethod
    def complete(cls, click_trans_id: str,
                 service_id: str,
                 click_paydoc_id: str,
                 merchant_trans_id: str,
                 amount: str,
                 action: str,
                 sign_time: str,
                 sign_string: str,
                 error: str,
                 error_note: str,
                 merchant_prepare_id: str = None,
                 *args, **kwargs) -> dict:
        """
        :param click_trans_id:
        :param service_id:
        :param click_paydoc_id:
        :param merchant_trans_id:
        :param amount:
        :param action:
        :param sign_time:
        :param sign_string:
        :param error:
        :param error_note:
        :param merchant_prepare_id:
        :param args:
        :param kwargs:
        :return:
        """
        order = cls.order_load(merchant_trans_id)
        result = cls.click_webhook_errors(click_trans_id, service_id, merchant_trans_id,
                                          amount, action, sign_time, sign_string, error, merchant_prepare_id)
        if error and int(error) < 0:
            order.change_status(ClickTransaction.CANCELED)
        if result['error'] == SUCCESS:
            order.change_status(ClickTransaction.CONFIRMED)
            order.click_paydoc_id = click_paydoc_id
            order.save()
            cls.VALIDATE_CLASS().successfully_payment(order)
        result['click_trans_id'] = click_trans_id
        result['merchant_trans_id'] = merchant_trans_id
        result['merchant_prepare_id'] = merchant_prepare_id
        result['merchant_confirm_id'] = merchant_prepare_id
        return result

    @staticmethod
    def generate_url(order_id, amount, return_url=None):
        service_id = settings.CLICK_SETTINGS['service_id']
        merchant_id = settings.CLICK_SETTINGS['merchant_id']
        url = f"https://my.click.uz/services/pay?service_id={service_id}&merchant_id={merchant_id}&amount={amount}&transaction_param={order_id}"
        if return_url:
            url += f"&return_url={return_url}"
        return url
