from __future__ import annotations

from constants import UPDATE_FIELDS
from contact import Contact, validate_contact


class Node:
    """Store one Contact and a reference to the next node."""

    def __init__(self, contact: Contact, next_node: Node | None = None) -> None:
        """Initialize one linked-list node."""
        self.contact = contact
        self.next = next_node

class Phonebook:
    """Manage contacts through a manually implemented singly linked list."""

    def __init__(self) -> None:
        """Create an empty phonebook with head = None and size = 0."""
        self.head: Node | None = None
        self.size: int = 0

    def _find_node_by_id(self, student_id: str) -> Node | None:
        """Return the node containing student_id, or None when not found."""
        current = self.head
        while current is not None:
            if current.contact.student_id == student_id:
                return current
            current = current.next
        return None

    def _student_id_exists(
        self,
        student_id: str,
        excluded_student_id: str | None = None,
    ) -> bool:
        """Return True when another contact already uses student_id.

        excluded_student_id is useful during UPDATE because the contact being
        changed is allowed to keep its own current ID.
        """
        current = self.head
        while current is not None:
            if current.contact.student_id == student_id:
                if excluded_student_id is None or student_id != excluded_student_id:
                    return True
            current = current.next
        return False
        pass

    def _phone_exists(
        self,
        phone_number: str,
        excluded_student_id: str | None = None,
    ) -> bool:
        """Return True when another contact already uses phone_number."""
        current = self.head
        while current is not None:
            if current.contact.phone_number() == phone_number:
                if excluded_student_id is None or current.contact.student_id != excluded_student_id:
                    return True
            current = current.next
        return False

    def _insert_node_sorted(self, node: Node) -> None:
        """Insert node into its correct linked-list position.

        Correctly handle an empty list, insertion before head, insertion in
        the middle, and insertion at the end. Update size exactly once.
        Do not use sort() or sorted().
        """
        node_key = node.contact.sort_key()

        if self.head is None or node_key < self.head.contact.sort_key():
            node.next = self.head
            self.head = node
        else:
            current = self.head
            while current.next is not None and current.next.contact.sort_key() < node_key:
                current = current.next
            node.next = current.next
            current.next = node

        self.size += 1

    def _detach_node(self, student_id: str) -> Node | None:
        """Unlink and return one node, or return None when it is missing.

        Correctly handle removing the only node, head, middle, and tail.
        Update size exactly once when a node is removed.
        """
        if self.head is None:
            return None

        if self.head.contact.student_id == student_id:
            removed = self.head
            self.head = self.head.next
            removed.next = None
            self.size -= 1
            return removed

        current = self.head
        while current.next is not None:
            if current.next.contact.student_id == student_id:
                removed = current.next
                current.next = removed.next
                removed.next = None
                self.size -= 1
                return removed
            current = current.next

        return None

    def add_contact(self, contact: Contact) -> str:
        """Add one validated Contact and return the exact ADD result line.

        Check duplicate student ID before duplicate complete phone number.
        """
        error = validate_contact(contact)
        if error:
            return error

        if self._student_id_exists(contact.student_id):
            return f"ERROR DUPLICATE_ID {contact.student_id}"

        if self._phone_exists(contact.phone_number()):
            return f"ERROR DUPLICATE_PHONE {contact.phone_number()}"

        new_node = Node(contact)
        self._insert_node_sorted(new_node)
        return f"OK ADD: {contact.student_id}"
    

    def find_contact(self, student_id: str) -> str:
        """Return the exact FOUND or NOT_FOUND output for student_id."""
        node = self._find_node_by_id(student_id)
        if node is not None:
            return f"FOUND: | {node.contact}"
        return f"ERROR NOT_FOUND {student_id}"

    def find_by_surname(self, surname: str) -> str:
        """Return MATCHES and CONTACT lines in current linked-list order."""
        matches = []
        target = surname.lower()
        current = self.head
        while current is not None:
            if current.contact.surname.lower() == target:
                matches.append(str(current.contact))
            current = current.next

        out = [f"MATCHES: {len(matches)}"]
        for match_str in matches:
            out.append(f"CONTACT: | {match_str}")
        return "\n".join(out)

    def update_contact(
        self,
        target_student_id: str,
        field: str,
        new_value: str,
    ) -> str:
        """Validate and apply one complete contact update.

        A failed update must leave the original Contact and linked list
        unchanged. ID, SURNAME, and GIVEN_NAME changes may require the node to
        be detached and reinserted into the correct sorted position.
        """
        node = self._find_node_by_id(target_student_id)
        if node is None:
            return f"ERROR NOT_FOUND {target_student_id}"

        if field not in UPDATE_FIELDS:
            return f"ERROR INVALID_FIELD {field}"

        pro = node.contact.copy_with_update(field, new_value)

        error = validate_contact(pro)
        if error:
            return error

        if self._student_id_exists(pro.student_id, excluded_student_id=target_student_id):
            return f"ERROR DUPLICATE_ID {pro.student_id}"

        if self._phone_exists(pro.phone_number(), excluded_student_id=target_student_id):
            return f"ERROR DUPLICATE_PHONE {pro.phone_number()}"

        old_value = node.contact.get_field(field)

        if field in ("ID", "SURNAME", "GIVEN_NAME"):
            detached = self._detach_node(target_student_id)
            if detached is not None:
                detached.contact = pro
                self._insert_node_sorted(detached)
        else:
            node.contact = pro

        return f"OK UPDATE: {field} | {old_value} -> {new_value}"

    def delete_contact(self, student_id: str) -> str:
        """Delete one contact and return the exact DELETE result line."""
        rem = self._detach_node(student_id)
        if rem is not None:
            return f"OK DELETE: {student_id}"
        return f"ERROR NOT_FOUND {student_id}"

    def list_contacts(self) -> str:
        """Return LIST followed by CONTACT lines in linked-list order."""
        out = [f"LIST: {self.size}"]
        current = self.head
        while current is not None:
            out.append(f"CONTACT: | {current.contact}")
            current = current.next
        return "\n".join(out)

    def filter_by_country(self, country_codes: set[str]) -> str:
        """Return COUNTRY_MATCHES and matching CONTACT lines in list order."""
        mat = []
        current = self.head
        while current is not None:
            if current.contact.country_code in country_codes:
                mat.append(str(current.contact))
            current = current.next

        out = [f"COUNTRY_MATCHES: {len(mat)}"]
        for match_str in mat:
            out.append(f"CONTACT: | {match_str}")
        return "\n".join(out)
