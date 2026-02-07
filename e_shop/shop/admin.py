from django.contrib import admin
from .models import Catagory, OrderItem, Product, Ratting, Cart, Order,CartItem

# Register your models here.
@admin.register(Catagory)
class CatagoryAdmin(admin.ModelAdmin):
    list_display =['name','slug']
    prepopulated_fields = {'slug': ('name',)}

class RattingInline(admin.TabularInline):
    model = Ratting
    extra = 0
    readonly_fields = ['user', 'rating', 'review', 'created']    

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'catagory', 'price', 'stock', 'available', 'created', 'updated']
    list_filter = ['available', 'created', 'updated', 'catagory']
    list_editable = ['price', 'stock', 'available']
    prepopulated_fields = {'slug': ('name',)}     
    inlines = [RattingInline]

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
  

@admin.register(Cart)    
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'created', 'updated']
    inlines = [CartItemInline]

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user','first_name', 'last_name', 'email', 'paid', 'created','status']
    list_filter = ['paid', 'created', 'status']
    search_fields = ['first_name', 'last_name', 'email']
    inlines = [OrderItemInline]

@admin.register(Ratting)
class RattingAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'created']
    list_filter = ['rating', 'created']
   