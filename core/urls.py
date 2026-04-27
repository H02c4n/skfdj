from django.urls import path
from .views import SiteSettingsView, BoardMemberListView

app_name = 'core'

urlpatterns = [
    path('settings/', SiteSettingsView.as_view(), name='site-settings'),
    path('board-members/', BoardMemberListView.as_view(), name='board-members'),
]