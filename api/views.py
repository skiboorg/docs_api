# coding utf-8

import json
import retailcrm
import ftputil
from django.template import loader, Context
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from .serializers import *
from .models import *
from user.models import Guest
from .services import *
from datetime import datetime
from pycdek3 import Client


import settings


class GetDelivery(generics.ListAPIView):
    serializer_class = DeliverySerializer
    queryset = DeliveryType.objects.all()


class GetBanners(generics.ListAPIView):
    serializer_class = BannerSerializer
    queryset = Banner.objects.all()


class GetCategories(generics.ListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()


class GetSubcategoryItems(generics.ListAPIView):
    serializer_class = ItemSerializer
    def get_queryset(self):
        return Item.objects.filter(subcategory__name_slug=self.request.query_params['subcategory_name_slug'],
                                   collection__isnull=True)

class GetCollections(generics.ListAPIView):
    serializer_class = CollectionSerializer
    def get_queryset(self):
        return Collection.objects.filter(subcategory__name_slug=self.request.query_params['subcategory_name_slug'])


class GetHomeCollections(generics.ListAPIView):
    serializer_class = CollectionSerializer
    def get_queryset(self):
        return Collection.objects.filter(is_show_at_home=True)


class GetItem(generics.RetrieveAPIView):
    serializer_class = ItemSerializer

    def get_object(self):
        base_item_slug = self.request.query_params['base_item_slug']
        item = Item.objects.get(name_slug=base_item_slug)
        return item

class GetItem_old(APIView):
    def get(self,request):
        colors = []
        base_item_slug = self.request.query_params['base_item_slug']

        item = Item.objects.get(name_slug=base_item_slug)
        types = ItemType.objects.filter(item=item)

        for type in types:
            color_for_add = {
                "color_id": type.color.id,
                "color_hex": type.color.bg_color,
                "color_name": type.color.name
            }
            if not color_for_add in colors:
                colors.append(color_for_add)

        for color in colors:
            color["sizes"] = []
            color["images"] = []

        for type in types:
            for color in colors:
                if color["color_id"] == type.color.id:
                    size_to_add = {
                        "size_id": type.size.id,
                        "size_name": type.size.name,
                        "heights": []
                    }
                    if not size_to_add in color["sizes"]:
                        color["sizes"].append(size_to_add)
        for type in types:
            for color in colors:
                for size in color['sizes']:
                    if color['color_id'] == type.color.id and size['size_id'] == type.size.id:
                        height_to_add = {
                            "height_id": type.height.id,
                            "height_name": type.height.name,
                        }
                        if not height_to_add in size['heights']:
                            size['heights'].append(height_to_add)

        for color in colors:
            images = ItemImage.objects.filter(item=type.item, color_id=color['color_id'])
            for image in images:
                image_to_add = {
                    "image_id": image.id,
                    "image": image.image.url,
                    "image_thumb": image.image_thumb.url,
                }
                color['images'].append(image_to_add)
        result = {
            "item_data":ItemSerializer(item).data,
            "colors_data": colors
        }

        return Response(result,status=200)


class GetCart(APIView):
    def get(self,request):
        cart = check_if_cart_exists(request, self.request.query_params.get('session_id'))
        print(cart)
        serializer = CartSerializer(cart)
        return Response(serializer.data,status=200)

class CreateOrder(APIView):
    def post(self, request):
        data = request.data
        session_id = data.get('session_id')
        order_data = data.get('order')
        cart = check_if_cart_exists(request, session_id)


        new_order = Order.objects.create(
            payment=order_data.get('pay_type'),
            phone=order_data.get('phone'),
            email=order_data.get('email'),
            fio=order_data.get('fio'),
            street=order_data.get('street'),
            house=order_data.get('house'),
            flat=order_data.get('flat'),
            delivery_id=order_data.get('delivery_type') if order_data.get('delivery_type') > 0 else None,
            city_id=order_data.get('delivery_city') if order_data.get('delivery_city') else None,
            comment=order_data.get('comment'),
            promo_code=cart.promo_code,
            weight=cart.weight,
            total_price=cart.total_price
        )
        if cart.client:
            new_order.client = cart.client
        else:
            new_order.guest = cart.guest

        new_order.save()
        items=[]
        for item in cart.items.all():
            new_order_item = OrderItem.objects.create(item_type=item.item_type,quantity=item.quantity)
            new_order.items.add(new_order_item)
            # item.delete()
            items.append({
                'productName': item.item_type.item.name,
                'initialPrice': item.item_type.item.price,
                'quantity': item.quantity,
                'offer': {
                    'xmlId': f'{item.item_type.item.id_1c.split("#")[0]}#{item.item_type.id_1c}',
                    # 'id': item.item_type.id
                }
            })
        cart.promo_code = None
        cart.save()

        client = retailcrm.v5(f'https://{settings.CRM_URL}.retailcrm.ru', settings.CRM_API)
        order = {
            'firstName': new_order.fio,
            'lastName': '',
            'phone': new_order.phone,
            'email': new_order.email,
            'items': items,
            'customerComment': new_order.comment,
            'orderMethod': 'call-request',
        }
        print(order)
        result = client.order_create(order)
        return Response({'order_code': True}, status=200)


class ApplyPromo(APIView):
    def post(self, request):
        data = request.data
        try:
            promo = PromoCode.objects.get(code=data.get('code'))
            cart = check_if_cart_exists(request, data.get('session_id'))
            cart.promo_code = promo
            cart.save()
            return Response({'status': True}, status=200)
        except:

            return Response({'status':False}, status=200)

class MinusQuantity(APIView):
    def post(self, request):
        data = request.data
        item = CartItem.objects.get(id=data.get('item_id'))
        if item.quantity > 1:
            item.quantity -= 1
            item.save()
        else:
            item.delete()
        return Response(status=200)

class PlusQuantity(APIView):
    def post(self, request):
        data = request.data
        item = CartItem.objects.get(id=data.get('item_id'))
        item.quantity += 1
        item.save()
        return Response(status=200)

class DeleteItem(APIView):
    def post(self, request):
        data = request.data
        item = CartItem.objects.get(id=data.get('item_id'))
        item.delete()
        return Response(status=200)


class AddToCart(APIView):
    def post(self, request):
        data = request.data
        print(request.data)
        user = None
        guest = None
        cart = None
        adding_item_type = ItemType.objects.get(id=data.get('item_id'))
        cart = check_if_cart_exists(request, data.get('session_id'))
        add_item_to_cart(cart, adding_item_type)
        return Response(status=200)


def catalog_feed(request,):
    template_vars = {}
    template_vars['categories'] = Category.objects.all()
    template_vars['item_types'] = ItemType.objects.all()
    template_vars['base_url'] = settings.BASE_URL
    template_vars['created'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')


    t = loader.get_template('catalog.xml')
    c = template_vars
    return HttpResponse(t.render(c),content_type='text/xml')

class CheckOstatok(APIView):
    def get(self, request):
        from lxml import etree
        with ftputil.FTPHost('185.92.148.221', settings.FTP_USER, settings.FTP_PASSWORD) as host:
            names = host.listdir(host.curdir)
            for name in names:
                if host.path.isfile(name):
                    host.download(name, name)
        tree = etree.parse('VigruzkaOstatok.xml')
        root = tree.getroot()
        for element in root:
            item_id = element.find("item_id").text
            quantity = element.find("goods").text
            try:
                item = ItemType.objects.get(id_1c=item_id)
                item.quantity = quantity
                item.save()
            except ItemType.DoesNotExist:
                pass
            return Response(status=200)

class CheckFtp(APIView):

    def get(self, request):
        from lxml import etree
        with ftputil.FTPHost('185.92.148.221', settings.FTP_USER, settings.FTP_PASSWORD) as host:
            names = host.listdir(host.curdir)
            for name in names:
                if host.path.isfile(name):
                    host.download(name, name)
        tree = etree.parse('tovar.xml')
        root = tree.getroot()
        for element in root:
            item_id = element.find("basic_item").text
            item_name = element.find("name").text
            item_price = element.find("price").text
            item, created = Item.objects.get_or_create(id_1c=item_id)
            item.name = item_name
            item.price = item_price
            item.save()
        tree = etree.parse('vigruzka.xml')
        root = tree.getroot()

        # for element in root:
        #     basic_item_id = element.find("basic_item").text
        #     base_item, created = Item.objects.get_or_create(id_1c=basic_item_id)
        #
        #     color_id = element.find("color").text
        #     color, created = ItemColor.objects.get_or_create(id_1c=color_id)
        #     if created:
        #         color.name = 'Новый цвет'
        #         color.save()
        #
        #     size_name = element.find("size").text
        #     size, created = ItemSize.objects.get_or_create(name=size_name)
        #     if created:
        #         size.name = size_name
        #         size.save()
        #
        #     height_name = element.find("height").text
        #     height, created = ItemHeight.objects.get_or_create(name=height_name)
        #     if created:
        #         height.name = height_name
        #         height.save()
        #
        #     add_name = element.find("add").text
        #     if add_name == '0':
        #         add_name = 'Нет модификации'
        #     mod, created = ItemModification.objects.get_or_create(name=add_name)
        #     if created:
        #         if add_name == '0':
        #             add_name = 'Нет модификации'
        #         mod.name = add_name
        #         mod.save()
        #
        #     cloth_name = element.find("cloth").text
        #     material, created = ItemMaterial.objects.get_or_create(name=cloth_name)
        #     if created:
        #         material.name = cloth_name
        #         material.save()
        #
        #     item_id = element.find("item_id").text
        #     item_type, created = ItemType.objects.get_or_create(id_1c=item_id)
        #     if created:
        #         item_type.item = base_item
        #         item_type.color = color
        #         item_type.size = size
        #         item_type.height = height
        #         item_type.material = material
        #         item_type.modification = mod
        #         item_type.save()

        return Response(status=200)


class CalculateDelivery(APIView):
    def get(self,request):
        # MOSCOW_ID = 44
        # SP_ID = 137
        #
        # tariffs = [119]
        #
        # print(Client.get_shipping_cost(MOSCOW_ID, SP_ID, tariffs,
        #                                goods=[{'weight': 3000, 'length': 50, 'width': 10, 'height': 20}]))



        return Response(status=200)