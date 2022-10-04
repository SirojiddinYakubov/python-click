from rest_framework.views import APIView, Response
from rest_framework.permissions import AllowAny

from pyclick.authorization import authorization
from pyclick.models import ClickTransaction
from pyclick.serializers import PyClickSerializer
from pyclick.status import *


class PyClickMerchantAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    VALIDATE_CLASS = None

    def post(self, request):
        serializer = PyClickSerializer(data=request.data)
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
            result = METHODS[action](**serializer.validated_data, response_data=serializer.validated_data)
            return Response(result)
        return Response({"error": check_order})

    @classmethod
    def prepare(cls, click_trans_id: str,
                merchant_trans_id: str,
                amount: str,
                sign_string: str,
                sign_time: str,
                response_data: dict,
                *args, **kwargs) -> dict:
        """
        :param click_trans_id:
        :param merchant_trans_id:
        :param amount:
        :param sign_string:
        :param sign_time:
        :param response_data:
        :param args:
        :return:
        """
        transaction = ClickTransaction.objects.create(
            click_trans_id=click_trans_id,
            merchant_trans_id=merchant_trans_id,
            amount=amount,
            action=PREPARE,
            sign_string=sign_string,
            sign_datetime=sign_time,
        )
        response_data.update(merchant_prepare_id=transaction.id)
        return response_data

    @classmethod
    def complete(cls, click_trans_id: str,
                 amount: str,
                 error: str,
                 merchant_prepare_id: str,
                 response_data: dict,
                 action: str,
                 *args, **kwargs):
        """
        :param click_trans_id:
        :param amount:
        :param error:
        :param merchant_prepare_id:
        :param response_data:
        :param action:
        :param args:
        :return:
        """
        try:
            transaction = ClickTransaction.objects.get(pk=merchant_prepare_id)

            if error == A_LACK_OF_MONEY:
                response_data.update(error=A_LACK_OF_MONEY_CODE)
                transaction.action = A_LACK_OF_MONEY
                transaction.status = ClickTransaction.CANCELED
                transaction.save()
                return response_data

            if transaction.action == A_LACK_OF_MONEY:
                response_data.update(error=A_LACK_OF_MONEY_CODE)
                return response_data

            if transaction.amount != amount:
                response_data.update(error=INVALID_AMOUNT)
                return response_data

            if transaction.action == action:
                response_data.update(error=INVALID_ACTION)
                return response_data

            transaction.action = action
            transaction.status = ClickTransaction.FINISHED
            transaction.save()
            response_data.update(merchant_confirm_id=transaction.id)
            cls.VALIDATE_CLASS().successfully_payment(transaction.merchant_trans_id, transaction)
            return response_data
        except ClickTransaction.DoesNotExist:
            response_data.update(error=TRANSACTION_NOT_FOUND)
            return response_data
