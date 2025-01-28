from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token # type: ignore
from .views import register, loan_list_create, loan_detail, offer_list_create, accept_offer, make_payment

urlpatterns = [
    path('auth/register/', register, name='register'),
    path('auth/login/', obtain_auth_token, name='login'),
    path('loans/', loan_list_create, name='loans'),
    path('loans/<int:pk>/', loan_detail, name='loan-detail'),
    path('offers/', offer_list_create, name='offers'),
    path('offers/<int:pk>/accept/', accept_offer, name='accept-offer'),
    path('payments/<int:pk>/', make_payment, name='make-payment'),
]