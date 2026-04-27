import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_svg(value):
    """
    Validate that the uploaded file:
    - Is an SVG (contains '<svg' tag)
    - Does NOT contain '<script' (security)
    """
    # Only check SVG files
    if not value.name.lower().endswith('.svg'):
        return

    try:
        # Read first 4KB – enough to detect SVG structure and scripts
        content = value.read(4096).decode('utf-8', errors='ignore').lower()
        value.seek(0)  # Reset file pointer for later use

        # Must contain '<svg'
        if '<svg' not in content:
            raise ValidationError(_('Invalid SVG file.'))

        # Must NOT contain '<script'
        if '<script' in content:
            raise ValidationError(_('SVG files containing scripts are not allowed.'))

    except UnicodeDecodeError:
        raise ValidationError(_('Invalid file encoding. SVG must be UTF-8 text.'))
    except Exception as e:
        raise ValidationError(_('Could not validate SVG file: %(error)s') % {'error': str(e)})