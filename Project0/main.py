from __future__ import annotations

import sys

from constants import COUNTRY_CODES
from contact import Contact, validate_contact
from phonebook import Phonebook


def is_canonical_count(value: str) -> bool:
    """Return True for 0 or a nonzero decimal without signs/leading zeros."""
    if value == "0":
        return True
    if not value or not value.isdigit():
        return False
    if value.startswith("0"):
        return False
    return True

def process_input_line(phonebook: Phonebook, line: str) -> str:
    """Process one phonebook input line and return its exact output.

    Check field count before field values. The input processor may parse text,
    validate fields, and call Phonebook methods, but it must not relink nodes
    or directly change Phonebook.head.
    """
    if not line:
        return "ERROR MALFORMED"

    parts = line.split(" ", 1)
    cmd = parts[0]
    rest = parts[1] if len(parts) > 1 else ""

    if cmd == "ADD":
        if not rest:
            return "ERROR MALFORMED ADD"
        fields = rest.split("|")
        if len(fields) != 7:
            return "ERROR MALFORMED ADD"
        contact = Contact(
            fields[0], fields[1], fields[2], fields[3], fields[4], fields[5], fields[6]
        )
        error = validate_contact(contact)
        if error:
            return error
            
        return phonebook.add_contact(contact)

    elif cmd == "FIND":
        if not rest:
            return "ERROR MALFORMED"
        return phonebook.find_contact(rest)

    elif cmd == "FIND_SURNAME":
        if not rest:
            return "ERROR MALFORMED"
        return phonebook.find_by_surname(rest)

    elif cmd == "UPDATE":
        if not rest:
            return "ERROR MALFORMED UPDATE"
        fields = rest.split("|")
        if len(fields) != 3:
            return "ERROR MALFORMED UPDATE"
        return phonebook.update_contact(fields[0], fields[1], fields[2])

    elif cmd == "DELETE":
        if not rest:
            return "ERROR MALFORMED"
        return phonebook.delete_contact(rest)

    elif cmd == "LIST":
        if rest:
            return "ERROR MALFORMED"
        return phonebook.list_contacts()

    elif cmd == "COUNTRY":
        if not rest:
            return "ERROR INVALID_VALUE COUNTRY_CODES"
        raw_codes = rest.split(",")
        unique_codes = set()
        for raw in raw_codes:
            code = raw.strip()
            if not code or not code.isdigit():
                return "ERROR INVALID_VALUE COUNTRY_CODES"
            if code not in COUNTRY_CODES:
                return f"ERROR INVALID_COUNTRY {code}"
            unique_codes.add(code)
        return phonebook.filter_by_country(unique_codes)

    else:
        return f"ERROR UNKNOWN_COMMAND {cmd}"

def run_program(raw_input: str) -> str:
    """Process one complete ASEAN-PHONEBOOK 1.0 input.

    Validate the version line and input-count line, process exactly the
    requested input lines, and return all produced output joined by newlines.
    """
    lines = raw_input.splitlines()
    if not lines or lines[0] != "ASEAN-PHONEBOOK 1.0":
        return "ERROR VERSION"

    if len(lines) < 2:
        return "ERROR COMMAND_COUNT"

    count_str = lines[1]
    if not is_canonical_count(count_str):
        return "ERROR COMMAND_COUNT"

    try:
        cmd_count = int(count_str)
    except ValueError:
        return "ERROR COMMAND_COUNT"

    if not (0 <= cmd_count <= 200):
        return "ERROR COMMAND_COUNT"

    input_lines = lines[2 : 2 + cmd_count]
    if len(input_lines) < cmd_count:
        return "ERROR COMMAND_COUNT"

    phonebook = Phonebook()
    results = []

    for line in input_lines:
        res = process_input_line(phonebook, line)
        if res:
            results.append(res)

    return "\n".join(results)


def main() -> None:
    """Read standard input, run the phonebook program, and print its output."""
    output = run_program(sys.stdin.read())
    if output:
        print(output)


if __name__ == "__main__":
    main()
