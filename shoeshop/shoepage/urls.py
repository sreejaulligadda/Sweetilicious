from django.conf import settings
from django.urls import path
from django.urls import path
from .views import *
from django.conf.urls.static import static
app_name = 'shoepage'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
     path('shop/', ShopView.as_view(), name='shop'),
    path('category/<slug>/', CategoryView.as_view(), name='category'),
    path('product/<slug>/', ItemDetailView.as_view(), name='product'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('notify/', send_payment_email, name='send_payment_email'),
    path('add_coupon/', AddCouponView.as_view(), name='add-coupon'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('remove-item-from-cart/<slug>/', remove_single_item_from_cart,
         name='remove-single-item-from-cart'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),
    path('process-payment/<payment_option>/', PaypalView.as_view(), name='process_payment'),
    path('payments/cash/', CashView.as_view(), name='cash'),
    path('contact/', Contact.as_view(), name='contact'),
    path('privacy/', Privacy.as_view(), name='privacy'),
    path('wishlist/', view_wishlist, name='view_wishlist'),
    path('wishlist/add/<int:product_id>/', add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', remove_from_wishlist, name='remove_from_wishlist'),
    path('search/', search, name='search'),
    path('contact/', Contact.as_view(), name='contact'),
    path('filter-products/', filter_products, name='filter_products'),
    path('get-states/', get_states, name='get_states'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)