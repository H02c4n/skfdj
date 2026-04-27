from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, MembershipCancellationRequest
from events.models import Event
from django.utils.translation import gettext_lazy as _



# Lightweight event serializer for dashboard
class EventMiniSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    price_display = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ('id', 'title', 'slug', 'date_time', 'price_display')

    def get_title(self, obj):
        return obj.safe_translation_getter('title', default='')

    def get_price_display(self, obj):
        if obj.price is None or obj.price == 0:
            return _('Free')
        return f"{obj.price} SEK"
    

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'role', 'is_volunteer', 'bio', 'phone', 'date_joined')
        read_only_fields = ('id', 'date_joined', 'role', 'is_volunteer')


# Enhanced user serializer for /me/
class UserMeSerializer(serializers.ModelSerializer):
    registered_events = serializers.SerializerMethodField()
    membership_status = serializers.SerializerMethodField()
    has_pending_cancellation = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name',
            'role', 'is_volunteer', 'bio', 'phone', 'date_joined',
            'membership_status', 'registered_events', 'has_pending_cancellation',
            'is_active',  # <-- add this line
        )
        read_only_fields = ('id', 'email', 'username', 'role', 'is_volunteer', 'date_joined', 
                            'membership_status', 'registered_events', 'has_pending_cancellation', 'is_active')

    def get_registered_events(self, obj):
        registrations = obj.event_registrations.select_related('event').order_by('event__date_time')
        events = [reg.event for reg in registrations]
        return EventMiniSerializer(events, many=True).data

    def get_membership_status(self, obj):
        return _('Active') if obj.is_active else _('Inactive')

    def get_has_pending_cancellation(self, obj):
        return obj.cancellation_requests.filter(status='pending').exists()

class VolunteerStatusSerializer(serializers.ModelSerializer):
    application_status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('is_volunteer', 'role', 'application_status')

    def get_application_status(self, obj):
        # If user is already a volunteer, status is 'approved'
        if obj.is_volunteer:
            return 'approved'
        # Check if there is a pending volunteer application
        # (Assume a VolunteerApplication model exists or we can use a flag)
        # For now, return 'none' if not applied; you can extend with actual VolunteerApplication model
        return 'none'


# Serializer for creating cancellation request
class MembershipCancellationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = MembershipCancellationRequest
        fields = ('id', 'user', 'reason', 'status', 'created_at')
        read_only_fields = ('id', 'user', 'status', 'created_at')

    def validate(self, attrs):
        user = self.context['request'].user
        if MembershipCancellationRequest.objects.filter(user=user, status='pending').exists():
            raise serializers.ValidationError(_('You already have a pending cancellation request.'))
        return attrs

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

# Admin serializer for managing cancellation requests
class AdminCancellationRequestSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    reviewed_by_email = serializers.EmailField(source='reviewed_by.email', read_only=True)

    class Meta:
        model = MembershipCancellationRequest
        fields = '__all__'
        read_only_fields = ('created_at', 'reviewed_at', 'reviewed_by')



class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])

class VolunteerApplicationSerializer(serializers.Serializer):
    message = serializers.CharField(required=False, allow_blank=True)