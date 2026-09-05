from __future__ import annotations

from constants import COUNTRY_CODES


class Contact:
    """Represent one contact stored by the ASEAN Phonebook."""

    def __init__(
        self,
        student_id: str,
        surname: str,
        given_name: str,
        occupation: str,
        country_code: str,
        area_code: str,
        local_number: str,
    ) -> None:
        """Store all seven contact fields without changing their text."""
        self.student_id = student_id
        self.surname = surname
        self.given_name = given_name
        self.occupation = occupation
        self.country_code = country_code
        self.area_code = area_code
        self.local_number = local_number

    def phone_number(self) -> str:
        """Return the complete phone number as code-area-local."""
        return f"{self.country_code}-{self.area_code}-{self.local_number}"

    def sort_key(self) -> tuple[str, str, str]:
        """Return the surname, given-name, and student-ID sorting key.

        Name comparison must ignore capitalization, but the original stored
        spelling must remain unchanged.
        """
        return (self.surname.lower(), self.given_name.lower(), self.student_id)

    def get_field(self, field: str) -> str:
        """Return the current value of one supported UPDATE field."""
        fields = {
            "ID": self.student_id,
            "SURNAME": self.surname,
            "GIVEN_NAME": self.given_name,
            "OCCUPATION": self.occupation,
            "COUNTRY_CODE": self.country_code,
            "AREA_CODE": self.area_code,
            "LOCAL_NUMBER": self.local_number,
        }
        if field in fields:
            return fields[field]
        raise ValueError(f"Unsupported field: {field}")

    def copy_with_update(self, field: str, new_value: str) -> Contact:
        """Return a proposed Contact containing one field change.

        Do not modify the current Contact. The proposed Contact is checked
        first so a failed UPDATE can leave the linked list unchanged.
        """
        fields = {
            "ID": self.student_id,
            "SURNAME": self.surname,
            "GIVEN_NAME": self.given_name,
            "OCCUPATION": self.occupation,
            "COUNTRY_CODE": self.country_code,
            "AREA_CODE": self.area_code,
            "LOCAL_NUMBER": self.local_number,
        }
        if field in fields:
            fields[field] = new_value
        return Contact(*fields.values())

    def __str__(self) -> str:
        """Return the exact readable contact format required by the project."""
        cname = COUNTRY_CODES.get(self.country_code, "")
        return (
            f"{self.student_id} {self.surname}, {self.given_name} "
            f"{self.occupation} {cname} {self.phone_number()}"
        )


def is_valid_student_id(value: str) -> bool:
    """Return True when value follows the published student-ID rules."""
    if not (1 <= len(value) <= 20):
        return False
    if not value[0].isalnum():
        return False
    for char in value:
        if not (char.isalnum() or char == "-"):
            return False
    return True


def is_valid_name(value: str) -> bool:
    """Return True when value is a valid surname or given name."""
    if not (1 <= len(value) <= 40):
        return False
    if value.startswith(" ") or value.endswith(" "):
        return False
    for char in value:
        if not (char.isalpha() or char in (" ", "'", "-")):
            return False
    return True


def is_valid_occupation(value: str) -> bool:
    """Return True when value follows the published occupation rules."""
    if not (1 <= len(value) <= 60):
        return False
    if value.startswith(" ") or value.endswith(" "):
        return False
    for char in value:
        if not (char.isalnum() or char in (" ", ".", "'", "/", "-", "+", "*")):
            return False
    return True


def is_valid_area_code(value: str) -> bool:
    """Return True for an area code containing 1 to 6 digits."""
    return value.isdigit() and (1 <= len(value) <= 6)


def is_valid_local_number(value: str) -> bool:
    """Return True for a local number containing 3 to 12 digits."""
    return value.isdigit() and (3 <= len(value) <= 12)


def is_valid_country_code(value: str) -> bool:
    """Return True for a valid country code."""
    return value in COUNTRY_CODES


def validate_contact(contact: Contact) -> str | None:
    """Return the first required validation error, or None when valid.

    Check fields from left to right using the order published in the project
    definition. COUNTRY_CODE uses ERROR INVALID_COUNTRY <value>.
    """
    if not is_valid_student_id(contact.student_id):
        return "ERROR INVALID_VALUE STUDENT_ID"
    if not is_valid_name(contact.surname):
        return "ERROR INVALID_VALUE SURNAME"
    if not is_valid_name(contact.given_name):
        return "ERROR INVALID_VALUE GIVEN_NAME"
    if not is_valid_occupation(contact.occupation):
        return "ERROR INVALID_VALUE OCCUPATION"
    if not is_valid_country_code(contact.country_code):
        return f"ERROR INVALID_COUNTRY {contact.country_code}"
    if not is_valid_area_code(contact.area_code):
        return "ERROR INVALID_VALUE AREA_CODE"
    if not is_valid_local_number(contact.local_number):
        return "ERROR INVALID_VALUE LOCAL_NUMBER"
    return None
