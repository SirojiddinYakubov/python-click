from django.db import models

from django.utils.translation import gettext_lazy as _


class ClickTransaction(models.Model):
    """
    Класс ClickTransaction
    Этот объект модели создается автоматически во время совершения платежа

    Подробнее здесь: https://docs.click.uz/click-api-request/
    """
    PROCESSING = 'processing'
    FINISHED = 'finished'
    CANCELED = 'canceled'
    STATUS = (
        (PROCESSING, PROCESSING),
        (FINISHED, FINISHED),
        (CANCELED, CANCELED)
    )
    click_trans_id = models.CharField(verbose_name=_('Транзакция ID'), max_length=255)
    merchant_trans_id = models.CharField(verbose_name=_('Merchant транзакция ID'), max_length=255)
    amount = models.CharField(verbose_name=_('Сумма оплаты (в сумах)'), max_length=255)
    action = models.CharField(verbose_name=_("Выполняемое действие"), max_length=255)
    sign_string = models.CharField(
        verbose_name=_("Проверочная строка, подтверждающая подлинность отправляемого запроса."), max_length=255)
    sign_datetime = models.DateTimeField(verbose_name=_("Дата платежа"), max_length=255)
    status = models.CharField(max_length=25, choices=STATUS, default=PROCESSING, verbose_name=_("Статус"))

    def __str__(self):
        return self.click_trans_id
