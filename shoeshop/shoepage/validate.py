import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class CustomCharacterValidator:
    def validate(self, password, user=None):
        if not re.search(r'[A-Za-z]', password):
            raise ValidationError(
                _("The password must contain at least one letter."),
                code='password_no_letters',
            )

        if not re.search(r'\d', password):
            raise ValidationError(
                _("The password must contain at least one numeric digit."),
                code='password_no_digits',
            )

        if not re.search(r'[!@#$%^&*()_+{}[\]|\\:;"\'<>?,./]', password):
            raise ValidationError(
                _("The password must contain at least one special character."),
                code='password_no_special_chars',
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least one letter, one numeric digit, and one special character."
        )