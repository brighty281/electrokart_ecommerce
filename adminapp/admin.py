from django.contrib import admin
from .models import *
# Register your models here.
class Product_images(admin.TabularInline):
    model=MultipleImages
class Product_highlights(admin.TabularInline):
    model=ProductHighlights
class Product_additionalinfo(admin.TabularInline):
    model=AdditionalInfo
class Product_Admin(admin.ModelAdmin):
    inlines=(Product_images,Product_highlights,Product_additionalinfo)

admin.site.register(MainCategory)
admin.site.register(SubCategory)
admin.site.register(Product,Product_Admin)
admin.site.register(MultipleImages)
admin.site.register(CustomerInfo)
admin.site.register(ProductHighlights)
admin.site.register(AdditionalInfo)
admin.site.register(Cart)
admin.site.register(address)
admin.site.register(OrderPlaced)
admin.site.register(Coupon)
admin.site.register(UserCoupon)
admin.site.register(wallet)
admin.site.register(Order)