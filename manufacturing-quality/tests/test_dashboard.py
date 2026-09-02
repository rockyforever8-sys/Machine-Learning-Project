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
        self.assertIn("中文", module.ui_text("en", "language_help"))
        self.assertIn("binder", module.ui_text("en", "layout_help"))
        self.assertIn("散页", module.ui_text("zh", "layout_help"))
        self.assertEqual(module.ui_text("en", "layout_mixed"), "mixed")

    def test_language_buttons_are_in_the_dashboard(self) -> None:
        app_source = (Path(__file__).resolve().parents[1] / "dashboard" / "app.py").read_text(
            encoding="utf-8"
        )
        self.assertIn('_render_language_buttons("sidebar_lang")', app_source)
        self.assertIn("st.radio", app_source)
        self.assertIn('"中文"', app_source)
        self.assertIn("def _render_language_buttons", app_source)
