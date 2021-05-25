from docs_api.celery import app
from .models import *
from lxml import etree
import ftputil
import settings

@app.task
def checkFtp():
    with ftputil.FTPHost('185.92.148.221', settings.FTP_USER, settings.FTP_PASSWORD) as host:
        names = host.listdir(host.curdir)
        for name in names:
            if host.path.isfile(name):
                host.download(name, name)
    tree = etree.parse('tovar.xml')
    root = tree.getroot()
    new_items = 0
    updated_items = 0
    new_items_types = 0
    updated_items_types = 0
    for element in root:
        item_id = element.find("basic_item").text
        item_name = element.find("name").text
        item_price = element.find("price").text
        item, created = Item.objects.get_or_create(id_1c=item_id)
        print(item_name)
        if created:
            new_items += 1
        else:
            updated_items += 1
        item.name = item_name
        item.price = int(item_price)
        item.save()

    tree = etree.parse('vigruzka.xml')
    root = tree.getroot()

    for element in root:
        basic_item_id = element.find("basic_item").text
        base_item = None
        try:
            base_item = Item.objects.get(id_1c=basic_item_id)
        except Item.DoesNotExist:
            print('BASE ITEM NOT EXIST. ABORT')
            base_item = None

        color_id = element.find("color").text
        color, created = ItemColor.objects.get_or_create(id_1c=color_id)
        if created:
            color.add_id = color_id
            color.name = 'Новый цвет'
            color.save()

        size_name = element.find("size").text
        size, created = ItemSize.objects.get_or_create(name=size_name)
        if created:
            size.name = size_name
            size.save()

        height_name = element.find("height").text
        height, created = ItemHeight.objects.get_or_create(name=height_name)
        if created:
            height.name = height_name
            height.save()

        add_id = element.find("add").text
        if not add_id:
            add_id = 0

        mod, created = ItemModification.objects.get_or_create(id_1c=add_id)
        if created:
            mod.id_1c = add_id
            mod.name = 'Новая модификация'
            mod.save()

        cloth_id = element.find("cloth").text
        material, created = ItemMaterial.objects.get_or_create(id_1c=cloth_id)
        if created:
            material.id_1c = cloth_id
            material.name = 'Новая ткань'
            material.save()

        item_id = element.find("item_id").text

        try:
            bar_code = element.find("barcode").text
        except:
            bar_code = ''

        if base_item:
            item_type, created = ItemType.objects.get_or_create(id_1c=item_id)
            if created:
                new_items_types += 1
            item_type.item = base_item
            item_type.color = color
            item_type.bar_cade = bar_code
            item_type.size = size
            item_type.height = height
            item_type.material = material
            item_type.modification = mod
            item_type.save()
            updated_items_types += 1


@app.task
def checkOstatok():
    from lxml import etree
    with ftputil.FTPHost('185.92.148.221', settings.FTP_USER, settings.FTP_PASSWORD) as host:
        names = host.listdir(host.curdir)
        for name in names:
            if host.path.isfile(name):
                host.download(name, name)
    tree = etree.parse('VigruzkaOstatok.xml')
    root = tree.getroot()
    print(root)
    items = 0
    for element in root:
        print(element)
        item_id = element.find("item_id").text
        quantity = element.find("goods").text
        print(item_id)
        try:
            item = ItemType.objects.get(id_1c=item_id)
            item.quantity = int(quantity)
            item.save()
            items += 1
        except:
            pass

