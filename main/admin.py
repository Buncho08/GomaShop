from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CartTable, CartDetailTable, ItemTable, OrderTable, OrderDetailTable

class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (_("重要な情報の編集"), {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("myouji", "namae","email", "icon", "post", "pref", "town","prefDetail", "points", "birthday", "gender", "mail_deriv")}),
        (_("Permissions"), 
            {
            "fields": (
                "is_active", "is_staff", "is_superuser","user_permissions"
                )
            }
        ),
        (_("Important dates"), {"fields": ("last_login",)}),
    )

    list_display = ("username", "pref", "gender", "myouji","namae","is_active", "is_superuser")

    search_fields = ("username", "gender", "pref")
    filter_horizontal = ("groups", "user_permissions")
    
    list_filter = ("pref","is_staff", "is_superuser", "is_active")

    ordering = ("username",)
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email","password1", "password2"),
            },
        ),
    )
CustomUser = get_user_model()
admin.site.register(CustomUser, CustomUserAdmin)

class CartAdmin(admin.ModelAdmin):
    list_display = ('cart_id', 'user_id', 'create', 'update', 'ordered')

class CartDetailAdmin(admin.ModelAdmin):
    list_display = ('detail_id', 'cart_id', 'item_id', 'quantity')

class ItemAdmin(admin.ModelAdmin):
    list_display = ('item_id', 'item_name', 'price', 'sale_flg')

class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'user_id', 'total_pay', 'ordered')

class OrderDetailAdmin(admin.ModelAdmin):
    list_display = ('detail_id', 'order_id', 'item_id')


admin.site.register(CartTable, CartAdmin)
admin.site.register(CartDetailTable, CartDetailAdmin)
admin.site.register(ItemTable, ItemAdmin)
admin.site.register(OrderTable, OrderAdmin)
admin.site.register(OrderDetailTable, OrderDetailAdmin)