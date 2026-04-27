from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, UserProfileView, ChangePasswordView, VolunteerApplicationView, UserMeView, MembershipCancelView, AdminCancellationRequestActionView, AdminCancellationRequestListView, LogoutView, UserEventsView, VolunteerStatusView
app_name = 'users'

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    #path('users/me/', UserProfileView.as_view(), name='user_profile'),
    path('users/me/change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('volunteer/apply/', VolunteerApplicationView.as_view(), name='volunteer_apply'),
    path('me/', UserMeView.as_view(), name='user-me'),
    path('me/cancel-membership/', MembershipCancelView.as_view(), name='membership-cancel'),
    path('auth/logout/', LogoutView.as_view(), name='auth-logout'),
    path('me/events/', UserEventsView.as_view(), name='user-events'),
    path('me/volunteer-status/', VolunteerStatusView.as_view(), name='volunteer-status'),
    # Admin endpoints
    path('admin/cancellation-requests/', AdminCancellationRequestListView.as_view(), name='admin-cancellation-list'),
    path('admin/cancellation-requests/<int:pk>/action/', AdminCancellationRequestActionView.as_view(), name='admin-cancellation-action'),
]