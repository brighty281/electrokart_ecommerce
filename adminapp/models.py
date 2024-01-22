from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone 
# Create your models here.
class CustomerInfo(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    first_name=models.CharField(max_length=100, default=None, null=True)
    last_name=models.CharField(max_length=100, default=None, null=True)
    phone=models.BigIntegerField(default=None, null=True)
    user_email=models.EmailField(default=None, null=True)
    user_password=models.CharField(max_length=100, default=None, null=True)
    user_active=models.BooleanField(default=True)

class address(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    name=models.CharField(max_length=100)
    house_name=models.CharField(max_length=100)
    locality=models.CharField(max_length=100)
    city=models.CharField(max_length=100)
    zipcode=models.PositiveBigIntegerField()
    state=models.CharField(max_length=100)

    def __str__(self):
        return f'{self.name} - {self.city}'

class MainCategory(models.Model):
    name=models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class SubCategory(models.Model):
    main_category=models.ForeignKey(MainCategory,on_delete=models.CASCADE)
    name=models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Product(models.Model):
    main_category=models.ForeignKey(MainCategory,on_delete=models.CASCADE) 
    title=models.CharField(max_length=100)
    our_price=models.FloatField()
    real_price=models.FloatField()
    description = models.TextField()
    main_img=models.ImageField(upload_to='main_imgs/')
    product_active=models.BooleanField(default=True)
    base_name=models.CharField(max_length=50,null=True,blank=True)
    variant_feature=models.CharField(max_length=50,null=True,blank=True)
    stock=models.PositiveBigIntegerField(default=10)
    def __str__(self):
        return self.title

    
class MultipleImages(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    images=models.ImageField(upload_to='main_imgs/')
    
    def __str__(self):
        return self.product.title
 
class ProductHighlights(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    highlight=models.CharField(max_length=200,null=True,blank=True)

    def __str__(self):
        return self.product.title

class AdditionalInfo(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    feature=models.CharField(max_length=50,null=True,blank=True)
    feature_description=models.CharField(max_length=200,null=True,blank=True)
    
    def __str__(self):
        return self.product.title

class Cart(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity=models.PositiveBigIntegerField(default=1)
    sub_total=models.PositiveBigIntegerField(default=0)
    is_paid=models.BooleanField(default=False)
    razor_pay_order_id=models.CharField(max_length=100, null=True, blank=True)
    razor_pay_payment_id=models.CharField(max_length=100,null=True, blank=True)
    razor_pay_payment_signature=models.CharField(max_length=100,null=True,blank=True)


    def __str__(self):
        return self.user.username
    @property
    def total_cost(self):
        return self.quantity * self.product.our_price
    def save(self, *args, **kwargs):
        self.sub_total = self.total_cost  # Calculate subtotal based on quantity and product price
        super(Cart, self).save(*args, **kwargs)
STATUS_CHOICE=(
    ('pending','pending'),
    ('Accepted','Accepted'),
    ('Packed','Packed'),
    ('On the way','On the way'),
    ('delivered','delivered'),
    ('Cancelled','Cancelled'),
    ('requested for cancellation','requested for cancellation'),
    ('requested for cancellation and refund','requested for cancellation and refund'),
    ('requested for return','requested for return'),
    ('returned','returned')
    
)

class Order(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    address=models.ForeignKey(address,on_delete=models.CASCADE)
    total_amount=models.PositiveBigIntegerField(default=0)
    discount_amount=models.PositiveBigIntegerField(default=0)
    status=models.CharField(max_length=50,choices=STATUS_CHOICE,default='pending')
    ordered_date=models.DateTimeField(auto_now_add=True)
    payment_mode=models.CharField(max_length=100,default='Cash on Delivery')
    
    def original_price(self):
        return self.total_amount + self.discount_amount


class OrderPlaced(models.Model):
    order=models.ForeignKey(Order,on_delete=models.CASCADE)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    address=models.ForeignKey(address,on_delete=models.CASCADE)
    Product=models.ForeignKey(Product,on_delete=models.CASCADE)
    ordered_date=models.DateTimeField(auto_now_add=True)
    delivery_date = models.DateTimeField(null=True, blank=True)
    quantity = models.PositiveBigIntegerField(default=1)
    status=models.CharField(max_length=50,choices=STATUS_CHOICE,default='pending')
    discount_status=models.BooleanField(default=False)
    payment_status=models.CharField(max_length=100,default='Cash on Delivery')
    def save(self, *args, **kwargs):
        if not self.ordered_date:
            self.ordered_date = timezone.now()  # Assuming you're using Django's timezone
        if not self.delivery_date:
            self.delivery_date = self.ordered_date + timedelta(days=3)
        super().save(*args, **kwargs)
    @property
    def total_cost(self):
        return self.quantity * self.Product.our_price


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    active = models.BooleanField(default=True)

    def is_valid(self):
        return self.valid_from <= timezone.now() <= self.valid_to and self.active

    def __str__(self):
        return self.code


class UserCoupon(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    coupon=models.ForeignKey(Coupon,on_delete=models.CASCADE)
    is_used=models.BooleanField(default=True)

    def __str__(self):
        return f'{self.user} - {self.coupon}'

class wallet(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    balance_amount=models.PositiveBigIntegerField(default=0)

    def __str__(self):
        return self.user.username
