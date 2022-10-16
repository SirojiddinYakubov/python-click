![banner](https://i.postimg.cc/brrfqW8k/banner.jpg "banner")

[![Downloads](https://img.shields.io/pypi/v/python-click)](https://pypi.org/project/python-click/)
[![Downloads](https://black.readthedocs.io/en/stable/_static/license.svg)](https://github.com/yakubov9791999/python-click/blob/master/LICENSE)
[![Downloads](https://img.shields.io/badge/docs-github-green)](https://github.com/yakubov9791999/python-click)
[![Downloads](https://img.shields.io/badge/telegram-yakubovdeveloper-green)](https://t.me/yakubovdeveloper)
[![Downloads](https://img.shields.io/badge/author-Sirojiddin_Yakubov-green)](https://t.me/Sirojiddin_Yakubov)
<div align="center">
<h1>Интеграция сервиса онлайн оплаты CLICK SHOP API и Merchant API через фреймворк Django в Python</h1>
</div>

С помощью пакет `python-click` вы сможете очень легко интегрировать платежную систему CLICK. В этом руководстве показано, как интегрировать систему оплаты CLICK SHOP API и Merchant API. Через этот пакет вы сможете получать платежи за различные товары, услуги и покупки в Интернет Магазине. Более подробная информация об интеграции находится на официальной документации [OOO "Click"](https://docs.click.uz/)

## Необходимые пакеты
[Django](https://docs.djangoproject.com/) - свободный фреймворк для веб-приложений на языке Python, использующий шаблон проектирования MVC.

[Django REST framework](https://www.django-rest-framework.org/) - это мощный и гибкий инструментарий для создания веб-приложений.

[Requests](https://requests.readthedocs.io/) - это элегантная и простая HTTP-библиотека для Python, созданная для людей.

## Установка
Установите с помощью pip, включая любые дополнительные пакеты, которые вы хотите...
```bash
pip install python-click
```
...или клонируйте проект с github
```console
git clone https://github.com/yakubov9791999/python-click.git
```

Поместите это в `settings.py`
```console
INSTALLED_APPS = [
    ...
    'pyclick',
    'rest_framework',
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

Добавьте следующее в свой корневой каталог `urls.py` файл.
```console
from django.urls import include

urlpatterns = [
    ...
    path('pyclick/', include('pyclick.urls')),
]
```
Выполните команды `makemigrations` и `migrate`
```console
python manage.py makemigrations
python manage.py migrate
```

## Настройка биллинг
Введите `Prepare URL (Адрес проверки)` и `Complete URL (Адрес результата)` на сайт merchant.click.uz, чтобы система CLICK проверил ваш заказ.

Prepare URL
```
https://example.com/pyclick/process/click/transaction/?format=json
```
Complete URL
```
https://example.com/pyclick/process/click/transaction/?format=json
```
<br>
<img src="https://i.postimg.cc/KYymdYsH/merchant-click.png" width="70%">
<br>
<br>
<img src="https://i.postimg.cc/Vk5cpCRg/merchant-click-2.png" width="70%">

## Создать заказ

Вы можете создать заказ через [администратора django](http://127.0.0.1:8000/admin/) или по этой ссылке http://127.0.0.1:8000/pyclick/process/click/transaction/create/
<br>
<img src="https://i.postimg.cc/pXkY69Gs/django-admin-click-transaction.png" width="70%">
<br>
<br>
<img src="https://i.postimg.cc/02zbPLWp/create-click-transaction.png" width="70%">


Поместите желаемую сумму в поле `amount` и создайте заказ.

## CLICK SHOP API

Обратите внимание, что после создания заказа по этой ссылке http://127.0.0.1:8000/pyclick/process/click/transaction/create/ мы перейдем на сайт http://my.click.uz. 
<br>
<br>
<img src="https://i.ibb.co/1XYKhzB/my-click.png" width="70%">

Вы можете оплатить, введя номер карты или номер телефона. 

Полная информация, локальное тестирование, реальная интеграция с системой CLICK SHOP API, настройка личного кабинета и для проверки заказа через систему [Merchant CLICK](https://merchant.click.uz/) вы можете найти по этой ссылке https://pypi.org/project/python-click/0.1/ или в этом видео

[![Watch the video](https://img.youtube.com/vi/HHQ9QKSObyI/maxresdefault.jpg)](https://youtu.be/HHQ9QKSObyI)


## CLICK Merchant API

### Создать инвойс (счет-фактуру)
```
POST http://127.0.0.1:8000/pyclick/process/click/service/create_invoice
```
> Body:
> ```
> phone_number - Номер телефона
> ```
> ```
> transaction_id - ID заказа
> ```
---
### Проверка статуса инвойса (счет-фактуры)
```
POST http://127.0.0.1:8000/pyclick/process/click/service/check_invoice
```
> Body:
> ```
> invoice_id - ID инвойса
> ```
> ```
> transaction_id - ID заказа
> ```
---
### Создание токена карты
```
POST http://127.0.0.1:8000/pyclick/process/click/service/create_card_token
```
> Body:
> ```
> card_number - Номер карты
> ```
> ```
> expire_date - Срок карты
> ```
> ```
> temporary - создать токен для единичного использования. Временные токены автоматически удаляются после оплаты.
> ```
> ```
> transaction_id - ID заказа
> ```
---
### Подтверждение токена карты
```
POST http://127.0.0.1:8000/pyclick/process/click/service/verify_card_token
```
> Body:
> ```
> card_token - Токен карты
> ```
> ```
> sms_code - Полученный смс код
> ```
> ```
> transaction_id - ID заказа
> ```
---
### Оплата с помощью токена
```
POST http://127.0.0.1:8000/pyclick/process/click/service/payment_with_token
```
> Body:
> ```
> card_token - Токен карты
> ```
> ```
> transaction_id - ID заказа
> ```
---
### Удаление токена карты
```
POST http://127.0.0.1:8000/pyclick/process/click/service/delete_card_token
```
> Body:
> ```
> card_token - Токен карты
> ```
> ```
> transaction_id - ID заказа
> ```
---
### Снятие платежа (отмена)
```
POST http://127.0.0.1:8000/pyclick/process/click/service/cancel_payment
```
> Body:
> ```
> transaction_id - ID заказа
> ```
---
### Проверка статуса платежа
```
POST http://127.0.0.1:8000/pyclick/process/click/service/check_payment_status
```
> Body:
> ```
> transaction_id - ID заказа
> ```
---

Вы можете отправить эти запросы через [Postman](https://www.postman.com/). Загрузите [эту коллекцию](https://) и импортируйте ее в свой `postman`. В этой коллекции все запросы и обязательные поля написано.

[comment]: <> (Для более подробной информации, production интеграция с системой CLICK, настройка личного кабинета и для проверки заказа через систему [Merchant CLICK]&#40;https://merchant.click.uz/&#41;, вы можете посмотреть это видео)

[comment]: <> ([![Watch the video]&#40;https://img.youtube.com/vi/HHQ9QKSObyI/maxresdefault.jpg&#41;]&#40;https://youtu.be/HHQ9QKSObyI&#41;)

## Спасибо за внимание!

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