from django.contrib import admin

# Register your models here.

# Register your models here.
from .models import*

admin.site.register(User)

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Cart)
admin.site.register(CartItem)


