from rest_framework import serializers
from .models import *


class CdekOfficeSerializer(serializers.ModelSerializer):
    city_code = serializers.SerializerMethodField()
    class Meta:
        model = CdekOffice
        fields = '__all__'
    def get_city_code(self, obj):
        return obj.city.code


class CitySerializer(serializers.ModelSerializer):
    offices = CdekOfficeSerializer(many=True, read_only=True, required=False)
    class Meta:
        model = City
        fields = '__all__'


class DeliverySerializer(serializers.ModelSerializer):
    cities = CitySerializer(many=True, read_only=True, required=False)

    class Meta:
        model = DeliveryType
        fields = '__all__'


class ItemColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemColor
        fields = '__all__'


class ItemSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemSize
        fields = '__all__'


class ItemHeightSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemHeight
        fields = '__all__'


class ItemMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemMaterial
        fields = '__all__'


class ItemModificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemModification
        fields = '__all__'


class ItemImageSerializer(serializers.ModelSerializer):
    color = ItemColorSerializer(many=False, read_only=True, required=False)
    class Meta:
        model = ItemImage
        fields = '__all__'


class ItemTypeSiteMapSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    class Meta:
        model = ItemType
        fields = ['url']

    def get_url(self,obj):
        if obj.get_path():
            return obj.get_path()


class ItemTypeSerializer(serializers.ModelSerializer):
    # item = ItemSerializer(many=False, read_only=True, required=False)
    color = ItemColorSerializer(many=False, read_only=True, required=False)
    size = ItemSizeSerializer(many=False, read_only=True, required=False)
    height = ItemHeightSerializer(many=False, read_only=True, required=False)
    material = ItemMaterialSerializer(many=False, read_only=True, required=False)
    modification = ItemModificationSerializer(many=False, read_only=True, required=False)
    image = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    article = serializers.SerializerMethodField()
    class Meta:
        model = ItemType
        fields = '__all__'

    def get_image(self, obj):
        return obj.item.images.first().image_thumb.url

    def get_name(self, obj):
        return obj.item.name

    def get_article(self, obj):
        return obj.item.article

class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = '__all__'


class ItemSerializer(serializers.ModelSerializer):
    images = ItemImageSerializer(many=True, read_only=True, required=False)
    types = ItemTypeSerializer(many=True, read_only=True, required=False)
    subcategory = SubCategorySerializer(many=False, read_only=True, required=False)
    category = serializers.SerializerMethodField()
    class Meta:
        model = Item
        fields = '__all__'

    def get_category(self, obj):
        return obj.subcategory.category.name_slug


class RecItemSerializer(serializers.ModelSerializer):
    images = ItemImageSerializer(many=True, read_only=True, required=False)
    types = ItemTypeSerializer(many=True, read_only=True, required=False)
    subcategory = SubCategorySerializer(many=False, read_only=True, required=False)

    class Meta:
        model = Item
        fields = '__all__'






class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = '__all__'




class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubCategorySerializer(many=True, read_only=True, required=False)
    class Meta:
        model = Category
        fields = '__all__'

class CollectionItemSerializer(serializers.ModelSerializer):
    images = ItemImageSerializer(many=True, read_only=True, required=False)
    subcategory = SubCategorySerializer(many=False, read_only=True, required=False)
    category = serializers.SerializerMethodField()
    class Meta:
        model = Item
        fields = '__all__'

    def get_category(self, obj):
        return obj.subcategory.category.name_slug



class CollectionWithItemsSerializer(serializers.ModelSerializer):
    collection_items = CollectionItemSerializer(many=True, read_only=True, required=False)

    class Meta:
        model = Collection
        fields = '__all__'


class CollectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Collection
        fields = '__all__'




class SimpleItemSerializer(serializers.ModelSerializer):
    images = ItemImageSerializer(many=True, read_only=True, required=False)
    image = serializers.SerializerMethodField()
    subcategory = SubCategorySerializer(many=False, read_only=True, required=False)
    collection = CollectionSerializer(many=False, read_only=True, required=False)

    class Meta:
        model = Item
        fields = '__all__'
    def get_image(self,obj):
        try:
            img = self.context['request'].build_absolute_uri(obj.images.get(is_preview=True).image_thumb.url)
        except:
            img = self.context['request'].build_absolute_uri(obj.images.first().image_thumb.url)


        return img

class PromoSerializer(serializers.ModelSerializer):

    class Meta:
        model = PromoCode
        fields = '__all__'


class CartItemSerializer(serializers.ModelSerializer):
    item_type = ItemTypeSerializer(many=False, read_only=True, required=False)

    class Meta:
        model = CartItem
        fields = '__all__'



class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True, required=False)
    total_price = serializers.SerializerMethodField()
    promo_code = PromoSerializer(many=False, read_only=True, required=False)
    weight = serializers.SerializerMethodField()
    class Meta:
        model = Cart
        fields = '__all__'

    def get_weight(self, obj):
        items = obj.items.all()
        weight = 0
        for i in items:
            weight += i.item_type.item.subcategory.weight * i.quantity
        obj.weight = weight
        obj.save()
        return weight

    def get_total_price(self, obj):
        items = obj.items.all()
        total_price = 0

        for i in items:
            total_price += i.price

        obj.raw_price = total_price
        obj.total_price = total_price

        if obj.promo_code:
            if obj.promo_code.summ:
                total_price -= obj.promo_code.summ

            if obj.promo_code.discount:
                total_price = int(total_price - (total_price * obj.promo_code.discount / 100))

        obj.total_price = total_price

        obj.save()
        return total_price

class OrderItemSerializer(serializers.ModelSerializer):
    item_type = ItemTypeSerializer(many=False, required=False, read_only=True)
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, required=False, read_only=True)
    city = CitySerializer(many=False, required=False, read_only=True)
    delivery = DeliverySerializer(many=False, read_only=True, required=False)
    class Meta:
        model = Order
        fields = '__all__'

