import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class PhoneNumberValidator:
    @staticmethod
    def validate_phone_number(value):
        if not re.match(r"^\+?1?\d{9,15}$", value):
            raise ValidationError(
                _("Invalid phone number format."), code="invalid_phone_number"
            )


class NameValidator:
    @staticmethod
    def validate_name(value):
        if not re.match(r"^[a-zA-Z\s]*$", value):
            raise ValidationError(
                _("Name should only contain alphabets and spaces."), code="invalid_name"
            )
