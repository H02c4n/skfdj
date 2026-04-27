from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from ckeditor.fields import RichTextField
from parler.models import TranslatableModel, TranslatedFields
from cloudinary.models import CloudinaryField

class Category(models.Model):
    NAME_CHOICES = (
        ('news', _('News')),
        ('events', _('Events')),
        ('activities', _('Activities')),
    )
    name = models.CharField(max_length=50, choices=NAME_CHOICES, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    def __str__(self):
        return self.get_name_display()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.get_name_display())
        super().save(*args, **kwargs)

class Tag(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=50, verbose_name=_('Name'))
    )
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')

    def __str__(self):
        return self.safe_translation_getter('name', self.slug)

    def save(self, *args, **kwargs):
        if not self.slug:
            name = self.safe_translation_getter('name', any_language=True)
            if name:
                self.slug = slugify(name)
            else:
                self.slug = f"tag-{self.id or ''}"
        super().save(*args, **kwargs)

class Post(TranslatableModel):
    translations = TranslatedFields(
        title=models.CharField(max_length=200, verbose_name=_('Title')),
        content=RichTextField(verbose_name=_('Content')),
    )
    slug = models.SlugField(unique=True, blank=True)
    image = CloudinaryField('image', blank=True, null=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True,
        related_name='posts', verbose_name=_('Category')
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts', verbose_name=_('Tags'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')
        ordering = ['-created_at']

    def __str__(self):
        return self.safe_translation_getter('title', self.slug)

    def save(self, *args, **kwargs):
        if not self.slug:
            title = self.safe_translation_getter('title', any_language=True)
            if title:
                self.slug = slugify(title)
            else:
                self.slug = f"post-{self.created_at or ''}"
        super().save(*args, **kwargs)