from django.shortcuts import render,redirect
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
from django.contrib import messages, auth
from django.contrib.auth.models import User
import random
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.cache import never_cache
from django.views.decorators.cache import cache_control
import re
from .decorator import admin_required
from adminapp.models import MainCategory,Product,MultipleImages, CustomerInfo, ProductHighlights,AdditionalInfo, Cart, address,OrderPlaced, Coupon,UserCoupon, wallet,Order
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.http import JsonResponse
from django.db.models import Sum
from decimal import Decimal
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa  # Install xhtml2pdf: pip install xhtml2pdf
import math
# Create your views here.
@never_cache
@admin_required
def page_account(request):
    if request.user.is_authenticated:
        return render(request,'users/page-account.html',{'username': request.user.username})
    else:
        return redirect('loginpage')


@never_cache
@admin_required
def signup(request):
        
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        request.session["username"]=username
        request.session["password"]=confirm_password
        request.session["email"]=email
        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("pageregister")

        try:
            if User.objects.get(username=username):
                messages.error(request, "Username already exists")
                return redirect("pageregister")
        except:
            pass

        try:
            if User.objects.get(email=email):
                messages.error(request, "Email already exists")
                return redirect("pageregister")
        except:
            pass

        if not re.match(r'^[\w.@+-]+$',username):
            messages.error(request, "Invalid username")
            return redirect("pageregister")

        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            messages.error(request, "Invalid email")
            return redirect("pageregister")

        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters")
            return redirect("pageregister")
        
        if password==confirm_password:
            send_otp(request)
            return render(request, 'users/otp.html', {"email":email})
        

    

    return render(request,'users/page-login-register.html')

def send_otp(request):
    s=""
    for x in range(0,4):
        s+=str(random.randint(0,9))
    request.session["otp"]=s
    send_mail("otp for sign up",s,'brightythomas281@gmail.com',[request.session['email']],fail_silently=False)
    return render(request,"users/otp.html")

def otp_verification(request):
    if request.method == 'POST':
        otp=request.POST.get("otp")
    if  otp==request.session["otp"]:
        encryptedpassword=make_password(request.session['password'])
        nameuser=User(username=request.session['username' ], email=request.session['email'], password=encryptedpassword)
        nameuser.save()
        messages.info(request,'signed in successfully ... ')
        User.is_active=True
        return redirect('loginpage')
    else:
        messages.error(request, "otp doesn't match")
        return render(request, 'users/otp.html')

@never_cache
@admin_required
def loginpage(request):
    if request.user.is_authenticated:
        return redirect('pageaccount')
    if request.method == 'POST':
        username=request.POST.get('username')
        password=request.POST.get('password')

        user=authenticate(username=username,password=password)
        if user is not None and not user.is_superuser:
            request.session['username'] = username
            login(request, user)
            return redirect('landingpage')
        else:
            messages.error(request, 'Invalid credentials')
            return redirect('loginpage')
    return render(request,'users/loginpage.html')

@never_cache
@admin_required
def Logout(request):
    if request.method=='POST':
        request.session.flush()
        logout(request)
    return redirect('landingpage')

@never_cache
def contact(request):
    return render(request,'users/contact.html')

@never_cache
def about(request):
    return render(request,'users/about.html')

def customer_info(request,name):   
    my_user=User.objects.get(username=name)
    my_customer, created = CustomerInfo.objects.get_or_create(user=my_user)
    context={
        'my_user':my_user,
        'my_customer':my_customer
    }

    if request.method=='POST':
        first_name=request.POST.get('fname')
        last_name=request.POST.get('lname')
        phone=request.POST.get('phone')
        new_email=request.POST.get('email')
        my_user.email=new_email
        my_user.save()
        my_customer.first_name=first_name
        my_customer.last_name=last_name
        my_customer.phone=phone
        my_customer.user_email=my_user.email
        my_customer.user_password=my_user.password
        my_customer.save()
        return redirect('pageaccount')   
        


    return render(request,'users/account_details.html',context)

def forgot_password(request):
    if request.method=='POST':
        username=request.POST.get('username')
        
        try:
            my_user=User.objects.get(username=username)
            request.session["username"]=username
            request.session['email']=my_user.email
            send_otp(request)
            return render(request,'users/fp_otp.html',{'email':my_user.email})
        except:
            messages.error(request,'user unavailable')
            return render(request,'users/forgot_password.html')
        
    return render(request,'users/forgot_password.html')

def fp_sendotp(request):
    s=""
    for x in range(0,4):
        s+=str(random.randint(0,9))
    request.session["otp"]=s
    send_mail("otp for sign up",s,'brightythomas281@gmail.com',[request.session['email']],fail_silently=False)
    return render(request,"users/fp_otp.html")    
        
def fp_otpverify(request):
    if request.method == 'POST':
        otp=request.POST.get("otp")
        if otp==request.session.get("otp"):
            return redirect('change_password')
        else:
            messages.error(request, "otp doesn't match")
            return render(request, 'users/fp_otp.html')
 
def change_password(request):
    myusername=request.session["username"]
    myuser=User.objects.get(username=myusername)
    if request.method=='POST':
        new_password=request.POST.get('newpassword')
        confirm_password=request.POST.get('confpassword')

        if new_password==confirm_password:
            myuser.set_password(confirm_password)
            myuser.save()
            messages.success(request, 'Password changed successfully')
            return redirect('loginpage')
        else:
            messages.error(request,"password does not match")
            return render(request, 'users/changepassword.html')
    
    return render(request, 'users/changepassword.html')

def addressinfo(request):
    if request.user.is_authenticated:
        my_address=address.objects.filter(user=request.user)
        
    return render(request,'users/my_address.html',{'my_address':my_address})
def add_addressinfo(request):
    if request.user.is_authenticated:
        my_address=address.objects.all()
        if request.method=='POST':
            new_name=request.POST.get('name')
            new_housename=request.POST.get('house_name')
            new_locality=request.POST.get('locality')
            new_city=request.POST.get('city')
            new_zipcode=request.POST.get('zipcode')
            new_state=request.POST.get('state')

            new_address=address.objects.create(
                user=request.user,
                name=new_name,
                house_name=new_housename,
                locality=new_locality,
                city=new_city,
                zipcode=new_zipcode,
                state=new_state
            )
            if 'amount_to_pay' in request.session and request.session['amount_to_pay']:
                newly_added_address_id = new_address.id
                request.session['newly_added_address_id'] = newly_added_address_id
                return redirect('checkout')
            else:
                return redirect('myaddress')
    return render(request,'users/add_address.html')

def edit_addressinfo(request,uid):
    if request.user.is_authenticated:
        my_address=address.objects.get(id=uid)
        if request.method=='POST':
            new_name=request.POST.get('name')
            new_housename=request.POST.get('house_name')
            new_locality=request.POST.get('locality')
            new_city=request.POST.get('city')
            new_zipcode=request.POST.get('zipcode')
            new_state=request.POST.get('state')

            my_address.name=new_name
            my_address.house_name=new_housename
            my_address.locality=new_locality
            my_address.city=new_city
            my_address.zipcode=new_zipcode
            my_address.state=new_state
            my_address.save()
            if 'amount_to_pay' in request.session and request.session['amount_to_pay']:
                return redirect('checkout')
            else:
                return redirect('myaddress')
    return render(request,'users/edit_address.html',{'my_address':my_address}) 

# def delete_addressinfo(request,uid):
#     if request.user.is_authenticated:
#         user=request.user
#         my_address=address.objects.filter(id=uid,user=user)
#         my_address.delete()
        
#     return render(request,'users/my_address.html')




@never_cache
@admin_required
def landing_page(request):
    # if request.user.is_authenticated:
    main_category_all=MainCategory.objects.all()
    latest_products=[]
    for category in main_category_all:
        product=Product.objects.filter(main_category=category,product_active=True).order_by('-our_price').first()
        latest_products.append(product)

    context={
        'main_category_all':main_category_all,
        'latest_products':latest_products
    }
    return render(request,'users/index.html',context)


def base_page(request):
    if request.user.is_authenticated:
        main_category_all=MainCategory.objects.all()
        context={
            'main_category_all':main_category_all
        }
    return render(request,'users/base.html',context)

def product_list(request,uid):
    # if request.user.is_authenticated:
    all_products=Product.objects.all()
    main_category=MainCategory.objects.get(id=uid)
    main_category_all=MainCategory.objects.all()
    my_products=Product.objects.filter(main_category=main_category)
    product_count=my_products.count()
    context={
        'all_products':all_products,
        'main_category':main_category,
        'my_products':my_products,
        'main_category_all':main_category_all,
        'product_count':product_count
    }
    return render(request,'users/product_list.html',context)

def all_productlist(request):
    # if request.user.is_authenticated:
    all_products=Product.objects.all()
    main_category_all=MainCategory.objects.all()
    return render(request,'users/all_productlist.html',{'all_products':all_products,'main_category_all':main_category_all})


def product_details(request,uid):
    print(type(uid))
    # if request.user.is_authenticated:
    my_product=Product.objects.get(id=uid)
    my_images=MultipleImages.objects.filter(product=my_product)
    highlights=ProductHighlights.objects.filter(product=my_product)
    additional_info=AdditionalInfo.objects.filter(product=my_product)
    variant_list=Product.objects.filter(base_name=my_product.base_name)
    item_already_in_cart=False
    if request.user == 'AnonymousUser':
        item_already_in_cart=Cart.objects.filter(Q(product=uid) & Q(user=request.user)).exists()
    context={
        'my_product':my_product,
        'my_images':my_images,
        'variant_list':variant_list,
        'highlights':highlights,
        'additional_info':additional_info,
        'item_already_in_cart':item_already_in_cart
        }
    return render(request,'users/product_details.html',context)

def search_productlist(request):
    # if request.user.is_authenticated:
        #all_products=Product.objects.all()
    main_category_all=MainCategory.objects.all()
    my_category_id=request.GET.get('category')

    if not my_category_id:
        my_products=Product.objects.all()
    elif my_category_id=='all':
        my_products=Product.objects.all()
    else:
        my_category=MainCategory.objects.get(id=my_category_id)
        my_products=Product.objects.filter(main_category=my_category)
    
    query=request.GET.get('search')
    if query:
        results=my_products.filter(Q(title__icontains=query) |Q(base_name__icontains=query))
        result_count=results.count()
    else:
        return redirect('all_productlist')
    return render(request,'users/search_productlist.html',{'results':results, 'main_category_all':main_category_all,'result_count':result_count})


def filter_productlist(request):
    # if request.user.is_authenticated:
    all_products = Product.objects.all()
    main_category_all = MainCategory.objects.all()
    
    min_price = request.GET.get('minPrice')
    max_price = request.GET.get('maxPrice')
    
    # Ensure min_price and max_price are integers or floats
    if min_price is not None and max_price is not None:
        min_price = float(min_price)
        max_price = float(max_price)
        # Filter products based on price range
        results = all_products.filter(our_price__gte=min_price, our_price__lte=max_price)
        result_count=results.count()
    else:
        results = all_products  # Return all products if no price range is specified
        result_count=results.count()
    return render(request,'users/search_productlist.html',{'results': results, 'main_category_all': main_category_all, 'result_count':result_count})

#***********************cart***************************#

def add_to_cart(request,uid):
    if request.user.is_authenticated:
        user=request.user
        product=Product.objects.get(id=uid)
        Cart(user=user,product=product).save()
        return redirect('show_cart')
    else:
        return redirect('loginpage')

def show_cart(request):
    if request.user.is_authenticated:
        user=request.user
        cart=Cart.objects.filter(user=user)
        #print(cart)
        cart_products=[p for p in cart if p.user== user]
        amount=0
        discount_amount=0
        if cart_products:
            for p in cart_products:
                tempamount=(p.quantity*p.product.our_price)
                amount+=tempamount
            
        if request.method == 'POST':
            coupon_code = request.POST.get('coupon_code')  # Assuming the form field is named 'coupon_code'
            my_coupon = Coupon.objects.filter(code=coupon_code).first()
            used_coupons=UserCoupon.objects.filter(user=user,is_used=True)
            if my_coupon:
                try:
                    for i in used_coupons:
                        if i.coupon.code==my_coupon.code:
                            return render(request, 'users/cart.html', {'cart': cart, 'amount': amount, 'error_message': 'Coupon used','discount_amount':discount_amount})

                           
                    if my_coupon not in used_coupons:
                        discount = my_coupon.discount
                        discounted_amount = Decimal(amount) - (Decimal(amount) * (discount / Decimal(100)))
                        discount_amount = Decimal(amount) * (discount / Decimal(100))                                                       
                        request.session['discount_amount'] = float(discount_amount)
                        amount = float(discounted_amount)
                        new_used_coupon=UserCoupon(user=user,coupon=my_coupon,is_used=True)
                        new_used_coupon.save()
                        return render(request, 'users/cart.html', {'cart': cart, 'amount': amount, 'success_message': 'Coupon successfully added','discount_amount':discount_amount})
                        
                except AttributeError:
                    # Handle missing attributes or unexpected data
                    return render(request, 'users/cart.html', {'cart': cart, 'amount': amount, 'error_message': 'Invalid coupon data','discount_amount':discount_amount})
            
            # Handle invalid coupon code or coupon not found
            return render(request, 'users/cart.html', {'cart': cart, 'amount': amount, 'error_message': 'Invalid coupon code','discount_amount':discount_amount})
        return render(request,'users/cart.html',{'cart':cart,'amount':amount,'discount_amount':discount_amount})
    else:
        return redirect('loginpage')

def plus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET.get('prod_id')
        user_cart = Cart.objects.filter(product=prod_id, user=request.user)
        if user_cart.exists():
            c = user_cart.first()  # Considering only the first instance if multiple are found
            c.quantity += 1
            c.save()
            c.sub_total=c.product.our_price*c.quantity
            c.save()
            
            amount = 0
            cart_products = Cart.objects.filter(user=request.user)
            
            for p in cart_products:
                temp_amount = (p.quantity * p.product.our_price)
                amount += temp_amount

            data = {
                'quantity': c.quantity,
                'amount': amount,
                'sub_total':c.sub_total
            }
            return JsonResponse(data)
        
        # Handle case if the user doesn't have this product in the cart
        return JsonResponse({'error': 'Product not found in cart'})

    # Handle other HTTP methods if needed
    return JsonResponse({'error': 'Invalid request method'})


def minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET.get('prod_id')
        user_cart = Cart.objects.filter(product=prod_id, user=request.user)
        
        if user_cart.exists():
            c = user_cart.first()
            c.quantity -= 1
            c.save()
            c.sub_total=c.product.our_price*c.quantity
            c.save()
            
            amount = 0
            cart_products = Cart.objects.filter(user=request.user)
            
            for p in cart_products:
                temp_amount = (p.quantity * p.product.our_price)
                amount += temp_amount

            data = {
                'quantity': c.quantity,
                'amount': amount,
                'sub_total':c.sub_total

            }
            return JsonResponse(data)
            
        
        # Handle case if the user doesn't have this product in the cart
        return JsonResponse({'error': 'Product not found in cart'})

    # Handle other HTTP methods if needed
    return JsonResponse({'error': 'Invalid request method'})

def remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET.get('prod_id')
        user_cart = Cart.objects.filter(product=prod_id, user=request.user)
        
        if user_cart.exists():
            c = user_cart.first()  # Considering only the first instance if multiple are found
            c.delete()
            
            amount = 0
            cart_products = Cart.objects.filter(user=request.user)
            
            for p in cart_products:
                temp_amount = (p.quantity * p.product.our_price)
                amount += temp_amount

            data = {
                'amount': amount
            }
            return JsonResponse(data)
        
        # Handle case if the user doesn't have this product in the cart
        return JsonResponse({'error': 'Product not found in cart'})

    # Handle other HTTP methods if needed
    return JsonResponse({'error': 'Invalid request method'})

def checkout(request):
    if request.user.is_authenticated:
        user=request.user
        my_address=address.objects.filter(user=user)
        cart_items=Cart.objects.filter(user=user)
        amount=0
        total_amount=0.0
        discount_amount=request.session.get('discount_amount', 0)
        cart_products=[p for p in Cart.objects.all() if p.user == request.user ]
        if cart_products:
            number_of_items=0
            for p in cart_products:
                tempamount=(p.quantity*p.product.our_price)
                total_amount+=tempamount
                number_of_items+=1
            amount=total_amount - discount_amount

        newly_added_address_id = request.session.get('newly_added_address_id')
        
        # Clear the session key to prevent it from being reused
        if newly_added_address_id:
            del request.session['newly_added_address_id']
        request.session['amount_to_pay']=amount
        #request.session['number_of_items']=number_of_items

        
        
    return render(request,'users/checkout.html',{'my_address':my_address,'amount':amount,'cart_items':cart_items,'discount_amount':discount_amount,'total_amount':total_amount,'newly_added_address_id': newly_added_address_id})

def payment_done(request):
    if request.user.is_authenticated:
        user=request.user
        
        if request.method == 'POST':
        
            cust_id=request.POST.get('custid')
            #customer=address.objects.get(id=cust_id)
            payment_method=request.POST.get('payment_method')
            cart=Cart.objects.filter(user=user)
        
        if not cust_id:
            return render(request,'users/checkout.html',{'error_message':'please select an address'})

        elif not payment_method:
            return render(request,'users/checkout.html',{'error_message':'please select payment option'})
        
        discount_amount=request.session.get('discount_amount',0.0)
        if discount_amount:
            del request.session['discount_amount']

        amount=request.session['amount_to_pay']

        customer=address.objects.get(id=cust_id)
        new_order=Order(user=user,address=customer,total_amount=amount,discount_amount=discount_amount)
        new_order.save()
        request.session['order_id']=new_order.id
        try:
            
            if payment_method=='cash':
                for c in cart:
                    if discount_amount!=0.0: 
                        OrderPlaced(order=new_order,user=user,address=customer,Product=c.product,discount_status=True,quantity=c.quantity,status='Accepted',payment_status='payment incomplete_COD').save()
                        c.delete()
                    else:
                        OrderPlaced(order=new_order,user=user,address=customer,Product=c.product,quantity=c.quantity,status='Accepted',payment_status='payment incomplete_COD').save()
                        c.delete()
                return redirect('success')
            elif payment_method=='online':
                for c in cart:
                    if discount_amount!=0.0:
                        OrderPlaced(order=new_order,user=user,address=customer,Product=c.product,discount_status=True,quantity=c.quantity,payment_status='payment incomplete').save()
                        new_order.payment_mode='online_payment'
                        new_order.save()
                    else:
                        OrderPlaced(order=new_order,user=user,address=customer,Product=c.product,quantity=c.quantity,payment_status='payment incomplete').save()
                        new_order.payment_mode='online_payment'
                        new_order.save()
        
        except address.DoesNotExist:
            return render(request,'users/checkout.html',{'error_message':'please select the address'})
        
        return redirect('choosepayment')
    return render(request,'users/checkout.html')

def my_orders(request):
    if request.user.is_authenticated:
        user=request.user
        discount_amount=request.session.get('discount_amount')
        print(discount_amount)
        placed_orders=OrderPlaced.objects.filter(user=user).order_by('-id')
    return render(request,'users/my_orders.html',{'placed_orders':placed_orders})

def cancel_order(request,uid):
    if request.user.is_authenticated:
        user=request.user
        order=OrderPlaced.objects.get(id=uid)
        #my_wallet=wallet.objects.get(user=user)
        if order.payment_status=='online_payment_done':
            order.status='requested for cancellation and refund'
            order.save()
            return redirect('myorders')
        elif order.payment_status=='payment incomplete_COD' or order.payment_status=='Cash on Delivery':
            order.status='requested for cancellation'
            order.save()
            return redirect('myorders')
    return render(request,'users/my_orders.html')

def return_order(request,uid):
    if request.user.is_authenticated:
        order=OrderPlaced.objects.get(id=uid)
        order.status='requested for return'
        order.save()
        return redirect('myorders')
    return render(request,'users/my_orders.html')


import razorpay
from django.http import HttpResponse

def choose_payment(request):
    user=request.user
    cart_items=Cart.objects.filter(user=user)
    amount=request.session.get('amount_to_pay', 0.0)
    print(amount)
    amount = math.floor(amount)
    print(amount)
    client=razorpay.Client(auth = (settings.RAZOR_KEY_ID,settings.RAZOR_KEY_SECRET) )
    payment=client.order.create({'amount': amount*100 , 'currency': 'INR', 'payment_capture':1})
    order_id=request.session['order_id']
    context={
        'payment':payment,
        'order_id':order_id
    }    
    return render(request,'users/choose_payment.html',context)

def success(request):
    print('------------------------------')
    print(request.GET['order_id'])
    # print(request.session['order_id'])
    print('------------------------------')
    # order_id=request.session['order_id']
    order_id=request.GET['order_id']
    print(order_id)
    main_order=Order.objects.get(id=order_id)
    user=request.user.id
    cart=Cart.objects.filter(user=user)
    for c in cart:   
        c.delete()
    online_orders=OrderPlaced.objects.filter(order=main_order,payment_status='payment incomplete')
    main_order=Order.objects.get(id=order_id)
    main_order.status='Accepted'
    main_order.save()
    print(online_orders)
    for orders in online_orders:
        orders.payment_status='online_payment_done'
        orders.status='Accepted'
        orders.save()
    return render(request, 'users/success_page.html',{'order_id':order_id})


def my_coupons(request):
    if request.user.is_authenticated:
        user=request.user
        all_coupons=Coupon.objects.all()
        used_coupons=UserCoupon.objects.filter(user=user,is_used=True)
        available_coupon_ids = used_coupons.values_list('coupon_id', flat=True)
        available_coupons=all_coupons.exclude(id__in=available_coupon_ids)
        context={
            'used_coupons':used_coupons,
            'available_coupons':available_coupons
        }
    return render(request,'users/my_coupons.html',context)

def my_wallet(request):
    if request.user.is_authenticated:
        user=request.user
        try:
            mywallet=wallet.objects.get(user=user)
        except wallet.DoesNotExist:
            mywallet=wallet.objects.create(user=user,balance_amount=0)
        return render(request,'users/my_wallet.html',{'mywallet':mywallet})
    

def invoice(request,order_id):
    # order_id=request.session['order_id']
    main_order=Order.objects.get(id=order_id)
    order_items=OrderPlaced.objects.filter(order=main_order)
    print(order_items)
    context={
        'order_items':order_items,
        'main_order':main_order
    }
    return render(request,'users/order_summary.html',context)

def orderpage_invoice(request,uid):
    main_order=Order.objects.get(id=uid)
    order_items=OrderPlaced.objects.filter(order=main_order)
    context={
        'order_items':order_items,
        'main_order':main_order
    }
    return render(request,'users/order_summary.html',context)

def render_to_pdf(template_path, context_dict):
    template = get_template(template_path)
    html = template.render(context_dict)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'

    # Create PDF
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

def invoice_pdf(request):
    order_id = request.session['order_id']
    main_order = Order.objects.get(id=order_id)
    order_items = OrderPlaced.objects.filter(order=main_order)
    context = {
        'order_items': order_items,
        'main_order': main_order
    }

    # Render PDF
    pdf = render_to_pdf('users/pdf_invoice_template.html', context)

    return pdf