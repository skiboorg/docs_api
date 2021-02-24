from user.models import Guest

from PIL import Image
from io import BytesIO
from yookassa import Configuration, Payment
from rest_framework.response import Response
import uuid
import settings


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
    if order.city:
        delivery_price = order.city.price
    else:
        delivery_price = 0
    print('delivery_price', delivery_price)
    order_total_price = order.total_price
    amount = order_total_price + delivery_price

    # payment_type = request.data.get('pay_type')

    Configuration.account_id = settings.YA_SHOP_ID
    Configuration.secret_key = settings.YA_API
    pay_id = uuid.uuid4()
    payment = Payment.create({
        "amount": {
            "value": amount,
            "currency": "RUB"
        },
        # "payment_method": {
        #     "type": payment_type,
        # },
        "confirmation": {
            "type": "redirect",
            "return_url": f'{settings.HOST}/lk/balance?pay_id={pay_id}'
        },
        "capture": True,
        "description": f'Оплата заказа ID {order.id}'
    }, pay_id)

    print(payment)


    new_payment = PaymentObj.objects.create(pay_id=payment.id,
                              pay_code=pay_id,
                              amount=amount,
                              status='Не оплачен')

    if order.client:
        new_payment.client = order.client
    else:
        new_payment.guest = order.guest
    new_payment.save()
    return Response(payment.confirmation.confirmation_url)
