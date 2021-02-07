from user.models import Guest

from PIL import Image
from io import BytesIO

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
