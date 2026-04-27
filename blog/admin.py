from django.contrib import admin
from parler.admin import TranslatableAdmin
from .models import Category, Tag, Post

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')

@admin.register(Tag)
class TagAdmin(TranslatableAdmin):
    list_display = ('name', 'slug')

@admin.register(Post)
class PostAdmin(TranslatableAdmin):
    list_display = ('title', 'slug', 'category', 'created_at')
    list_filter = ('category', 'tags', 'created_at')
    search_fields = ('translations__title', 'translations__content')
    filter_horizontal = ('tags',)