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


if __name__ == "__main__":
    unittest.main()
