from rest_framework import generics, status
from rest_framework.response import Response
from django.conf import settings
from .models import ContactMessage
from .serializers import ContactMessageSerializer
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from rest_framework.permissions import AllowAny


class ContactCreateView(generics.CreateAPIView):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        smtp_server = 'send.one.com'
        smtp_port = 465
        smtp_username = settings.EMAIL_HOST_USER
        smtp_password = settings.EMAIL_HOST_PASSWORD

        try:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
            server.login(smtp_username, smtp_password)

            admin_email = smtp_username
            subject = f"Contact Form: {instance.subject}"

            admin_msg = MIMEMultipart()
            admin_msg['From'] = f"Snödroppen Kultur Förening <{smtp_username}>"
            admin_msg['To'] = admin_email
            admin_msg['Subject'] = subject
            admin_msg.add_header('Reply-To', instance.email)
            admin_msg.attach(MIMEText(f"From: {instance.name} <{instance.email}>\n\n{instance.message}", 'plain'))
            server.sendmail(smtp_username, admin_email, admin_msg.as_string())

            user_msg = MIMEMultipart()
            user_msg['From'] = f"Snödroppen Kultur Förening <{smtp_username}>"
            user_msg['To'] = instance.email
            user_msg['Subject'] = "Thank you for contacting us"
            user_msg.attach(MIMEText(f"Dear {instance.name},\n\nWe have received your message and will get back to you soon.\n\nBest regards,\nAssociation", 'plain'))
            server.sendmail(smtp_username, instance.email, user_msg.as_string())

            server.quit()

        except Exception as e:
            print(f"SMTP ERROR: {str(e)}")
            # Email hatası olsa bile 201 dön — mesaj kaydedildi

        return Response(serializer.data, status=status.HTTP_201_CREATED)