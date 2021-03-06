from django.contrib import admin
from .models import *

class ImagesInline (admin.TabularInline):
    model = ItemImage
    readonly_fields = ('image_tag', )
    extra = 0

class ItemAdmin(admin.ModelAdmin):
    list_display = ['image_tag','collection_tag', 'name', 'article', 'price', 'is_active','is_in_feed','discount','order_num']
    inlines = [ImagesInline]
    list_filter = ('is_active', 'is_in_feed','collection',)
    search_fields = ('name_lower', 'article')
    class Meta:
        model = Item


class ItemTypeAdmin(admin.ModelAdmin):
    list_display = ['article_tag','name_tag','color_tag','size_tag',
                    'height_tag','material_tag','modification_tag','quantity_tag','is_active']
    list_filter = ('item','color','size')

    class Meta:
        model = ItemType


class CdekOfficeInline(admin.TabularInline):
    model = CdekOffice
    extra = 0


class CityAdmin(admin.ModelAdmin):
    inlines = [CdekOfficeInline]
    list_filter = ('type',)
    class Meta:
        model = City

class OrderItemInline (admin.TabularInline):
    model = Order.items.through
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at', 'total_price', 'email', 'phone', 'is_payed']
    list_filter = ('is_payed',)
    inlines = [OrderItemInline]
    class Meta:
        model = OrderItem

admin.site.register(Banner)
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Collection)
admin.site.register(ItemSize)
admin.site.register(ItemHeight)
admin.site.register(ItemColor)
admin.site.register(Item,ItemAdmin)
admin.site.register(ItemType,ItemTypeAdmin)
admin.site.register(ItemImage)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(ItemModification)
admin.site.register(ItemMaterial)
admin.site.register(City,CityAdmin)
admin.site.register(DeliveryType)
admin.site.register(PromoCode)
admin.site.register(Order,OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(CdekKey)
admin.site.register(CdekOffice)
admin.site.register(PaymentObj)
admin.site.register(MailSubscribe)

