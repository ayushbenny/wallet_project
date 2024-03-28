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


class PasswordValidator:
    @staticmethod
    def validate_password(value):
        if not re.match(
            r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,16}$",
            value,
        ):
            raise ValidationError(
                _(
                    "Password must contain at least one uppercase letter, one lowercase letter, one digit, one special character, and be between 8 and 16 characters long."
                ),
                code="invalid_password",
            )
