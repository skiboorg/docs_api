from django.urls import path,include
from . import views

urlpatterns = [
    path('get_banners', views.GetBanners.as_view()),
    path('get_delivery', views.GetDelivery.as_view()),
    path('get_categories', views.GetCategories.as_view()),
    path('get_collection_by_slug', views.GetCollectionBySlug.as_view()),
    path('get_home_collections', views.GetHomeCollections.as_view()),
    path('get_subcategory_items', views.GetSubcategoryItems.as_view()),
    path('get_item', views.GetItem.as_view()),
    path('get_recomended_items', views.GetRecommendedItems.as_view()),
    path('get_cart', views.GetCart.as_view()),
    path('add_to_cart', views.AddToCart.as_view()),
    path('delete_item', views.DeleteItem.as_view()),
    path('plus_quantity', views.PlusQuantity.as_view()),
    path('minus_quantity', views.MinusQuantity.as_view()),
    path('apply_promo', views.ApplyPromo.as_view()),
    path('create_order', views.CreateOrder.as_view()),
    path('check_ftp', views.CheckFtp.as_view()),
    path('check_ostatok', views.CheckOstatok.as_view()),
    path('calculate_delivery', views.CalculateDelivery.as_view()),
    path('order_payed', views.OrderPayed.as_view()),
    path('fill_city', views.FillC.as_view()),
    path('get_user_orders', views.GetUserOrders.as_view()),


    path('catalog.xml', views.catalog_feed, name='catalog_feed'),

]
