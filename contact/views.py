from rest_framework import generics, status
from rest_framework.response import Response
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from .models import ContactMessage
from .serializers import ContactMessageSerializer
from rest_framework.permissions import AllowAny


class ContactCreateView(generics.CreateAPIView):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        try:
            # Admin'e email
            send_mail(
                subject=f"Contact Form: {instance.subject}",
                message=f"From: {instance.name} <{instance.email}>\n\n{instance.message}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.EMAIL_HOST_USER],
                reply_to=[instance.email],
                fail_silently=True,
            )

            # Kullanıcıya auto-reply
            send_mail(
                subject="Thank you for contacting us",
                message=f"Dear {instance.name},\n\nWe have received your message and will get back to you soon.\n\nBest regards,\nAssociation",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"EMAIL ERROR: {str(e)}")

        return Response(serializer.data, status=status.HTTP_201_CREATED)