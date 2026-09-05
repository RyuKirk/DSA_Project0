from __future__ import annotations

from pathlib import Path
import difflib
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CASES = HERE / "cases"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import main as student_main


def normalize(text: str) -> str:
    """Normalize line endings and ignore only final newline characters."""
    return text.replace("\r\n", "\n").rstrip("\n")


def run_structure_tests() -> bool:
    """Run direct class/function tests before the full program cases."""
    loader = unittest.TestLoader()
    suite = loader.discover(str(HERE), pattern="test_structure.py")
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    return result.wasSuccessful()


def run_io_cases() -> tuple[int, int]:
    """Run every public .in/.out pair through run_program()."""
    passed = 0
    files = sorted(CASES.glob("*.in"))
    for input_path in files:
        expected_path = input_path.with_suffix(".out")
        expected = normalize(expected_path.read_text(encoding="utf-8"))
        error: Exception | None = None
        try:
            produced = student_main.run_program(input_path.read_text(encoding="utf-8"))
            actual = normalize(produced) if isinstance(produced, str) else ""
        except Exception as exc:
            error = exc
            actual = ""
        ok = error is None and actual == expected
        if ok:
            passed += 1
            print(f"PASS {input_path.stem}")
        else:
            print(f"FAIL {input_path.stem}")
            if error is not None:
                print(f"  Program error: {type(error).__name__}: {error}")
            diff = difflib.unified_diff(
                expected.splitlines(), actual.splitlines(),
                fromfile="expected", tofile="actual", lineterm=""
            )
            for line in list(diff)[:14]:
                print(f"  {line}")
    return passed, len(files)


def main() -> None:
    print("=== Structure Tests ===")
    structure_ok = run_structure_tests()
    print("\n=== Input/Output Tests ===")
    passed, total = run_io_cases()
    print(f"\nPublic I/O: {passed}/{total} passed")
    if structure_ok and passed == total:
        print("All preliminary public tests passed.")
        raise SystemExit(0)
    raise SystemExit(1)


if __name__ == "__main__":
    main()
