from django.urls import path,include
from . import views

urlpatterns = [
    path('get_banners', views.GetBanners.as_view()),
    path('get_delivery', views.GetDelivery.as_view()),
    path('get_categories', views.GetCategories.as_view()),
    path('get_collections', views.GetCollections.as_view()),
    path('get_home_collections', views.GetHomeCollections.as_view()),
    path('get_subcategory_items', views.GetSubcategoryItems.as_view()),
    path('get_item', views.GetItem.as_view()),
    path('get_cart', views.GetCart.as_view()),
    path('add_to_cart', views.AddToCart.as_view()),
    path('delete_item', views.DeleteItem.as_view()),
    path('plus_quantity', views.PlusQuantity.as_view()),
    path('minus_quantity', views.MinusQuantity.as_view()),
    path('apply_promo', views.ApplyPromo.as_view()),

    path('catalog.xml', views.catalog_feed, name='catalog_feed'),

]
