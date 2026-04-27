from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from .models import User, MembershipCancellationRequest
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from .serializers import (
    UserSerializer, RegisterSerializer, UserMeSerializer, MembershipCancellationRequestSerializer,
    ChangePasswordSerializer, VolunteerApplicationSerializer, AdminCancellationRequestSerializer, VolunteerStatusSerializer
)
from events.models import Event
from events.serializers import EventMiniSerializer
from django.utils.translation import gettext_lazy as _
from .permissions import IsAdminUser
from django.utils import timezone

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
    

class UserMeView(generics.RetrieveUpdateAPIView):
    """
    GET: Returns user profile with dashboard data.
    PATCH: Updates bio and phone only.
    """
    serializer_class = UserMeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class MembershipCancelView(generics.CreateAPIView):
    """
    POST: Create a membership cancellation request.
    """
    serializer_class = MembershipCancellationRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class AdminCancellationRequestListView(generics.ListAPIView):
    """
    Admin only: List all cancellation requests.
    """
    serializer_class = AdminCancellationRequestSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = MembershipCancellationRequest.objects.all().select_related('user', 'reviewed_by')


class AdminCancellationRequestActionView(views.APIView):
    """
    Admin only: Approve or reject a cancellation request.
    """
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        try:
            req = MembershipCancellationRequest.objects.get(pk=pk, status='pending')
        except MembershipCancellationRequest.DoesNotExist:
            return Response(
                {'detail': _('Pending request not found.')},
                status=status.HTTP_404_NOT_FOUND
            )

        action = request.data.get('action')
        if action == 'approve':
            req.approve(request.user)
            return Response({'detail': _('Request approved. User deactivated.')})
        elif action == 'reject':
            req.reject(request.user)
            return Response({'detail': _('Request rejected.')})
        else:
            return Response(
                {'detail': _('Action must be "approve" or "reject".')},
                status=status.HTTP_400_BAD_REQUEST
            )


class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not user.check_password(serializer.validated_data['old_password']):
            return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({"detail": "Password changed successfully."})

class VolunteerApplicationView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = VolunteerApplicationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        admins = User.objects.filter(role='admin', is_staff=True)
        admin_emails = [admin.email for admin in admins if admin.email]
        if admin_emails:
            subject = f"Volunteer Application from {request.user.email}"
            message = f"User {request.user.email} wants to become a volunteer.\n"
            message += f"Message: {serializer.validated_data.get('message', '')}"
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, admin_emails)

        return Response({"detail": "Your volunteer application has been submitted."})
    

class LogoutView(views.APIView):
    """
    POST /api/auth/logout/
    Blacklist the provided refresh token.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except TokenError:
                # Token invalid or already blacklisted – still success from client perspective
                pass
        return Response({'detail': _('Successfully logged out.')})


class UserEventsView(generics.ListAPIView):
    """
    GET /api/me/events/
    Returns all events the authenticated user has registered for.
    """
    serializer_class = EventMiniSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        now = timezone.now()
        return Event.objects.filter(
            registrations__user=self.request.user,
            date_time__gte=now  # only future events
        ).order_by('date_time')


class VolunteerStatusView(generics.RetrieveAPIView):
    """
    GET /api/me/volunteer-status/
    Returns volunteer status information.
    """
    serializer_class = VolunteerStatusSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user