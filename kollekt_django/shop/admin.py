from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Category, Order, Product, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Contact", {"fields": ("phone",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("Contact", {"fields": ("phone",)}),)
    list_display = ("username", "phone", "email", "is_staff", "date_joined")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "ordered_count", "stock", "arrival_date", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product", "quantity", "unit_price", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "user__phone", "product__name")
