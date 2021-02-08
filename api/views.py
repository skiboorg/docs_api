import json
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