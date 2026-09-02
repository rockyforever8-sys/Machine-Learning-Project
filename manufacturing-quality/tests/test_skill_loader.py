from __future__ import annotations

import unittest

from ppap_inbox_triage.elements import CRITICAL_ELEMENT_NUMBERS, PPAP_LEVEL_3_ELEMENTS
from ppap_inbox_triage.skill_loader import skill_element_records, skill_metadata, sqe_checks_by_element
from ppap_inbox_triage.sqe_checklist import SQE_VERIFICATION_CHECKS


class SkillRulesLoaderTests(unittest.TestCase):
    def test_loads_eighteen_elements_from_skill(self) -> None:
        records = skill_element_records()
        self.assertEqual(len(records), 18)
        self.assertEqual(len(PPAP_LEVEL_3_ELEMENTS), 18)
        self.assertEqual(PPAP_LEVEL_3_ELEMENTS[5].name, "Process FMEA")
        self.assertEqual(PPAP_LEVEL_3_ELEMENTS[17].name, "Part Submission Warrant")

    def test_critical_elements_come_from_skill(self) -> None:
        meta = skill_metadata()
        self.assertEqual(set(meta["critical_element_numbers"]), {6, 7, 18})
        self.assertEqual(CRITICAL_ELEMENT_NUMBERS, frozenset({6, 7, 18}))
        self.assertTrue(meta["source_path"].endswith("rules.json"))

    def test_sqe_checks_come_from_skill(self) -> None:
        checks = sqe_checks_by_element()
        self.assertEqual(checks[18], SQE_VERIFICATION_CHECKS[18])
        self.assertGreaterEqual(len(checks[6]), 1)
        self.assertIn("PSW", " ".join(checks[18]))


if __name__ == "__main__":
    unittest.main()
