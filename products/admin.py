from django.contrib import admin

# Register your models here.
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)} # Automatically generate slug from name

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'price', 'available', 'created', 'updated', 'featured']
    list_filter = ['available', 'created', 'updated', 'featured']
    list_editable = ['price', 'available', 'featured'] # Allows editing directly from list view
    prepopulated_fields = {'slug': ('name',)}
    raw_id_fields = ['category'] # For selecting category, better for many categoriess