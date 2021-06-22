# coding utf-8


import json
from user.models import Guest
import datetime as dt
from datetime import datetime
from django.utils import timezone
import requests
from PIL import Image
from io import BytesIO
from yookassa import Configuration, Payment
from rest_framework.response import Response
import retailcrm
import uuid
import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

def check_if_guest_exists(session_id):
    guest, created = Guest.objects.get_or_create(session=session_id)
    if created:
        print('guest created')
    else:
        print('guest already created')
    return guest


def check_if_cart_exists(request, session_id):
    from .models import Cart
    user = None
    guest = None
    if request.user.is_authenticated:
        user = request.user
    else:
        guest = check_if_guest_exists(session_id)

    if user:
        cart, created = Cart.objects.get_or_create(client=user)
    else:
        # cart = Cart.objects.get(guest=guest)
        cart, created = Cart.objects.get_or_create(guest=guest)

    if created:
        print('new cart created')
    else:
        print('cart already created')
    return cart

def add_item_to_cart(cart,item):
    from .models import CartItem
    user = cart.client
    guest = cart.guest
    print(user,guest)
    print(item)
    if user:
        cart_item, created = CartItem.objects.get_or_create(client=user, item_type=item)
    else:
        cart_item, created = CartItem.objects.get_or_create(guest=guest, item_type=item)
        print('creating item ')
    if created:
        print('new item created')
        cart.items.add(cart_item)
    else:
        print('item already created')
        print(cart_item)
        cart_item.quantity += 1
        cart_item.save()
    print(cart.items.all())

def image_resize_and_watermark(image,watermarked,new_w,new_h):
    """Ресайз картинки и добавление ватермарки"""
    fill_color = '#fff'
    base_image = Image.open(image)
    blob = BytesIO()
    if base_image.mode in ('RGBA', 'LA'):
        background = Image.new(base_image.mode[:-1], base_image.size, fill_color)
        background.paste(base_image, base_image.split()[-1])
        base_image = background

    width, height = base_image.size
    transparent = Image.new('RGB', (width, height), (0, 0, 0, 0))
    transparent.paste(base_image, (0, 0))
    transparent.thumbnail((new_w, new_h), Image.ANTIALIAS)
    if watermarked:
        watermark = Image.open('static/img/wm.png')
        transparent.paste(watermark, (50, 50), mask=watermark)
    # transparent.show()
    transparent.save(blob, 'png', quality=100, optimize=True)
    return blob


def pay_request(order):
    from .models import PaymentObj
    delivery_price = order.delivery_price
    is_need_pack = order.is_need_pack
    print('delivery_price', delivery_price)
    order_total_price = order.total_price

    pack_price = 0
    if is_need_pack:
        pack_price = 300
    amount = order_total_price + delivery_price
    print('amount', amount)
    # payment_type = request.data.get('pay_type')

    Configuration.account_id = settings.YA_SHOP_ID
    Configuration.secret_key = settings.YA_API
    pay_id = uuid.uuid4()
    items = []

    for item in order.items.all():

        if is_need_pack:
            items.append({
                "description": 'Упаковка',
                "quantity": 1,
                "amount": {
                    "value": pack_price,
                    "currency": "RUB"
                },
                "vat_code": "2",
                "payment_mode": "full_prepayment",
                "payment_subject": "commodity"
            })

        if delivery_price > 0:
            items.append({
                "description": 'Доставка',
                "quantity": 1,
                "amount": {
                    "value": delivery_price,
                    "currency": "RUB"
                },
                "vat_code": "2",
                "payment_mode": "full_prepayment",
                "payment_subject": "commodity"
            })

        items.append({
                    "description": item.item_type.item.name,
                    "quantity": item.quantity,
                    "amount": {
                        "value": item.price / item.quantity,
                        "currency": "RUB"
                    },
                    "vat_code": "2",
                    "payment_mode": "full_prepayment",
                    "payment_subject": "commodity"
                })

        # vat_code
        # 1        Без        НДС
        # 2        НДС        по        ставке        0 %
        # 3        НДС        по        ставке        10 %
        # 4        НДС        чека        по        ставке        20 %
        # 5        НДС        чека        по        расчетной        ставке        10 / 110
        # 6        НДС        чека        по        расчетной        ставке        20 / 120
    print(items)
    payment = Payment.create({
        "amount": {
            "value": amount,
            "currency": "RUB"
        },
        "receipt": {
            "customer": {
                "full_name": order.fio,
                "phone": order.phone
            },
            "items": items
        },
        # "payment_method": {
        #     "type": payment_type,
        # },
        "confirmation": {
            "type": "redirect",
            # "return_url": f'{settings.HOST}/payment_complete?pay_id={pay_id}'
            "return_url": f'{settings.HOST}'
        },
        "capture": True,
        "description": f'Оплата заказа ID {order.id}'
    }, pay_id)

    print(payment.id)
    ya_id = payment.id
    print(payment.confirmation.confirmation_url)



    new_payment = PaymentObj.objects.create(pay_id=pay_id,
                                            ya_id = ya_id,
                                            order=order,
                                            amount=amount,
                                            status='Не оплачен')

    if order.client:
        new_payment.client = order.client
    else:
        new_payment.guest = order.guest
    new_payment.save()
    return payment.confirmation.confirmation_url

def cdekGetToken():
    print('get token')
    data = {
        'grant_type': 'client_credentials',
        'client_id': settings.CDEK_CLIENT_ID,
        'client_secret': settings.CDEK_CLIENT_SECRET
    }
    response = requests.post('https://api.cdek.ru/v2/oauth/token?parameters', data=data)
    access_token = response.json().get('access_token')
    return access_token

def checkCdekToken():
    from .models import CdekKey
    access_token = ''

    try:
        key = CdekKey.objects.first()
        access_token = key.access_token
    except:
        access_token = cdekGetToken()
        CdekKey.objects.create(access_token=access_token)
        return access_token

    if timezone.now() - key.updated_at > dt.timedelta(hours=1):
        print('expired')
        access_token = cdekGetToken()
        key.access_token = access_token
        key.save()
    return access_token

def calculateDelivery(access_token,city_code,weight,cdek_type):
    print(cdek_type)
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {access_token}",
    }
    data = {
        "type": "2",
        # "date": "2020-11-03T11:49:32+0700",
        "currency": "1",
        "tariff_code": "11" if cdek_type == 'not_office' else "10",
        "from_location": {
            "code": "44"
        },
        "to_location": {
            "code": city_code
        },
        "packages": [
            {
                "weight": weight
            }
        ]
    }
    response = requests.post('https://api.cdek.ru/v2/calculator/tariff',
                             headers=headers,
                             data=json.dumps(data))
    print(response.json())
    return response.json().get('delivery_sum')


def send_order_to_crm(order):
    items = []
    print('sending to crm')
    for item in order.items.all():
        items.append({
            'productName': item.item_type.item.name,
            'initialPrice': item.item_type.item.price,
            'quantity': item.quantity,
            'offer': {
                'xmlId': f'{item.item_type.item.id_1c.split("#")[0]}#{item.item_type.id_1c}',
                # 'id': item.item_type.id
            }
        })



    if not order.delivery.is_self_delivery:
        delivery = {
            'code': 'sdek',
            'address':
                {
                    'city': order.city.name,
                    'cityId': order.city.code,
                    'street': order.street,
                    'building': order.house,
                    'flat': order.flat,
                }
        }
    else:
        delivery = {
            'code': 'self-delivery'
        }

    client = retailcrm.v5(f'https://{settings.CRM_URL}.retailcrm.ru', settings.CRM_API)

    order_info = {
        'payments': [
            {
                'type': 'site-u-kassa',
                'status': 'paid'
            }
        ],
        'firstName': order.fio,
        'lastName': '',
        'phone': order.phone,
        'email': order.email,
        'items': items,
        'customerComment': order.comment,
        # 'orderMethod': 'site',
        'source': {
            'source': 'site',
        },

        'delivery': delivery
    }

    print('order', order_info)
    result = client.order_create(order_info)
    print('result.get_errors()', result.get_errors())
    print('result.get_status_code()', result.get_status_code())
    print('result.get_response()', result.get_response())

    msg_html = render_to_string('new_order.html', {'order': order,
                                                   'items': order.items.all()})
    send_mail('Ваш заказ', None, 'noreply@docsuniform.ru', [order.email, 'info@docsuniform.ru'],
              fail_silently=False, html_message=msg_html)
    return
