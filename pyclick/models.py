from django.db import models

from django.utils.translation import gettext_lazy as _


class ClickTransaction(models.Model):
    """ Класс ClickTransaction """
    PROCESSING = 'processing'
    WAITING = "waiting"
    CONFIRMED = 'confirmed'
    CANCELED = 'canceled'
    ERROR = 'error'

    STATUS = (
        (WAITING, WAITING),
        (PROCESSING, PROCESSING),
        (CONFIRMED, CONFIRMED),
        (CANCELED, CANCELED),
        (ERROR, ERROR)
    )
    click_paydoc_id = models.CharField(verbose_name=_('Номер платежа в системе CLICK'), max_length=255, blank=True)
    amount = models.DecimalField(verbose_name=_('Сумма оплаты (в сумах)'), max_digits=9, decimal_places=2,
                                 default="0.0")
    action = models.CharField(verbose_name=_("Выполняемое действие"), max_length=255, blank=True, null=True)
    status = models.CharField(verbose_name=_("Статус"), max_length=25, choices=STATUS, default=WAITING)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    extra_data = models.TextField(blank=True, default="")
    message = models.TextField(blank=True, default="")

    def __str__(self):
        return self.click_paydoc_id

    def change_status(self, status: str, message=""):
        """
        Обновляет статус платежа
        """
        self.status = status
        self.message = message
        self.save(update_fields=["status", "message"])
