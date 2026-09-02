from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


class DashboardImportTests(unittest.TestCase):
    def test_dashboard_app_imports(self) -> None:
        app_path = Path(__file__).resolve().parents[1] / "dashboard" / "app.py"
        spec = importlib.util.spec_from_file_location("ppap_dashboard", app_path)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertTrue(callable(module.main))

    def test_launch_dashboard_imports(self) -> None:
        launch_path = Path(__file__).resolve().parents[1] / "launch_dashboard.py"
        spec = importlib.util.spec_from_file_location("launch_dashboard", launch_path)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertTrue(callable(module.main))

    def test_i18n_chinese_strings(self) -> None:
        spec = importlib.util.spec_from_file_location(
            "dashboard_i18n",
            Path(__file__).resolve().parents[1] / "dashboard" / "i18n.py",
        )
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertIn("立即分拣", module.ui_text("zh", "run_triage"))
        self.assertEqual(module.ui_text("en", "run_triage"), "Run triage now")
        self.assertEqual(module.element_display_name("zh", 6, "Process FMEA"), "过程FMEA")
        self.assertEqual(module.element_display_name("en", 6, "Process FMEA"), "Process FMEA")
        self.assertEqual(module.element_status_label("zh", "missing"), "缺失")
