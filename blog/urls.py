from django.urls import path
from .views import PostListView, PostDetailView, CategoryListView, TagListView

app_name = 'blog'

urlpatterns = [
    path('posts/', PostListView.as_view(), name='post-list'),
    path('posts/<slug:slug>/', PostDetailView.as_view(), name='post-detail'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('tags/', TagListView.as_view(), name='tag-list'),
]