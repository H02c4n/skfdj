from rest_framework import serializers
from parler_rest.serializers import TranslatableModelSerializer
from parler_rest.fields import TranslatedFieldsField
from .models import Category, Tag, Post

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug')

class TagSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Tag)

    class Meta:
        model = Tag
        fields = ('id', 'slug', 'translations')

class PostListSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Post)
    category = CategorySerializer(read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'slug', 'image', 'category', 'created_at', 'translations')

    def get_image(self, obj):
        if not obj.image:
            return None
        return obj.image.url

class PostDetailSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Post)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'slug', 'image', 'category', 'tags', 'created_at', 'updated_at', 'translations')

    def get_image(self, obj):
        if not obj.image:
            return None
        return obj.image.url