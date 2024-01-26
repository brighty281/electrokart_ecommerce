"""
URL configuration for electrokart project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from . import views

urlpatterns = [
    #path('homepage/',views.homepage,name='homepage'),
    #path('loginpage/',views.loginpage,name='loginpage'),
    path('',views.loginpage,name='loginpage'),
    path('logout/',views.Logout,name='logout'),
    path('otp_verification/', views.otp_verification, name='otp_verification'),
    path('pageregister/',views.signup,name='pageregister'),
    path('base_page/',views.base_page,name='base_page'),
    #path('pagelogin/',views.loginpage,name='pagelogin'),
    path('contact/',views.contact,name='contact'),
    path('about/',views.about,name='about'),
    path('pageaccount/',views.page_account,name='pageaccount'),
    path('myaddress/',views.addressinfo,name='myaddress'),
    path('editaddress/<int:uid>',views.edit_addressinfo,name='editaddress'),
    path('addaddress/',views.add_addressinfo,name='addaddress'),
    #path('deleteaddress/<int:uid>',views.delete_addressinfo,name='deleteaddress'),
    path('landingpage/',views.landing_page,name='landingpage'),
    path('productlist/<int:uid>',views.product_list,name='productlist'),
    path('all_productlist/',views.all_productlist,name='all_productlist'),
    path('search_productlist/',views.search_productlist,name='search_productlist'),
    path('filter_productlist/',views.filter_productlist,name='filter_productlist'),

    path('product_details/<int:uid>',views.product_details,name='product_details'),
    path('cancelorder/<int:uid>',views.cancel_order,name='cancelorder'),
    path('returnorder/<int:uid>',views.return_order,name='return_order'),
    path('add_to_cart/<int:uid>',views.add_to_cart,name="add_to_cart"),
    path('show_cart/',views.show_cart,name='show_cart'),
    path('pluscart/',views.plus_cart,name="pluscart"),
    path('minuscart/',views.minus_cart,name="minuscart"),
    path('removecart/',views.remove_cart),
    path('checkout/',views.checkout,name="checkout"),
    path('paymentdone/',views.payment_done,name="paymentdone"),
    path('myorders/',views.my_orders,name='myorders'),
    path('mycoupons/',views.my_coupons,name='mycoupons'),
    path('mywallet/',views.my_wallet,name="mywallet"),
    path('choosepayment/',views.choose_payment,name='choosepayment'),
    path('success/',views.success,name='success'),
    path('invoice/',views.invoice,name='invoice'),
    path('invoice/pdf/', views.invoice_pdf, name='invoice_pdf'),
    path('orderpage_invoice/<int:uid>',views.orderpage_invoice,name='orderpage_invoice'),
    # path('initiate_razorpay_payment/', views.initiate_razorpay_payment, name='initiate_razorpay_payment'),
    # path('process_payment/', views.process_payment, name='process_payment'),
   # path('basefile/',views.basefile,name='basefile'),
    path('customer_info/<str:name>',views.customer_info,name='customer_info'),
    path('forgot_password/',views.forgot_password,name='forgot_password'),
    path('fp_otpverify',views.fp_otpverify,name='fp_otpverify'),
    path('change_password/',views.change_password,name='change_password')
    
]
