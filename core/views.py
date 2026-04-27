from rest_framework import generics, permissions
from .models import SiteSettings, BoardMember
from .serializers import SiteSettingsSerializer, BoardMemberSerializer

class SiteSettingsView(generics.RetrieveAPIView):
    """
    Returns the singleton site settings.
    Publicly accessible.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = SiteSettingsSerializer

    def get_object(self):
        return SiteSettings.get_solo()


class BoardMemberListView(generics.ListAPIView):
    """
    Returns all board members, ordered by the 'order' field.
    Publicly accessible.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = BoardMemberSerializer
    queryset = BoardMember.objects.all()