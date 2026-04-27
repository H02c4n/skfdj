from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from .models import Post, Category, Tag
from .serializers import PostListSerializer, PostDetailSerializer, CategorySerializer, TagSerializer
from .filters import PostFilter
from core.permissions import IsAdminOrReadOnly

class PostListView(generics.ListAPIView):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostListSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = PostFilter
    search_fields = ['translations__title', 'translations__content']

class PostDetailView(generics.RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostDetailSerializer
    lookup_field = 'slug'

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

class TagListView(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]