![banner](https://i.postimg.cc/brrfqW8k/banner.jpg "banner")

[![Downloads](https://img.shields.io/pypi/v/python-click)](https://pypi.org/project/python-click/)
[![Downloads](https://black.readthedocs.io/en/stable/_static/license.svg)](https://github.com/yakubov9791999/python-click/blob/master/LICENSE)
[![Downloads](https://img.shields.io/badge/docs-github-green)](https://github.com/yakubov9791999/python-click)
[![Downloads](https://img.shields.io/badge/telegram-yakubovdeveloper-green)](https://t.me/yakubovdeveloper)
[![Downloads](https://img.shields.io/badge/author-Sirojiddin_Yakubov-green)](https://t.me/Sirojiddin_Yakubov)
<div align="center">
<h1>Интеграция сервиса онлайн оплаты CLICK SHOP API через фреймворк Django в Python</h1>
</div>

С помощью пакет `python-click` вы сможете очень легко интегрировать платежную систему CLICK SHOP API. Используйте версию `0.1` для интеграции CLICK SHOP API. В этом руководстве показано, как интегрировать систему оплаты CLICK SHOP API. Через этот «CLICK SHOP API» вы сможете получать платежи за различные товары, услуги и покупки в Интернет Магазине. Более подробная информация об интеграции находится на официальной документации [OOO "Click"](https://docs.click.uz/click-api/)

## Необходимые пакеты
[Django](https://docs.djangoproject.com/) - свободный фреймворк для веб-приложений на языке Python, использующий шаблон проектирования MVC.

[Django REST framework](https://www.django-rest-framework.org/) - это мощный и гибкий инструментарий для создания веб-приложений.

## Установка
Установите с помощью pip, включая любые дополнительные пакеты, которые вы хотите...
```bash
pip install python-click==0.1
```
...или клонируйте проект с github
```console
git clone https://github.com/yakubov9791999/python-click.git
```
Создадим новое приложение с названием `basic`
```console
python manage.py startapp basic
```
> Имя приложении не обязательно должно быть `basic`. Вы можете использовать любое имя, которое хотите

Поместите это в `settings.py`
```console
INSTALLED_APPS = [
    ...
    'pyclick',
    'rest_framework',
    'basic',
]

CLICK_SETTINGS = {
    'service_id': "<Ваш сервис ID>",
    'merchant_id': "<Ваш merchant ID>",
    'secret_key': "<Ваш секретный ключ>",
    'merchant_user_id': "<Ваш merchant user ID>",
}
```
> _**Примечание:**_
> Эти информации будет предоставлена ​​вам после того, как вы подписали контракт с OOO «Click»

В приложении `basic` в `models.py` создайте новую модель `ClickOrder`, с помощью этой модели мы можем создать заказ
```console
from django.db import models

class ClickOrder(models.Model):
    is_paid = models.BooleanField(default=False)
    amount = models.DecimalField(decimal_places=2, max_digits=12)
```
В приложении `basic` создайте `serializers.py`, потом поместите эти коды
```console
from rest_framework import serializers
from .models import ClickOrder

class ClickOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClickOrder
        fields = ["amount", "is_paid"]
```
В приложении `basic` в `views.py` создайте новый класс `CreateClickOrderView`,`OrderCheckAndPayment` и `OrderTestView`. C помощью `CreateClickOrderView` класса мы создадим заказ, после этого система Click проверяет наш заказ с помощью классы `OrderCheckAndPayment` и `OrderTestView`. Чтобы получить больше информации, переходите по этой ссылке [Документация Click](https://docs.click.uz/). 
```console
from django.shortcuts import redirect
from rest_framework.generics import CreateAPIView
from basic import serializers
from basic.models import ClickOrder
from pyclick import PyClick
from pyclick.views import PyClickMerchantAPIView


class CreateClickOrderView(CreateAPIView):
    serializer_class = serializers.ClickOrderSerializer

    def post(self, request, *args, **kwargs):
        amount = request.POST.get('amount')
        order = ClickOrder.objects.create(amount=amount)
        return_url = 'http://127.0.0.1:8000/'
        url = PyClick.generate_url(order_id=order.id, amount=str(amount), return_url=return_url)
        return redirect(url)


class OrderCheckAndPayment(PyClick):
    def check_order(self, order_id: str, amount: str):
        if order_id:
            try:
                order = ClickOrder.objects.get(id=order_id)
                if int(amount) == order.amount:
                    return self.ORDER_FOUND
                else:
                    return self.INVALID_AMOUNT
            except ClickOrder.DoesNotExist:
                return self.ORDER_NOT_FOUND

    def successfully_payment(self, order_id: str, transaction: object):
        """ Эта функция вызывается после успешной оплаты """
        try:
            order = ClickOrder.objects.get(id=order_id)
            order.is_paid = True
            order.save()
        except ClickOrder.DoesNotExist:
            print(f"no order object not found: {order_id}")


class OrderTestView(PyClickMerchantAPIView):
    VALIDATE_CLASS = OrderCheckAndPayment
```
Добавьте следующее в свой корневой каталог `urls.py` файл.
```console
from django.urls import include

urlpatterns = [
    ...
    path('', include('basic.urls')),
]
```
В приложении `basic` создайте `urls.py`, потом поместите эти коды
```console
from django.urls import path
from basic import views

urlpatterns = [
    path('', views.CreateClickOrderView.as_view()),
    path('click/transaction/', views.OrderTestView.as_view()),
]
```
Выполните команды `makemigrations` и `migrate`
```console
python manage.py makemigrations
python manage.py migrate
```
Теперь вы можете создать заказ в своем браузере по адресу http://127.0.0.1:8000/ . Получим сумму заказа 500 сумов.
> _**Предупреждение:**_
> Если вы создадите сумму по-другому, произойдет ошибка при локальном тестировании через [тестовое программное обеспечение](https://docs.click.uz/wp-content/uploads/2018/05/NEW-CLICK_API.zip).

<img src="https://i.ibb.co/k6Pw0wm/2022-10-04-17-50.png" width="70%">

Обратите внимание, что после создания заказа мы перейдем на сайт http://my.click.uz
<br>
<br>
<img src="https://i.ibb.co/1XYKhzB/my-click.png" width="70%">

Но нам нужно сначала проверить заказ локально для этого мы можем использовать данное [программное обеспечение](https://docs.click.uz/wp-content/uploads/2018/05/NEW-CLICK_API.zip). Мы просто получаем номер заказа и закрываем вкладку, начинаем проверку локально через программное обеспечение.
> _**Предупреждение:**_
> Если вы используете базу данных [SQLite](https://www.sqlite.org/), вы можете получить ошибку `OverflowError`, поэтому мы рекомендуем использовать другую базу данных. Например: [MySQL](https://www.mysql.com/) или [PostgreSQL](https://www.postgresql.org/)

<br>
<img src="https://i.ibb.co/pPQ8Tcd/jC6EN5D.png" width="70%">

Введите в `Prepare URL` и `Complete URL` http://localhost:8000/click/transaction/?format=json. Заполните `service_id`, `merchant_user_id`, `secret_key` информацией, предоставленной "CLICK", в `merchant_trans_id` введите номер заказа. После этого начинайте проверить заказа. 

Это программное обеспечение проверяет заказ с помощью нескольких запросов. Всего существует 15 сценариев. В каждом сценарии отправляется разная информация, и заказ проверяется. Подробнее [здесь](https://docs.click.uz/click-api-request/)

> _**Примечание:**_
> После сценариев 7 и 11 программа останавливается. Выберите следующий сценарий и продолжите тестирование

Если у вас успешно прошли 15 сценариев, то ваши коды готовы к интеграции с платежной системой CLICK.

Для более подробной информации, production интеграция с системой CLICK, настройка личного кабинета и для проверки заказа через систему [Merchant CLICK](https://merchant.click.uz/), вы можете посмотреть это видео

[![Watch the video](https://img.youtube.com/vi/HHQ9QKSObyI/maxresdefault.jpg)](https://youtu.be/HHQ9QKSObyI)

<h3>Спасибо за внимание!</h3>

## Автор
[Sirojiddin Yakubov](https://t.me/Sirojiddin_Yakubov)

## Социальные сети
<div align="center">
  Подпишитесь на нас, чтобы получать больше новостей о веб-программировании: <br>
  <a href="https://www.youtube.com/channel/UCeJ6Sc3SaKKArAurnCwlJBw">YouTube</a>
  <span> | </span>
  <a href="https://www.instagram.com/yakubovdeveloper">Instagram</a>
  <span> | </span>
  <a href="https://www.facebook.com/yakubovdeveloper">Facebook</a>
  <span> | </span>
  <a href="https://www.tiktok.com/@yakubovdeveloper">TikTok</a>
  <span> | </span>
  <a href="https://t.me/yakubovdeveloper">Telegram</a>
</div>