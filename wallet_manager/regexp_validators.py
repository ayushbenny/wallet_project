import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class PhoneNumberValidator:
    """
    Phone number Validator class
    """

    @staticmethod
    def validate_phone_number(value):
        """
        The entered value (phone number) will be checked like ,
        '+1' is there or not and minimum of 9 and maximum of 15 characters are allowed.
        """
        if not re.match(r"^\+?1?\d{9,15}$", value):
            raise ValidationError(
                _("Invalid phone number format."), code="invalid_phone_number"
            )


class NameValidator:
    """
    Name Validator class
    """

    @staticmethod
    def validate_name(value):
        """
        The entered value (first_name or last_name) will be checked based on ,
        it should only accept Alphabet and whitespaces but not special characters.
        """
        if not re.match(r"^[a-zA-Z\s]*$", value):
            raise ValidationError(
                _("Name should only contain alphabets and spaces."), code="invalid_name"
            )
