from __future__ import annotations

import unittest

import main
from constants import COUNTRY_CODES
from contact import (
    Contact,
    is_valid_area_code,
    is_valid_local_number,
    is_valid_student_id,
)
from phonebook import Node, Phonebook


class ArchitectureTests(unittest.TestCase):
    def test_classes_remain_in_the_required_files(self) -> None:
        self.assertEqual(Contact.__module__, "contact")
        self.assertEqual(Node.__module__, "phonebook")
        self.assertEqual(Phonebook.__module__, "phonebook")

    def test_country_dictionary_is_available_from_main(self) -> None:
        self.assertIs(main.COUNTRY_CODES, COUNTRY_CODES)


class ContactTests(unittest.TestCase):
    def make_contact(self, **changes: str) -> Contact:
        values = dict(
            student_id="S-001", surname="Abad", given_name="Lio",
            occupation="Analyst", country_code="62", area_code="021",
            local_number="000777",
        )
        values.update(changes)
        return Contact(**values)

    def test_country_dictionary_contains_all_required_codes(self) -> None:
        expected = {"60", "62", "63", "65", "66", "84", "95", "670", "673", "855", "856"}
        self.assertEqual(set(COUNTRY_CODES), expected)

    def test_contact_stores_all_fields(self) -> None:
        c = self.make_contact()
        self.assertEqual(
            (c.student_id, c.surname, c.given_name, c.occupation, c.country_code, c.area_code, c.local_number),
            ("S-001", "Abad", "Lio", "Analyst", "62", "021", "000777"),
        )

    def test_phone_number_preserves_leading_zeros(self) -> None:
        self.assertEqual(self.make_contact().phone_number(), "62-021-000777")

    def test_sort_key_ignores_name_capitalization(self) -> None:
        a = self.make_contact(surname="Garcia", given_name="Mina")
        b = self.make_contact(surname="gARCIA", given_name="mINA")
        self.assertEqual(a.sort_key(), b.sort_key())

    def test_str_uses_required_readable_template(self) -> None:
        self.assertEqual(
            str(self.make_contact()),
            "S-001 - Abad, Lio - Analyst - Indonesia - 62-021-000777",
        )

    def test_copy_with_update_does_not_mutate_original(self) -> None:
        original = self.make_contact()
        candidate = original.copy_with_update("SURNAME", "Abao")
        self.assertEqual(original.surname, "Abad")
        self.assertEqual(candidate.surname, "Abao")


class NodePhonebookTests(unittest.TestCase):
    def contact(self, student_id: str, surname: str, given: str, phone: str) -> Contact:
        return Contact(student_id, surname, given, "Analyst", "63", "02", phone)

    def test_node_stores_contact_and_next(self) -> None:
        c = self.contact("S-001", "Abad", "Ana", "100001")
        node = Node(c)
        self.assertIs(node.contact, c)
        self.assertIsNone(node.next)

    def test_new_phonebook_is_empty(self) -> None:
        p = Phonebook()
        self.assertIsNone(p.head)
        self.assertEqual(p.size, 0)

    def test_sorted_add_builds_real_node_chain(self) -> None:
        p = Phonebook()
        p.add_contact(self.contact("S-003", "Zulu", "Ana", "100003"))
        p.add_contact(self.contact("S-001", "Abad", "Ana", "100001"))
        p.add_contact(self.contact("S-002", "Lim", "Ana", "100002"))
        self.assertEqual(p.size, 3)
        self.assertIsInstance(p.head, Node)
        ids = []
        current = p.head
        while current is not None:
            ids.append(current.contact.student_id)
            current = current.next
        self.assertEqual(ids, ["S-001", "S-002", "S-003"])

    def test_delete_only_node_restores_empty_state(self) -> None:
        p = Phonebook()
        p.add_contact(self.contact("S-001", "Abad", "Ana", "100001"))
        self.assertEqual(p.delete_contact("S-001"), "OK DELETE S-001")
        self.assertIsNone(p.head)
        self.assertEqual(p.size, 0)

    def test_failed_duplicate_update_does_not_change_contact(self) -> None:
        p = Phonebook()
        p.add_contact(self.contact("S-001", "Abad", "Ana", "100001"))
        p.add_contact(self.contact("S-002", "Lim", "Bea", "100002"))
        result = p.update_contact("S-001", "ID", "S-002")
        self.assertEqual(result, "ERROR DUPLICATE_ID S-002")
        self.assertIn("S-001 - Abad, Ana", p.list_contacts())


class ValidationTests(unittest.TestCase):
    def test_student_id_examples(self) -> None:
        self.assertTrue(is_valid_student_id("S-001"))
        self.assertFalse(is_valid_student_id("s-001"))
        self.assertFalse(is_valid_student_id("-S001"))

    def test_area_and_local_number_lengths(self) -> None:
        self.assertTrue(is_valid_area_code("000001"))
        self.assertFalse(is_valid_area_code("0000001"))
        self.assertTrue(is_valid_local_number("000"))
        self.assertFalse(is_valid_local_number("00"))

    def test_canonical_count_examples(self) -> None:
        self.assertTrue(main.is_canonical_count("0"))
        self.assertTrue(main.is_canonical_count("120"))
        self.assertFalse(main.is_canonical_count("005"))
        self.assertFalse(main.is_canonical_count("+5"))


if __name__ == "__main__":
    unittest.main()
