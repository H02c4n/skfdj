from rest_framework import serializers
from parler_rest.serializers import TranslatableModelSerializer
from parler_rest.fields import TranslatedFieldsField
from .models import Event, EventRegistration, RecurrenceRule
from users.serializers import UserSerializer
from django.utils.translation import gettext_lazy as _


# ----------------------------------------------------------------------------
# New serializer for a single occurrence (used in expanded lists)
# ----------------------------------------------------------------------------
class EventOccurrenceSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    slug = serializers.CharField()
    date_time = serializers.DateTimeField()
    time = serializers.CharField()
    price = serializers.DecimalField(max_digits=8, decimal_places=2)  # keep raw price
    is_free = serializers.BooleanField()
    attendees_count = serializers.IntegerField()
    capacity = serializers.IntegerField(allow_null=True)
    image = serializers.CharField(allow_null=True)   # URL string
    location = serializers.CharField()
    occurrence_date = serializers.DateField()


class EventListSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Event)
    is_free = serializers.SerializerMethodField()
    attendees_count = serializers.IntegerField(source='registrations.count', read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ('id', 'slug', 'image', 'date_time', 'price', 'capacity',
                  'translations', 'is_free', 'attendees_count')

    def get_is_free(self, obj):
        return obj.is_free()
    
    def get_image(self, obj):
        if not obj.image:
            return None
        return obj.image.url

class EventDetailSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Event)
    is_free = serializers.SerializerMethodField()
    attendees_count = serializers.IntegerField(source='registrations.count', read_only=True)
    available_spots = serializers.IntegerField(read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ('id', 'slug', 'image', 'date_time', 'price', 'capacity',
                  'created_at', 'updated_at', 'translations',
                  'is_free', 'attendees_count', 'available_spots')

    def get_is_free(self, obj):
        return obj.is_free()
    
    def get_image(self, obj):
        if not obj.image:
            return None
        return obj.image.url
    



class EventMiniSerializer(serializers.ModelSerializer):
    translations = TranslatedFieldsField(shared_model=Event)
   
    price_display = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ('id', 'translations', 'slug', 'image', 'date_time', 'price_display')

   

    def get_price_display(self, obj):
        if obj.price is None or obj.price == 0:
            return _('Free')
        return f"{obj.price} SEK"
    
    def get_image(self,obj):
        if not obj.image:
            return None
        return obj.image.url



class EventRegistrationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    event_slug = serializers.SlugRelatedField(
        source='event', slug_field='slug', queryset=Event.objects.all(), write_only=True
    )
    occurrence_date = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = EventRegistration
        fields = ('id', 'user', 'event', 'event_slug', 'registered_at', 'occurrence_date')
        read_only_fields = ('user', 'registered_at', 'event')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    




class CalendarEventSerializer(serializers.ModelSerializer):
    translations = TranslatedFieldsField(shared_model=Event)
    time = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ('id', 'slug', 'time', 'price', 'translations')

    """ def get_title(self, obj):
        title = obj.safe_translation_getter("title", language_code="sv")
    
        if not title:
            title = obj.safe_translation_getter("title", any_language=True)
    
        return title """

    def get_time(self, obj):
        return obj.date_time.strftime('%H:%M')

    def get_price(self, obj):
        if obj.price is None or obj.price == 0:
            return 'Free'
        return f"{obj.price} SEK"