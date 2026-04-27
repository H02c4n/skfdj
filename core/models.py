from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields
#from django.core.validators import FileExtensionValidator
#from .validators import validate_svg
from cloudinary.models import CloudinaryField

class SiteSettings(TranslatableModel):
    """
    Singleton model for global organisation data.
    Only one instance allowed.
    """
    # Non-translatable fields
    organization_name = models.CharField(max_length=100, verbose_name=_('Organization Name'))
    org_number = models.CharField(max_length=50, verbose_name=_('Organization Number'))
    """ logo = models.FileField(
        upload_to='site/',
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['svg', 'png', 'jpg', 'jpeg']),
            validate_svg,
        ],
        verbose_name=_('Logo')
    ) """
    logo = CloudinaryField('logo', blank=True, null=True)
    email = models.EmailField(verbose_name=_('Email'))
    phone = models.CharField(max_length=30, verbose_name=_('Phone'))
    address = models.TextField(verbose_name=_('Address'))
    website = models.URLField(blank=True, verbose_name=_('Website'))
    facebook = models.URLField(blank=True, verbose_name=_('Facebook'))
    instagram = models.URLField(blank=True, verbose_name=_('Instagram'))
    linkedin = models.URLField(blank=True, verbose_name=_('LinkedIn'))
    founded_year = models.PositiveIntegerField(blank=True, null=True, verbose_name=_('Founded Year'))
    hero_background = CloudinaryField(
        'hero_background',
        blank=True,
        null=True
    )

    # Translatable fields
    translations = TranslatedFields(
        mission=models.TextField(blank=True, verbose_name=_('Mission')),
        vision=models.TextField(blank=True, verbose_name=_('Vision')),
        short_description=models.CharField(max_length=255, blank=True, verbose_name=_('Short Description')),
    )

    class Meta:
        verbose_name = _('Site Settings')
        verbose_name_plural = _('Site Settings')

    def __str__(self):
        return self.organization_name

    def save(self, *args, **kwargs):
        if not self.pk and SiteSettings.objects.exists():
            raise ValidationError(_('Only one SiteSettings instance can be created.'))
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        """
        Returns the singleton instance, creating it if it doesn't exist.
        """
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class BoardMember(models.Model):
    """
    Board members displayed in a fixed order.
    """
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    title = models.CharField(max_length=100, verbose_name=_('Title/Role'))
    email = models.EmailField(verbose_name=_('Email'))
    image = CloudinaryField('image', blank=True, null=True)
    order = models.PositiveIntegerField(default=0, verbose_name=_('Display Order'))

    class Meta:
        verbose_name = _('Board Member')
        verbose_name_plural = _('Board Members')
        ordering = ['order']

    def __str__(self):
        return f"{self.name} – {self.title}"