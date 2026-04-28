""" from rest_framework import generics
from django.core.mail import send_mail
from django.conf import settings
from .models import ContactMessage
from .serializers import ContactMessageSerializer
import smtplib


class ContactCreateView(generics.CreateAPIView):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        print(instance.email)

        # Send email to admin
        admin_email = settings.DEFAULT_FROM_EMAIL
        subject = f"Contact Form: {instance.subject}"
        message = f"From: {instance.name} <{instance.email}>\n\n{instance.message}"
        send_mail(subject, message, instance.email, [admin_email])

        # Auto-reply
        reply_subject = "Thank you for contacting us"
        reply_message = f"Dear {instance.name},\n\nWe have received your message and will get back to you soon.\n\nBest regards,\nAssociation"
        send_mail(reply_subject, reply_message, admin_email, [instance.email])

 """


from rest_framework import generics
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

    def perform_create(self, serializer):
        instance = serializer.save()

        smtp_server = 'send.one.com'
        smtp_port = 465
        smtp_username = settings.EMAIL_HOST_USER
        smtp_password = settings.EMAIL_HOST_PASSWORD

        try:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
            server.login(smtp_username, smtp_password)

            # =========================
            # 📩 EMAIL TO ADMIN
            # =========================
            admin_email = smtp_username
            subject = f"Contact Form: {instance.subject}"

            admin_msg = MIMEMultipart()
            admin_msg['From'] = f"Snödroppen Kultur Förening <{smtp_username}>"
            admin_msg['To'] = admin_email
            admin_msg['Subject'] = subject
            admin_msg.add_header('Reply-To', instance.email)

            admin_body = f"""
            From: {instance.name} <{instance.email}>

            {instance.message}
            """

            admin_msg.attach(MIMEText(admin_body, 'plain'))

            server.sendmail(smtp_username, admin_email, admin_msg.as_string())

            # =========================
            # 📬 AUTO-REPLY TO USER
            # =========================
            reply_subject = "Thank you for contacting us"

            user_msg = MIMEMultipart()
            user_msg['From'] = f"Snödroppen Kultur Förening <{smtp_username}>"
            user_msg['To'] = instance.email
            user_msg['Subject'] = reply_subject

            reply_body = f"""
            Dear {instance.name},

            We have received your message and will get back to you soon.

            Best regards,
            Association
            """

            user_msg.attach(MIMEText(reply_body, 'plain'))

            server.sendmail(smtp_username, instance.email, user_msg.as_string())

            server.quit()

        except Exception as e:
            print(f"SMTP ERROR: {str(e)}")