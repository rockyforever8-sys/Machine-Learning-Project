from __future__ import annotations

import unittest

from ppap_inbox_triage.pfmea_ap import (
    AP_RANK,
    compare_table_vs_benchmark,
    pfmea_action_priority,
    pfmea_sort_key,
    split_table_actions,
)
from ppap_inbox_triage.quality_analysis import PfmeaRow, _parse_pfmea_rows


class PfmeaActionPriorityTests(unittest.TestCase):
    def test_high_ap_before_medium(self) -> None:
        self.assertEqual(pfmea_action_priority(9, 5, 4), "H")
        self.assertEqual(pfmea_action_priority(7, 6, 4), "H")
        self.assertIn(pfmea_action_priority(5, 4, 4), {"L", "M"})

    def test_ap_sort_key_orders_h_before_m_before_l(self) -> None:
        high = PfmeaRow(
            failure_mode="Porosity in weld",
            severity=9,
            occurrence=5,
            detection=4,
            rpn=180,
            action_priority="H",
            table_actions=("Install venting",),
            benchmark_actions=(),
            comparison_notes=(),
            source_file="pfmea.pdf",
        )
        medium = PfmeaRow(
            failure_mode="Handling scratch",
            severity=5,
            occurrence=6,
            detection=5,
            rpn=150,
            action_priority="M",
            table_actions=("Redesign rack",),
            benchmark_actions=(),
            comparison_notes=(),
            source_file="pfmea.pdf",
        )
        self.assertLess(pfmea_sort_key(high), pfmea_sort_key(medium))
        self.assertEqual(AP_RANK["H"], 0)


class PfmeaTableActionTests(unittest.TestCase):
    def test_split_table_actions_requires_action_verbs(self) -> None:
        self.assertEqual(
            split_table_actions("Install venting and monitor melt temperature profile"),
            ("Install venting and monitor melt temperature profile",),
        )
        self.assertEqual(split_table_actions("192"), ())

    def test_parse_row_with_supplier_action_text(self) -> None:
        text = (
            "Porosity in weld cavity visual escape      8  4  6  192  "
            "Install venting and audit melt temperature profile"
        )
        rows = _parse_pfmea_rows(text, source_file="binder.pdf", page_number=6)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].action_priority, "M")
        self.assertTrue(rows[0].table_actions)
        self.assertTrue(rows[0].benchmark_actions)
        self.assertTrue(rows[0].comparison_notes)

    def test_rows_without_table_actions_are_excluded(self) -> None:
        text = "Dimensional out of tolerance on bore        7  3  5  105"
        rows = _parse_pfmea_rows(text, source_file="binder.pdf", page_number=6)
        self.assertEqual(rows, [])

    def test_compare_notes_flag_gaps(self) -> None:
        notes = compare_table_vs_benchmark(
            table_actions=("Install barcode scanner at setup",),
            benchmark_actions=(
                "Audit melt temperature, injection speed/pressure profile, and venting",
            ),
            failure_mode="Porosity in weld",
            action_priority="H",
        )
        self.assertTrue(any(note.startswith("Gap:") for note in notes))


if __name__ == "__main__":
    unittest.main()
