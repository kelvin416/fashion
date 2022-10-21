from django.urls import path
from . import views

urlpatterns = [
    path('', views.store, name="store"),
    path('cart/', views.cart, name="cart"),
    path('checkout/', views.checkout, name="checkout"),

    path('cart/update_item/', views.update_item, name="update_item"),

    path('process_order/', views.process_order, name="process_order"),

    # mpesa url
    path('daraja', views.daraja_mpesa, name='daraja_mpesa'),
    path('daraja/stk_push/', views.stk_push_callback, name="stk_push_callback")
    
]
