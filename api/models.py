from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField
from django.db.models.signals import post_save, post_delete, pre_save
from pytils.translit import slugify
from random import choices
import string
from colorfield.fields import ColorField
from django.utils.safestring import mark_safe
from django.core.files import File
from .services import image_resize_and_watermark


class CdekKey(models.Model):
    access_token = models.TextField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)




class DeliveryType(models.Model):
    name = models.CharField('Название типа доставки', max_length=255, blank=False, null=True)
    time = models.CharField('Минимальное время доставки', max_length=255, blank=False, null=True)
    price = models.CharField('Минимальная стоимость доставки', max_length=255, blank=False, null=True)
    is_self_delivery = models.BooleanField('Это самовывоз?', default=False)
    is_office_cdek = models.BooleanField('Это СДЕК до офиса?', default=False)
    is_active = models.BooleanField('Отображать??', default=True)
    code = models.CharField('Код доставки для CRM', max_length=255, blank=False, null=True)

    def __str__(self):
        return f'Тип доставки : {self.name}'

    class Meta:
        ordering = ('-is_self_delivery',)
        verbose_name = "Тип доставки"
        verbose_name_plural = "7. Типы доставки"


class City(models.Model):
    type = models.ForeignKey(DeliveryType,
                             on_delete=models.CASCADE,
                             null=True,
                             blank=False,
                             verbose_name='Относится к',
                             related_name='cities')
    name = models.CharField('Название города', max_length=255, blank=False, null=True)
    name_lower = models.CharField('Название города', max_length=255, blank=False, null=True,editable=False)
    price = models.IntegerField('Стоимость доставки',blank=True,null=True,editable=False)
    code = models.IntegerField('Код города',blank=False,null=True)

    def __str__(self):
        return f'{self.type.name}  - {self.name} - код {self.code}'

    def save(self, *args, **kwargs):
        self.name_lower = self.name.lower()

        super(City, self).save(*args, **kwargs)

    class Meta:
        ordering = ('name', )
        verbose_name = "Город"
        verbose_name_plural = "7.1. Города"


class CdekOffice(models.Model):
    city = models.ForeignKey(City,
                             on_delete=models.CASCADE,
                             null=True,
                             blank=False,
                             verbose_name='Относится к',
                             related_name='offices')
    office_id = models.CharField('ID офиса', max_length=255, blank=True, null=True)
    address = models.CharField('Адрес офиса', max_length=255, blank=True, null=True)

    def __str__(self):
        return f'{self.office_id} - {self.city.name}'

    class Meta:
        #ordering = ('name', )
        verbose_name = "Адрес офиса"
        verbose_name_plural = "7.2. Адреса офисов СДЕК"


class Banner(models.Model):
    image = models.ImageField('Изображение ', upload_to='images/banner/', blank=True,null=True)
    url = models.CharField('Ссылка', max_length=255, blank=True, null=True)

    def __str__(self):
        return f'Баннер id {self.id}'

    class Meta:
        verbose_name = "Баннер"
        verbose_name_plural = "Баннеры"


class Category(models.Model):
    uid =models.IntegerField('UID', default=0)
    name = models.CharField('Название категории', max_length=255, blank=True, null=True)

    string = models.CharField('Текст в бегущей строке', max_length=255, blank=True, null=True)
    name_slug = models.CharField(max_length=255, blank=True, null=True, editable=False, db_index=True)
    image = models.ImageField('Изображение категории', upload_to='images/categories/', blank=True)
    is_for_man = models.BooleanField('Для мужчин', default=True)
    is_at_home = models.BooleanField('Показывать на главной', default=False)
    is_at_menu = models.BooleanField('Показывать в меню', default=True)

    def save(self, *args, **kwargs):

        self.name_slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "1. Категории"


class SubCategory(models.Model):
    uid = models.IntegerField('UID', default=0)
    category = models.ForeignKey(Category, blank=True, null=True, on_delete=models.SET_NULL, verbose_name='Категория',
                                 related_name='subcategories')
    discount = models.IntegerField('Скидка', default=0)
    name = models.CharField('Название подкатегории', max_length=255, blank=True, null=True)
    name_slug = models.CharField(max_length=255, blank=True, null=True,editable=False, db_index=True)
    image = models.ImageField('Изображение категории', upload_to='images/subcategories/', blank=True)
    weight = models.IntegerField('Вес товара в г.', blank=True, null=True)

    def save(self, *args, **kwargs):
        items = self.subcategory_items.all()
        for item in items:
            if item.discount == 0:
                item.discount=self.discount
                item.save()

        slug = slugify(self.name)
        if not self.name_slug:
            testSlug = SubCategory.objects.filter(name_slug=slug)
            slugRandom = ''
            if testSlug:
                slugRandom = '-' + ''.join(choices(string.ascii_lowercase + string.digits, k=2))
            self.name_slug = slug + slugRandom
        super(SubCategory, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.category.name}:{self.name} '

    class Meta:
        verbose_name = "Подкатегория"
        verbose_name_plural = "2. Подкатегории"


class Collection(models.Model):
    # subcategory = models.ManyToManyField(SubCategory, blank=True, verbose_name='Относится к')
    order_num = models.IntegerField('Номер по порядку', default=100)
    name = models.CharField('Название', max_length=255, blank=True, null=True)
    discount = models.IntegerField('Скидка', default=0)
    name_slug = models.CharField(max_length=255, blank=True, null=True, editable=False, db_index=True)
    title = models.CharField('Описание', max_length=255, blank=True, null=True)
    is_show_at_home = models.BooleanField('Отображать на главной', default=False)
    is_base_collection = models.BooleanField('Это базовая колекция?', default=False)

    def __str__(self):
        return f'Коллекция {self.name}'

    def save(self, *args, **kwargs):
        items = self.collection_items.all()
        for item in items:
            if item.discount == 0:
                item.discount = self.discount
                item.save()
        slug = slugify(self.name)
        if not self.name_slug:
            testSlug = SubCategory.objects.filter(name_slug=slug)
            slugRandom = ''
            if testSlug:
                slugRandom = '-' + ''.join(choices(string.ascii_lowercase + string.digits, k=2))
            self.name_slug = slug + slugRandom
        super(Collection, self).save(*args, **kwargs)


    class Meta:
        verbose_name = "Коллекция"
        verbose_name_plural = "3. Коллекции"


class ItemColor(models.Model):
    id_1c = models.CharField('ID 1C', max_length=255, blank=True, null=True)
    name_slug = models.CharField(max_length=255, blank=True, null=True, db_index=True, editable=False)
    name = models.CharField('Название', max_length=255, blank=True, null=True)
    bg_color = ColorField('Цвет', default='#000000')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = "Цвет"
        verbose_name_plural = "5.3. Цвета"

    def save(self, *args, **kwargs):
        if self.name:
            self.name_slug = slugify(self.name)
        super(ItemColor, self).save(*args, **kwargs)


class ItemSize(models.Model):
    order_num = models.IntegerField('Номер по порядку', default=100)
    id_1c = models.CharField('ID 1C', max_length=255, blank=True, null=True)
    name = models.CharField('Размер', max_length=255, blank=True, null=True)
    name_slug = models.CharField(max_length=255, blank=True, null=True, db_index=True, editable=False)


    def save(self, *args, **kwargs):
        if self.name:
            self.name_slug = slugify(self.name)
        super(ItemSize, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = "Размер"
        verbose_name_plural = "5.1. Размеры"


class ItemHeight(models.Model):
    id_1c = models.CharField('ID 1C', max_length=255, blank=True, null=True)
    name = models.CharField('Рост', max_length=255, blank=True, null=True)
    name_slug = models.CharField(max_length=255, blank=True, null=True, db_index=True, editable=False)

    def save(self, *args, **kwargs):
        if self.name:
            self.name_slug = slugify(self.name)
        super(ItemHeight, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        ordering = ('-name',)
        verbose_name = "Рост"
        verbose_name_plural = "5.2. Рост"


class ItemMaterial(models.Model):
    id_1c = models.CharField('ID 1C', max_length=255, blank=True, null=True)
    name = models.CharField('Ткань', max_length=255, blank=True, null=True)
    name_slug = models.CharField(max_length=255, blank=True, null=True, db_index=True, editable=False)

    def save(self, *args, **kwargs):
        if self.name:
            self.name_slug = slugify(self.name)
        super(ItemMaterial, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = "Ткань"
        verbose_name_plural = "5.4. Ткань"


class ItemModification(models.Model):
    id_1c = models.CharField('ID 1C', max_length=255, blank=True, null=True)
    name = models.CharField('Модификация', max_length=255, blank=True, null=True)
    name_slug = models.CharField(max_length=255, blank=True, null=True, db_index=True, editable=False)

    def save(self, *args, **kwargs):
        if self.name:
            self.name_slug = slugify(self.name)
        super(ItemModification, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = "Модификация"
        verbose_name_plural = "5.5. Модификация"


class Item(models.Model):
    id_1c = models.CharField('ID 1C', max_length=255, blank=True, null=True)
    order_num = models.IntegerField('Номер по порядку', default=100)
    subcategory = models.ForeignKey(SubCategory, verbose_name='Подкатегория',
                                   on_delete=models.SET_NULL, blank=True, null=True, db_index=True,
                                   related_name='subcategory_items')
    collection = models.ForeignKey(Collection, verbose_name='Коллекция',
                                   on_delete=models.SET_NULL, blank=True, null=True, db_index=True,
                                   related_name='collection_items')
    name = models.CharField('Название товара', max_length=255, blank=True, null=True)
    name_lower = models.CharField(max_length=255, blank=True, null=True,default='',editable=False)
    name_slug = models.CharField(max_length=255, blank=True, null=True,db_index=True)
    old_price = models.IntegerField('Цена без скидки', blank=True, default=0, editable=True)
    price = models.IntegerField('Цена', blank=True, default=0, db_index=True)
    article = models.CharField('Артикул', max_length=50, blank=True, null=True)
    discount = models.IntegerField('Скидка', default=0)
    discount_val = models.IntegerField('Скидка', default=0, editable=False)
    short_description = models.TextField('Короткое описание', blank=True, null=True)

    description = RichTextUploadingField('Тект для вкладки Детали', blank=True, null=True)
    carry = RichTextUploadingField('Тект для вкладки Состав и уход', blank=True, null=True)
    delivery = RichTextUploadingField('Тект для вкладки Срок доставки', blank=True, null=True)

    is_active = models.BooleanField('Отображать товар ?', default=False, db_index=True)
    is_in_feed = models.BooleanField('Выгружать товар ?', default=False, db_index=True)
    is_present = models.BooleanField('Товар в наличии ?', default=True, db_index=True)
    is_new = models.BooleanField('Товар новинка ?', default=False, db_index=True)
    buys = models.IntegerField(default=0,editable=False)
    views = models.IntegerField(default=0,editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    def image_tag(self):
        # used in the admin site model as a "thumbnail"
        try:
            preview = self.images.get(is_preview=True)
        except:
            preview = self.images.filter(is_preview=True).first()
        if preview:
            return mark_safe('<img src="{}" width="100" height="100" />'.format(preview.image_thumb.url))
        else:
            return mark_safe('<span>НЕТ МИНИАТЮРЫ</span>')

    image_tag.short_description = 'Основная картинка'

    def collection_tag(self):
        if self.collection:
            return self.collection.name
        else:
            return 'Без коллекции'
    collection_tag.short_description = 'Коллекция'

    def save(self, *args, **kwargs):
        if self.old_price == 0:
            self.old_price = self.price

        if self.discount > 0:
            self.discount_val = self.discount
            self.old_price = self.price
            self.price = self.price - (self.price * self.discount / 100)
        else:
            self.price = self.price + (self.old_price * self.discount_val / 100)
            self.discount_val = 0


        slug = slugify(self.name)
        if self.name and not self.name_slug:
            testSlug = Item.objects.filter(name_slug=slug)
            slugRandom = ''
            if testSlug:
                slugRandom = '-' + ''.join(choices(string.ascii_lowercase + string.digits, k=2))
            self.name_slug = slug + slugRandom
        if self.name:
            self.name_lower = self.name.lower()
        super(Item, self).save(*args, **kwargs)

    def __str__(self):
        if self.subcategory:
            return f'{self.subcategory.category.name}:{self.subcategory.name} - {self.name}'
        else:
            return 'НЕТ ПОДКАТЕГОРИИ'

    class Meta:
        ordering = ('order_num',)
        verbose_name = "Базовый товар"
        verbose_name_plural = "4. Базовые товары"


class ItemType(models.Model):
    id_1c = models.CharField('ID 1C', max_length=255, blank=True, null=True)
    bar_cade = models.CharField('Штрихкод', max_length=255, blank=True, null=True)
    name_slug = models.CharField(max_length=255, blank=True, null=True, db_index=True,editable=False)
    item = models.ForeignKey(Item, verbose_name='Базовый товар',
                                    on_delete=models.CASCADE, blank=True,null=True,db_index=True,
                             related_name='types')
    color = models.ForeignKey(ItemColor, verbose_name='Цвет',
                             on_delete=models.CASCADE, blank=True, null=True, db_index=True, related_name='colors')
    size = models.ForeignKey(ItemSize, verbose_name='Размер',
                             on_delete=models.CASCADE, blank=True, null=True, db_index=True, related_name='sizes')
    height = models.ForeignKey(ItemHeight, verbose_name='Рост',
                             on_delete=models.CASCADE, blank=True, null=True, db_index=True, related_name='heights')
    material = models.ForeignKey(ItemMaterial, verbose_name='Ткань', on_delete=models.SET_NULL, blank=True,
                                 null=True, db_index=True, related_name='materials')
    modification = models.ForeignKey(ItemModification, verbose_name='Модификация',
                                 on_delete=models.SET_NULL, blank=True, null=True, db_index=True,
                                 related_name='modification')
    modification_id_1c = models.CharField('ID Модификации 1C', max_length=255, blank=True, null=True)
    quantity = models.IntegerField('Остаток', default=0)

    def __str__(self):
        return f'Вид товара : {self.item.name} | {self.color.name} |' \
               f' {self.size.name} | {self.height.name} || Остаток: {self.quantity}'# | {self.material.name} | {self.modification.name}'

    class Meta:
        verbose_name = "Вид товара"
        verbose_name_plural = "5. Виды товаров"

    def get_path(self):
        try:
            return f'/category/{self.item.subcategory.category.name_slug}/{self.item.subcategory.name_slug}/{self.item.name_slug}'
        except:
            return ''
    #
    # def save(self, *args, **kwargs):
    #
    #     # self.name_slug = f'{self.item.name_slug}-{self.color.name_slug}-' \
    #     #                  f'{self.size.name_slug}-{self.height.name_slug}'
    #     super(ItemType, self).save(*args, **kwargs)

    def color_tag(self):
        return self.color.name
    color_tag.short_description = 'Цвет'

    def article_tag(self):
        if self.item:
            return self.item.article
    article_tag.short_description = 'Артикул'

    def name_tag(self):
        return self.item.name
    name_tag.short_description = 'Базовый товар'

    def size_tag(self):
        return self.size.name
    size_tag.short_description = 'Размер'

    def height_tag(self):
        return self.height.name
    height_tag.short_description = 'Рост'

    def material_tag(self):
        if self.material:
            return self.material.name
        else:
            return 'Нет'
    material_tag.short_description = 'Ткань'

    def modification_tag(self):
        if self.modification:
            return self.modification.name
        else:
            return 'Нет'
    modification_tag.short_description = 'Модификация'

    def quantity_tag(self):
        return self.quantity
    quantity_tag.short_description = 'Остаток'


class ItemImage(models.Model):
    item = models.ForeignKey(Item, blank=True, null=True, on_delete=models.CASCADE, verbose_name='К товару',
                             related_name='images')
    image = models.ImageField('Изображение товара', upload_to='images/catalog/items/', blank=True)
    image_thumb = models.ImageField('Изображение товара', upload_to='images/catalog/items/', blank=True, editable=False)
    color = models.ForeignKey(ItemColor, on_delete=models.SET_NULL, verbose_name='Цвет', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_preview = models.BooleanField('Это превью', default=False)

    def __str__(self):
        return '%s Изображение для товара : %s ' % (self.id, self.item.name)

    class Meta:
        verbose_name = "Изображение для товара"
        verbose_name_plural = "Изображения для товара"

    def image_tag(self):
        # used in the admin site model as a "thumbnail"
        if self.image:
            return mark_safe('<img src="{}" width="150" height="150" />'.format(self.image_thumb.url))
        else:
            return mark_safe('<span>НЕТ МИНИАТЮРЫ</span>')

    image_tag.short_description = 'Картинка'

    def save(self, *args, **kwargs):
        self.image_thumb.save(f'{self.item.name_slug}-thumb.jpg',
                              File(image_resize_and_watermark(self.image, False, 350, 450)), save=False)
        super(ItemImage, self).save(*args, **kwargs)


class PromoCode(models.Model):
    code = models.CharField('ПромоКод', max_length=255, blank=False, null=True)
    discount = models.IntegerField('Скидка % по коду',default=0)
    summ = models.IntegerField('Скидка в рублях по коду',default=0)

    def __str__(self):
        return f'Промо код {self.code} | Скидка {self.discount}% | Скидка {self.summ}руб'
    class Meta:
        verbose_name = "Промо код"
        verbose_name_plural = "6. Промо коды"


class CartItem(models.Model):
    client = models.ForeignKey('user.User', blank=True, null=True, default=None, on_delete=models.CASCADE)
    guest = models.ForeignKey('user.Guest', blank=True, null=True, default=None, on_delete=models.CASCADE)
    item_type = models.ForeignKey(ItemType, blank=True, null=True, on_delete=models.CASCADE, db_index=True)
    quantity = models.IntegerField('Кол-во', blank=True, null=True, default=1)
    price = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.item_type.item.name} | {self.item_type.color.name} |' \
               f' {self.item_type.size.name} | {self.item_type.height.name} X {self.quantity}'

    class Meta:
        verbose_name = "Товар в корзине"
        verbose_name_plural = "Товары в корзинах"

    def save(self, *args, **kwargs):
        self.price = self.item_type.item.price * self.quantity
        super(CartItem, self).save(*args, **kwargs)


class Cart(models.Model):
    client = models.ForeignKey('user.User', blank=True, null=True, default=None, on_delete=models.CASCADE,
                               verbose_name='Корзина клиента')
    guest = models.ForeignKey('user.Guest', blank=True, null=True, default=None, on_delete=models.CASCADE,
                              verbose_name='Корзина гостя')
    promo_code = models.ForeignKey(PromoCode, blank=True, null=True, default=None, on_delete=models.CASCADE,
                              verbose_name='Промокод')
    items = models.ManyToManyField(CartItem, blank=True, verbose_name='Товары', db_index=True)
    weight = models.IntegerField(default=0)
    raw_price = models.IntegerField(default=0)
    total_price = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.client:
            return f'Корзина клиента : {self.client.id} '
        else:
            return f'Корзина гостя : {self.guest.id} '

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

class OrderItem(models.Model):
    item_type = models.ForeignKey(ItemType, blank=True, null=True, on_delete=models.CASCADE)
    quantity = models.IntegerField('Кол-во', blank=True, null=True, default=1)
    price = models.IntegerField(default=0)

    def __str__(self):
        return "Товар в заказе"

    class Meta:
        verbose_name = "Товар в заказе"
        verbose_name_plural = "Товары в заказах"

    def save(self, *args, **kwargs):
        self.price = self.item_type.item.price * self.quantity
        super(OrderItem, self).save(*args, **kwargs)

class Order(models.Model):
    client = models.ForeignKey('user.User', blank=True, null=True, default=None, on_delete=models.CASCADE,
                               verbose_name='Заказ клиента')
    guest = models.ForeignKey('user.Guest', blank=True, null=True, default=None, on_delete=models.CASCADE,
                              verbose_name='Заказ гостя')
    promo_code = models.ForeignKey(PromoCode, blank=True, null=True, default=None, on_delete=models.SET_NULL,
                               verbose_name='Использованный промо-код')
    items = models.ManyToManyField(OrderItem, blank=True, verbose_name='Товары')
    payment = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    fio = models.CharField(max_length=255, blank=True, null=True)
    street = models.CharField(max_length=255, blank=True, null=True)
    house = models.CharField(max_length=255, blank=True, null=True)
    flat = models.CharField(max_length=255, blank=True, null=True)

    delivery = models.ForeignKey(DeliveryType, blank=True, null=True, default=None, on_delete=models.CASCADE,
                               verbose_name='Доставка')
    city = models.ForeignKey(City, blank=True, null=True, default=None, on_delete=models.CASCADE,
                                 verbose_name='Город')
    comment = models.TextField(blank=True, null=True)
    total_price = models.IntegerField('Общая стоимость заказа', default=0)
    # total_price_with_code = models.DecimalField('Общая стоимость заказа с учетом промо-кода', decimal_places=2,
    #                                             max_digits=10, default=0)
    weight = models.IntegerField(default=0)
    delivery_price = models.IntegerField(default=0)

    track_code = models.CharField('Трек код', max_length=50, blank=True, null=True)
    order_code = models.CharField('Код заказа', max_length=10, blank=True, null=True)
    is_complete = models.BooleanField('Заказ выполнен ?', default=False)
    is_payed = models.BooleanField('Заказ оплачен ?', default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Заказ ID {self.id} от {self.created_at}'

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

class PaymentObj(models.Model):
    pay_id = models.CharField('ID платежа yandex',max_length=255,blank=True,null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, blank=True, null=True)
    client = models.ForeignKey('user.User', blank=True, null=True,
                                  on_delete=models.CASCADE,
                                  verbose_name='Пользователь')
    guest = models.ForeignKey('user.Guest', blank=True, null=True,
                                  on_delete=models.CASCADE,
                                  verbose_name='Гость')

    type = models.CharField('Вид платежа',max_length=255,blank=True,null=True)
    status = models.CharField('Статус платежа', max_length=255,blank=True,null=True)
    amount = models.IntegerField('Сумма платежа', blank=True,null=True)
    is_payed = models.BooleanField("Оплачен?", default=False)
    created_at = models.DateTimeField("Дата платежа", auto_now_add=True)

    def __str__(self):
        return f'Платеж от {self.created_at}. На сумму {self.amount}. Статус {self.is_payed}'

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"
