from rest_framework import serializers
from .models import SiteSettings, BoardMember

class SiteSettingsSerializer(serializers.ModelSerializer):
    mission = serializers.SerializerMethodField()
    vision = serializers.SerializerMethodField()
    short_description = serializers.SerializerMethodField()

    logo = serializers.SerializerMethodField()
    hero_background = serializers.SerializerMethodField()

    class Meta:
        model = SiteSettings
        fields = [
            'id', 'organization_name', 'org_number', 'logo', 'email', 'phone',
            'address', 'website', 'facebook', 'instagram', 'linkedin', 'founded_year',
            'mission', 'vision', 'short_description', 'hero_background',
        ]

    def _get_translated_field(self, obj, field_name):
        # Use safe_translation_getter to fallback gracefully
        return obj.safe_translation_getter(field_name, default='')

    def get_mission(self, obj):
        return self._get_translated_field(obj, 'mission')

    def get_vision(self, obj):
        return self._get_translated_field(obj, 'vision')

    def get_short_description(self, obj):
        return self._get_translated_field(obj, 'short_description')
    
    # ✅ FULL URL döndür
    def get_logo(self, obj):
        if not obj.logo:
            return None
        return obj.logo.url  # CloudinaryField varsa bu yeterli

    def get_hero_background(self, obj):
        if not obj.hero_background:
            return None
        return obj.hero_background.url


class BoardMemberSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = BoardMember
        fields = ['id', 'name', 'title', 'email', 'image', 'order']

    def get_image(self, obj):
        if not obj.image:
            return None
        return obj.image.url