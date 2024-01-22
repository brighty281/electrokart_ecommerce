

from django.urls import path
from . import views

urlpatterns = [
    path('admin_login',views.admin_login,name='admin_login'),
    path('admin_home',views.admin_home,name='admin_home'),
    path('admin_logout',views.admin_logout,name='admin_logout'),
    path('userslist',views.user_list,name='userslist'),

    path('edituser/<int:uid>/',views.edit_user,name='edituser'),
    path('deleteuser/<int:uid>/',views.delete_user,name='deleteuser'),
    path('adduser',views.add_user,name='adduser'),

    path('maincat_list',views.maincat_list,name='maincat_list'),
    path('editmaincatlist/<int:uid>/',views.edit_maincat_list,name='editmaincatlist'),
    path('deletemaincatlist/<int:uid>/',views.delete_maincat_list,name='deletemaincatlist'),
    path('addmaincatlist',views.add_maincat_list,name='addmaincatlist'),
    path('brandlist/<int:uid>/',views.brand_list,name='brandlist'),
    path('editsubcatlist/<int:uid>/',views.edit_subcat_list,name='editsubcatlist'),
    path('deletesubcatlist/<int:uid>/',views.delete_subcat_list,name='deletesubcatlist'),
    path('add_product/',views.add_product,name='add_product'),
    path('product_list/',views.product_list,name='product_list'),
    path('edit_product/<int:uid>/',views.edit_product,name='edit_product'),
    path('delete_product/<int:uid>/',views.delete_product,name='delete_product'),
    path('orders_list/',views.orders_list,name='orders_list'),
    path('edit_orderlist/<int:uid>/',views.edit_orderlist,name='edit_orderlist'),
    path('addorder/',views.add_order,name='add_order'),
    path('deleteorder/<int:uid>',views.delete_order,name='delete_order'),
    path('order_details/<int:uid>',views.order_details,name='order_details'),
    path('search_orderlist',views.search_orderlist,name='search_orderlist'),
    path('filter_orderlist/',views.filter_orderlist,name='filter_orderlist'),
    path('cancel_refund/<int:uid>',views.cancel_order_with_refund,name='cancel_refund'),


    path('couponlist/',views.coupon_list,name='couponlist'),
    path('addcoupon/',views.add_coupon,name='addcoupon'),
    path('editcoupon/<int:uid>',views.edit_coupon,name='editcoupon'),
    path('deletecoupon/<int:uid>',views.delete_coupon,name='deletecoupon'),
    path('userslist_coupon/',views.userslist_coupon,name='userslist_coupon'),
    path('my_couponlist/<int:uid>',views.my_couponlist,name='my_couponlist'),
    path('edit_mycoupon/<int:uid>',views.edit_mycoupon,name='edit_mycoupon'),
    path('add_mycoupon/',views.add_mycoupon,name='add_mycoupon'),
    path('delete_mycoupon/<int:uid>',views.delete_mycoupon,name='delete_mycoupon'),

    path('week_sales/',views.week_sales,name='week_sales'),
    path('current_year_sales/',views.current_year_sales,name='current_year_sales'),
    path('today_sales/',views.today_sales,name='today_sales')
    
    
]
