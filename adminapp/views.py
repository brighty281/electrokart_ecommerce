import datetime
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.checks import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,login,logout
from django.db.models import Q
from django.contrib import messages
import re
from . models import MainCategory, SubCategory, Product, MultipleImages, CustomerInfo, OrderPlaced, address, STATUS_CHOICE, ProductHighlights, AdditionalInfo, Coupon, UserCoupon,Order, wallet
from django.views.decorators.cache import never_cache
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta, time
from django.db.models import F, Sum, Count
#from . forms import ProductForm, ImageForm

# Create your views here.


@never_cache
def admin_home(request):
    if request.user.is_anonymous and not request.user.is_superuser:
        return redirect('admin_login')
    else:
        total_orders=OrderPlaced.objects.exclude(status__in=['Cancelled', 'Pending']).count()
        total_products=Product.objects.all().count()
        all_orders=Order.objects.all()
        total_revenue=0
        for order in all_orders:
            total_revenue +=order.total_amount

        print(total_revenue)
        total_customers=User.objects.filter(is_active=True).count()
        total_delivered=OrderPlaced.objects.filter(status='delivered').count()
        total_returned=OrderPlaced.objects.filter(status='returned').count()
        total_cancelled=OrderPlaced.objects.filter(status='Cancelled').count()
        total_requests = OrderPlaced.objects.filter(status__in=['requested for cancellation', 'requested for cancellation and refund', 'requested for return']).count()

        all_users=User.objects.filter(is_active=True)[:4]
        orders_list=Order.objects.all().order_by('-id')[:5]
        context={
            'total_orders':total_orders,
            'total_products':total_products,
            'total_revenue':total_revenue,
            'total_customers':total_customers,
            'total_delivered':total_delivered,
            'total_returned':total_returned,
            'total_cancelled':total_cancelled,
            'total_requests':total_requests,
            'all_users':all_users,
            'orders_list':orders_list
        }
    return render(request,'myadmin/index.html',context)

@never_cache
def admin_login(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('admin_home')
    if request.method == 'POST':
        uname = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=uname, password=password)

        if user is not None and user.is_superuser and user.is_active:
            print(user.is_superuser)
            request.session['super_user']=uname
            login(request, user)
            return redirect('admin_home')
            
        else:
            messages.error(request, "Invalid credentials. Please Try again.")
            return redirect('admin_login')
    return render(request,'myadmin/adminlogin.html')


@never_cache
def admin_logout(request):
    if request.user.is_authenticated and request.user.is_superuser:
        request.session.flush()
        logout(request)
        return redirect('admin_login')
    else:
        messages.info(request, "Please log in as admin")
        return render(request,'myadmin/adminlogin.html')


@never_cache    
def user_list(request):
     if request.user.is_authenticated and request.user.is_superuser:
        result = User.objects.all().exclude(username='admin')
        return render(request,'myadmin/user_list.html',{'users':result})
     else:
         messages.info(request, "Please log in as admin")
         return render(request,'myadmin/adminlogin.html')
     
@never_cache
def edit_user(request,uid):
    if request.user.is_authenticated and request.user.is_superuser:
        user=User.objects.get(id=uid)
        my_customer=CustomerInfo.objects.get(user=user)
        if request.method=='POST':
            new_username=request.POST['username']
            new_email=request.POST['email']
            new_firstname=request.POST['fname']
            new_lastname=request.POST['lname']
            new_phone=request.POST['phone']
            useractive=request.POST['user_status']

            try:
                existing_user_with_username = User.objects.get(username=new_username)
                if existing_user_with_username != user:
                    messages.error(request, "Username already exists")
                    return redirect('edituser', uid=uid)
            except User.DoesNotExist:
                pass

            try:
                existing_user_with_email = User.objects.get(email=new_email)
                if existing_user_with_email != user:
                    messages.error(request, "Email already exists")
                    return redirect('edituser', uid=uid)
            except User.DoesNotExist:
                pass

            if useractive=='activate':
                user.is_active=True
                my_customer.user_active=True
                
            elif useractive=='inactivate':
                user.is_active=False
                my_customer.user_active=False
            
            user.save()
            my_customer.save()

            user.username = new_username
            user.email = new_email
            my_customer.user_email=user.email
            my_customer.first_name=new_firstname
            my_customer.last_name=new_lastname
            my_customer.phone=new_phone

            #try:
            user.save()
            my_customer.save()
            # except Exception as e:
            #     print(f"Error while saving user: {e}")

            return redirect('userslist')
        context={
            'user': user,
            'my_customer':my_customer
        }


        return render(request,'myadmin/edituser.html',context)
    else:
        messages.info(request, "Please log in as admin")
        return render(request, 'myadmin/adminlogin.html')


@never_cache
def delete_user(request,uid):
    if request.user.is_authenticated and request.user.is_superuser:
        user = User.objects.get(id=uid)
        user.delete()
        return redirect('userslist')
    else:
        messages.info(request, "Please log in as admin")
        return render(request,'myadmin/adminlogin.html')


@never_cache
def add_user(request):
    if request.user.is_authenticated and request.user.is_superuser:
        if request.method=='POST':
            username=request.POST.get('username')
            email=request.POST.get('email')
            password=request.POST.get('pass1')
            try:
                if User.objects.get(username=username):
                    messages.error(request, "Username already exists")
                    return redirect("adduser")
            except:
                pass

            try:
                if User.objects.get(email=email):
                    messages.error(request, "Email already exists")
                    return redirect("adduser")
            except:
                pass

            if not re.match(r'^[\w.@+-]+$', username):
                messages.error(request, "Invalid username")
                return redirect("adduser")

            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                messages.error(request, "Invalid email")
                return redirect("adduser")

            if len(password) < 8:
                messages.error(request, "Password must be at least 8 characters")
                return redirect("adduser")

            user=User.objects.create_user(username,email,password)
            user.save()
            if user is not None:
                messages.success(request, "User added successfully")
                return redirect('userslist')
            else:
                return render(request,'myadmin/adduser.html')
        return render(request,'myadmin/adduser.html')

    else:
        messages.info(request, "Please log in as admin")
        return render(request,'myadmin/adminlogin.html')
    

@never_cache
def maincat_list(request):
    if request.user.is_authenticated and request.user.is_superuser:
        main_category = MainCategory.objects.all()
        context={
            'main_category':main_category
        }
        return render(request, 'myadmin/categorymgmt.html',context)
    else:
        messages.info(request, "Please log in as admin")
        return render(request,'myadmin/adminlogin.html')

@never_cache    
def edit_maincat_list(request,uid):
    if request.user.is_authenticated and request.user.is_superuser:
        main_category = get_object_or_404(MainCategory, id=uid)
        if request.method=='POST':
            new_catname=request.POST['catname']

            
            existing_user_with_catname = MainCategory.objects.exclude(id=uid).filter(name=new_catname)
            if existing_user_with_catname:
                messages.error(request, "category already exists")
                return redirect('editmaincatlist', uid=uid)
            

            main_category.name = new_catname
            
            try:
                main_category.save()
                messages.success(request, "Category updated successfully")
            except Exception as e:
                print(f"Error while saving user: {e}")

            return redirect('maincat_list')
        
        

        return render(request,'myadmin/edit_maincat_list.html',{'main_category':main_category})
    else:
        messages.info(request, "Please log in as admin")
        return render(request, 'myadmin/edit_maincat_list.html')
    
def delete_maincat_list(request,uid):
    if request.user.is_authenticated and request.user.is_superuser:
        main_category = MainCategory.objects.get(id=uid)
        main_category.delete()
        return redirect('maincat_list')
    else:
        messages.info(request, "Please log in as admin")
        return render(request,'myadmin/adminlogin.html')
    

def add_maincat_list(request):
    if request.user.is_authenticated and request.user.is_superuser:

        if request.method=='POST':
            catname=request.POST.get('catname')

            if MainCategory.objects.filter(name=catname).exists():
                messages.error(request, "Category already exists")
                return redirect("addmaincatlist")
            
            main_category=MainCategory(name=catname)
            main_category.save()
            
            messages.success(request, "Category added successfully")
            return redirect("maincat_list")
        
        return render(request, 'myadmin/add_maincat_list.html')
    else:
        messages.info(request, "Please log in as admin")
        return redirect('adminlogin') 

def brand_list(request,uid):
    if request.user.is_authenticated and request.user.is_superuser:
        main_category=MainCategory.objects.get(pk=uid)
        sub_category=SubCategory.objects.filter(main_category=main_category)
        context={
            'main_category':main_category,
            'sub_category':sub_category
        }
        if request.method=='POST':
            brandname=request.POST.get('brandname')

            if SubCategory.objects.filter(main_category=main_category,name=brandname).exists():
                messages.error(request, "Category already exists")
                return redirect("brandlist")
            
            sub_category=SubCategory(main_category=main_category,name=brandname)
            sub_category.save()
            
            messages.success(request, "brand added successfully")
            return redirect("brandlist",uid=uid)

        return render(request,'myadmin/brand_list.html',context)
    else:
        messages.info(request, "Please log in as admin")
        return redirect('adminlogin') 

def edit_subcat_list(request,uid):
    if request.user.is_authenticated and request.user.is_superuser:
        sub_category = get_object_or_404(SubCategory, id=uid)
        main_category_id = sub_category.main_category_id
        if request.method=='POST':
            new_brandname=request.POST.get('brandname')

            existing_subcategory=SubCategory.objects.filter(name=new_brandname).exclude(id=uid).first()
            if existing_subcategory:
                messages.error(request, "category already exists")
                return redirect('editsubcatlist', uid=uid)
            
            else:
                sub_category.name = new_brandname
                sub_category.save()
                messages.success(request, "brand added successfully")
                return redirect('brandlist',uid=main_category_id)
            
        return render(request,'myadmin/edit_subcat_list.html',{'sub_category':sub_category})
    else:
        messages.info(request, "Please log in as admin")
        return render(request, 'myadmin/adminlogin.html')
    
def delete_subcat_list(request,uid):
    if request.user.is_authenticated and request.user.is_superuser:
        sub_category=SubCategory.objects.get(id=uid)
        main_id=sub_category.main_category_id
        sub_category.delete()
        return redirect('brandlist',uid=main_id)
    else:
        messages.info(request, "Please log in as admin")
        return render(request,'myadmin/adminlogin.html')
    
def add_product(request):
    if request.user.is_authenticated and request.user.is_superuser:
        main_category=MainCategory.objects.all()
        if request.method == 'POST':
            main_category_id = request.POST.get('main_category')
            title = request.POST.get('title')
            base_name=request.POST.get('base_name')
            our_price = request.POST.get('our_price')
            real_price = request.POST.get('real_price')
            description = request.POST.get('description')
            main_img = request.FILES.get('main_img')
            images = request.FILES.getlist('images')
            highlights = request.POST.getlist('highlights[]')
            additional_feature=request.POST.getlist('features[]')
            addtional_featureinfo=request.POST.getlist('feature_descriptions[]')

            product = Product.objects.create(
            main_category_id=main_category_id,
            title=title,
            base_name=base_name,
            our_price=our_price,
            real_price=real_price,
            description=description,
            main_img=main_img
            )
            
            for img in images:
                MultipleImages.objects.create(product=product, images=img)
            
            for highlight in highlights:
                ProductHighlights.objects.create(product=product, highlight=highlight)

            for feature, description in zip(additional_feature, addtional_featureinfo):
                AdditionalInfo.objects.create(product=product, feature=feature, feature_description=description)


            return redirect('product_list')
        return render(request,'myadmin/add_product.html',{'main_category': main_category})
     
    

def product_list(request):
    if request.user.is_authenticated and request.user.is_superuser:
        my_products=Product.objects.all()
        context={
            'my_products':my_products
        }
        return render(request,'myadmin/page-products-list.html',context)
    else:
        messages.info(request, "Please log in as admin")
        return redirect('adminlogin')
    
def edit_product(request, uid):
    if request.user.is_authenticated and request.user.is_superuser:
        my_product = get_object_or_404(Product, id=uid)
        main_category = MainCategory.objects.all()
        existing_highlights = ProductHighlights.objects.filter(product=my_product)
        existing_additional_info = AdditionalInfo.objects.filter(product=my_product)
        
        if request.method == 'POST':
            new_main_category_id = request.POST.get('main_category')
            new_title = request.POST.get('title')
            new_our_price = request.POST.get('our_price')
            new_real_price = request.POST.get('real_price')
            new_description = request.POST.get('description')
            new_main_img = request.FILES.get('main_img')
            status= request.POST.get('status')
            new_images = request.FILES.getlist('images')

            if status=='active':
                my_product.product_active=True
                my_product.save()
            elif status=='disable':
                my_product.product_active=False
                my_product.save()
            
            
            
            new_main_category=MainCategory.objects.get(id=new_main_category_id)
            # Update product fields
            my_product.main_category = new_main_category
            my_product.title = new_title
            my_product.our_price = new_our_price
            my_product.real_price = new_real_price
            my_product.description = new_description
            
            if new_main_img:
                my_product.main_img = new_main_img

            my_product.save()

            # Clear previous images and add new ones
            #my_product.multipleimages_set.all().delete()
            for img in new_images:
                MultipleImages.objects.create(product=my_product, images=img)
            
            my_product.producthighlights_set.all().delete()  # Delete existing highlights
            new_highlights = request.POST.getlist('highlights[]')
            for highlight in new_highlights:
                ProductHighlights.objects.create(product=my_product, highlight=highlight)

            # Update additional information
            my_product.additionalinfo_set.all().delete()  # Delete existing additional info
            new_additional_features = request.POST.getlist('features[]')
            new_additional_feature_info = request.POST.getlist('feature_descriptions[]')
            for feature, description in zip(new_additional_features, new_additional_feature_info):
                AdditionalInfo.objects.create(product=my_product, feature=feature, feature_description=description)

            return redirect('product_list')

        
        context = {
            'my_product': my_product,
            'main_category': main_category,
            'existing_highlights': existing_highlights,
            'existing_additional_info': existing_additional_info,
        }
        return render(request, 'myadmin/edit_product.html', context)


def delete_product(request,uid):
    if request.user.is_authenticated and request.user.is_superuser:
        my_product=Product.objects.get(id=uid)
        my_product.delete()
        return redirect('product_list')
    else:
        messages.info(request, "Please log in as admin")
        return render(request,'myadmin/adminlogin.html')
    

def orders_list(request):
    if request.user.is_authenticated and request.user.is_superuser:
        all_orders=OrderPlaced.objects.all().order_by('-id')
        status_choice=STATUS_CHOICE
        return render(request,'myadmin/orders_list.html',{'all_orders':all_orders, 'status_choice':status_choice})

def edit_orderlist(request,uid):
    if request.user.is_authenticated and request.user.is_superuser:
        my_order=OrderPlaced.objects.get(id=uid)
        all_products=Product.objects.all()
        all_users=User.objects.all()
        all_address=address.objects.all()
        status_choice=STATUS_CHOICE
        context={
            'my_order':my_order,
            'all_products':all_products,
            'all_users':all_users,
            'all_address':all_address,
            'status_choices':status_choice
        }
        if request.method=='POST':
            new_user_id=request.POST.get('user')       #getting ids and assigning
            new_product_id=request.POST.get('product')
            new_address_id=request.POST.get('address')
            new_quantity=request.POST.get('quantity')
            new_status=request.POST.get('status')
            new_deliverydate=request.POST.get('delivery_date')

            new_user=User.objects.get(id=new_user_id)         #getting objects using ids
            new_product=Product.objects.get(id=new_product_id)
            new_address=address.objects.get(id=new_address_id)
            
            my_order.user=new_user              #assigning new objects
            my_order.Product=new_product
            my_order.address=new_address
            my_order.quantity=new_quantity
            my_order.status=new_status
            my_order.delivery_date=new_deliverydate
            my_order.save()
            return redirect('orders_list')

        return render(request,'myadmin/edit_orderlist.html',context)

def add_order(request):
    if request.user.is_authenticated and request.user.is_superuser:
        all_products=Product.objects.all()
        all_users=User.objects.all()
        all_address=address.objects.all()
        status_choice=STATUS_CHOICE
        context={
            
            'all_products':all_products,
            'all_users':all_users,
            'all_address':all_address,
            'status_choices':status_choice,
            

        }
        if request.method=='POST':
            new_user_id=request.POST.get('user')       #getting ids and assigning
            new_product_id=request.POST.get('product')
            new_address_id=request.POST.get('address')
            new_quantity=request.POST.get('quantity')
            new_status=request.POST.get('status')

            new_user=User.objects.get(id=new_user_id)         #getting objects using ids
            new_product=Product.objects.get(id=new_product_id)
            new_address=address.objects.get(id=new_address_id)

            new_order=OrderPlaced.objects.create(
                user=new_user,
                Product=new_product,
                address=new_address,
                quantity=new_quantity,
                status=new_status
                
            )
            return redirect('orders_list')

    return render(request,'myadmin/add_orders.html',context)

def delete_order(request,uid):
    if request.user.is_authenticated and request.user.is_superuser:
        myorder=OrderPlaced.objects.get(id=uid)
        myorder.delete()
        return redirect('orders_list')
    return render(request,'myadmin/orders_list.html')
    
def order_details(request, uid):
    if request.user.is_authenticated and request.user.is_superuser:
        myorder = OrderPlaced.objects.get(id=uid)
        user = myorder.user
        my_wallet = None  # Default value
        try:
            my_wallet = wallet.objects.get(user=user)
        except wallet.DoesNotExist:
            my_wallet = wallet.objects.create(user=user, balance_amount=0)
    return render(request, 'myadmin/page-orders-detail.html', {'myorder': myorder, 'my_wallet': my_wallet})


def cancel_order_with_refund(request,uid):
    if request.user.is_authenticated and request.user.is_superuser:
        my_order=OrderPlaced.objects.get(id=uid)
        user=my_order.user
        my_wallet=wallet.objects.get(user=user)
        if my_order.status=='requested for cancellation':
            my_order.status='Cancelled'
            my_order.save()
            return redirect('orders_list')
        elif my_order.status=='requested for cancellation and refund':
            my_order.status='Cancelled'
            my_order.save()
            refund_amount=my_order.Product.our_price
            print(refund_amount)
            my_wallet.balance_amount=my_wallet.balance_amount+refund_amount
            my_wallet.save()
            print(my_wallet.balance_amount)
            #my_wallet.balance_amount
            return redirect('orders_list')
    return render(request,'myadmin/page-orders-detail.html',{'my_order':my_order, 'my_wallet':my_wallet})


def search_orderlist(request):
    if request.user.is_authenticated and request.user.is_superuser:
        all_orders=OrderPlaced.objects.all()
        query=request.GET.get('search')
        if query:
            result=all_orders.filter(Q(id__icontains=query) | Q(address__name__icontains=query))
        
        return render(request,'myadmin/search_orderlist.html',{'result':result})

def filter_orderlist(request):
    if request.user.is_authenticated and request.user.is_superuser:
        all_orders=OrderPlaced.objects.all()
        my_option=request.GET.get('status')
        if my_option:
            result=all_orders.filter(status=my_option)
        
        return render(request,'myadmin/search_orderlist.html',{'result':result})

def coupon_list(request):
    if request.user.is_authenticated and request.user.is_superuser:
        coupon_list=Coupon.objects.all()
    return render(request,'myadmin/coupon_list.html',{'coupon_list':coupon_list})

def add_coupon(request):
    if request.user.is_authenticated and request.user.is_superuser:
        if request.method == 'POST':
            code = request.POST.get('code')
            discount = request.POST.get('discount')
            valid_from = request.POST.get('valid_from')
            valid_to = request.POST.get('valid_to')
            status = request.POST.get('status')

            # Convert string inputs to appropriate types
            discount = float(discount)
            

            # Convert status string to boolean
            if status=='active':
                is_active=True
            else:
                is_active=False

            # Create Coupon object and save it
            coupon = Coupon(
                code=code,
                discount=discount,
                valid_from=valid_from,
                valid_to=valid_to,
                active=is_active  # Set the active field to the boolean value
            )
            coupon.save()
            return redirect('couponlist')
    
    return render(request, 'myadmin/add_coupon.html')

def edit_coupon(request,uid):
    if request.user.is_authenticated and request.user.is_superuser:
        my_coupon=Coupon.objects.get(id=uid)
        if request.method == 'POST':
            code = request.POST.get('code')
            discount = request.POST.get('discount')
            valid_from = request.POST.get('valid_from')
            valid_to = request.POST.get('valid_to')
            status = request.POST.get('status')

            # Convert string inputs to appropriate types
            discount = float(discount)
            
            # Convert status string to boolean
            if status=='active':
                is_active=True
            else:
                is_active=False
            
            my_coupon.code=code
            my_coupon.discount=discount
            my_coupon.valid_from=valid_from
            my_coupon.valid_to=valid_to
            my_coupon.active=is_active
            my_coupon.save()
            return redirect('couponlist')

    return render(request,'myadmin/edit_coupon.html',{'my_coupon':my_coupon})

def delete_coupon(request,uid):
    if request.user.is_authenticated and request.user.is_superuser:
        my_coupon=Coupon.objects.get(id=uid)
        my_coupon.delete()
        return redirect('couponlist')
    return render(request,'myadmin/coupon_list.html')

def userslist_coupon(request):
    if request.user.is_authenticated and request.user.is_superuser:
        users=User.objects.all()
    return render(request,'myadmin/userslist_coupon.html',{'users':users})

def my_couponlist(request,uid):
    if request.user.is_authenticated and request.user.is_superuser:
        request.session['userid']=uid
        user=User.objects.get(id=uid)
        my_coupons=UserCoupon.objects.filter(user=user)
    return render(request,'myadmin/my_couponlist.html',{'my_coupons':my_coupons,'user':user})

def edit_mycoupon(request,uid):
    if request.user.is_authenticated and request.user.is_superuser:
        my_coupon=UserCoupon.objects.get(id=uid)
        userid=request.session['userid']
        if request.method=='POST':
            status = request.POST.get('status')
            
            if status=='used':
                is_used=True
            else:
                is_used=False
            
            my_coupon.is_used=is_used
            my_coupon.save()
            return redirect('my_couponlist',userid)
                
    return render(request,'myadmin/edit_mycoupon.html',{'my_coupon':my_coupon})

def add_mycoupon(request):
    if request.user.is_authenticated and request.user.is_superuser:
        userid=request.session['userid']
        user=User.objects.get(id=userid)
        all_coupons=Coupon.objects.all()
        if request.method=='POST':
            status = request.POST.get('status')
            coupon_id = request.POST.get('code')
            if status=='active':
                active=True
            else:
                active=False
            
            couponobj=Coupon.objects.get(id=coupon_id)
            user_coupon=UserCoupon(
                coupon=couponobj,
                user=user,
                is_active=active
            )
            user_coupon.save()
            return redirect('my_couponlist', userid)

    return render(request,'myadmin/add_mycoupon.html',{'all_coupons':all_coupons})

def delete_mycoupon(request,uid):
    if request.user.is_authenticated and request.user.is_superuser:
        my_coupon=UserCoupon.objects.get(id=uid)
        userid=request.session['userid']
        my_coupon.delete()
        return redirect('my_couponlist', userid)
    return render(request,'myadmin/my_couponlist.html')


def week_sales(request):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    #total_sales = OrderPlaced.objects.filter(status='Accepted',ordered_date__range=(start_date, end_date)).aggregate(
        #total_sales=Sum('total_cost'))['total_sales'] or 0
    total_sales = OrderPlaced.objects.filter(status='delivered',ordered_date__range=(start_date, end_date)).annotate(total_cost=F('quantity') * F('Product__our_price')).aggregate(total_sales=Sum('total_cost'))['total_sales'] or 0
    total_orders = OrderPlaced.objects.filter(ordered_date__range=(start_date, end_date)).count()
    success_orders = OrderPlaced.objects.filter(status='delivered', ordered_date__range=(start_date, end_date)).count()
    delivered_products = OrderPlaced.objects.filter(status='delivered'
                                                  ,ordered_date__range=(start_date, end_date)
                                                  ).values('Product__title').annotate(total_quantity_sold=Sum('quantity')
                                                  ,total_revenue=Sum(F('quantity') * F('Product__our_price'))).order_by('-total_quantity_sold')
    order_products = OrderPlaced.objects.filter(ordered_date__range=(start_date, end_date)).order_by(
        '-ordered_date')
    print(order_products)
    date = end_date.strftime("%Y-%m-%d")
    print(date)
    context={
        'total_sales': total_sales,
        'total_orders': total_orders,
        'delivered_products':delivered_products,
        'order_products':order_products,
        'success_orders':success_orders,
        'date': date
    }
    return render(request,'myadmin/weekly_sales.html',context)

def today_sales(request):
    current_datetime = datetime.now()
    current_day = current_datetime.strftime('%d')

    start_date = datetime.combine(current_datetime.date(), time.min)
    end_date = current_datetime

    total_sales = OrderPlaced.objects.filter(status='delivered',ordered_date__range=(start_date, end_date)).annotate(total_cost=F('quantity') * F('Product__our_price')).aggregate(total_sales=Sum('total_cost'))['total_sales'] or 0
    total_orders = OrderPlaced.objects.filter(ordered_date__range=(start_date, end_date)).count()
    success_orders = OrderPlaced.objects.filter(status='delivered', ordered_date__range=(start_date, end_date)).count()
    delivered_products = OrderPlaced.objects.filter(status='delivered'
                                                  ,ordered_date__range=(start_date, end_date)
                                                  ).values('Product__title').annotate(total_quantity_sold=Sum('quantity')
                                                  ,total_revenue=Sum(F('quantity') * F('Product__our_price'))).order_by('-total_quantity_sold')
    order_products = OrderPlaced.objects.filter(ordered_date__range=(start_date, end_date)).order_by(
        '-ordered_date')
    print(order_products)
    Month = end_date.month
    date = end_date.strftime("%d-%m-%Y")
    print(date)
    context={
        'total_sales': total_sales,
        'total_orders': total_orders,
        'delivered_products':delivered_products,
        'order_products':order_products,
        'current_day': current_day,
        'current_datetime': current_datetime,
        'success_orders': success_orders,
        'month': Month,
        'date':date
    }
    return render(request,'myadmin/today_sales.html',context)

def current_year_sales(request):
    current_year = datetime.now().year
    start_date = datetime(current_year, 1, 1)
    end_date = datetime.now()
    total_sales = OrderPlaced.objects.filter(status='delivered',ordered_date__range=(start_date, end_date)).annotate(total_cost=F('quantity') * F('Product__our_price')).aggregate(total_sales=Sum('total_cost'))['total_sales'] or 0
    total_orders = OrderPlaced.objects.filter(ordered_date__range=(start_date, end_date)).count()
    success_orders = OrderPlaced.objects.filter(status='delivered', ordered_date__range=(start_date, end_date)).count()
    delivered_products = OrderPlaced.objects.filter(status='delivered'
                                                  ,ordered_date__range=(start_date, end_date)
                                                  ).values('Product__title').annotate(total_quantity_sold=Sum('quantity')
                                                  ,total_revenue=Sum(F('quantity') * F('Product__our_price'))).order_by('-total_quantity_sold')
    order_products = OrderPlaced.objects.filter(ordered_date__range=(start_date, end_date)).order_by(
        '-ordered_date')
    print(order_products)
    context={
        'total_sales': total_sales,
        'total_orders': total_orders,
        'success_orders': success_orders,
        'delivered_products': delivered_products,
        'current_year': current_year,
        'order_products': order_products,
    }
    return render(request, 'myadmin/current_year_sales.html',context)