import os
from pathlib import Path
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parents[1] / "app.py")
CONFIG = {
    "SUPABASE_URL": "https://example.supabase.co",
    "SUPABASE_KEY": "test-key",
    "DB_HOST": "example.pooler.supabase.com",
    "POSTGRES_USER": "quiz_reader.example",
    "POSTGRES_PASSWORD": "test-only",
}


class AppTests(unittest.TestCase):
    def test_signed_out_buttons_are_disabled(self):
        with patch.dict(os.environ, CONFIG):
            app = AppTest.from_file(APP, default_timeout=15).run()
            self.assertFalse(app.exception)
            buttons = {button.label: button for button in app.button}
            for label in ["Run SQL", "Save answer", "Load my saved answer"]:
                self.assertTrue(buttons[label].disabled)

    def test_signed_in_query_displays_rows(self):
        with patch.dict(os.environ, CONFIG), patch("services.run_query", return_value=(["name"], [("Campus Tacos",)])) as run:
            app = AppTest.from_file(APP, default_timeout=15)
            app.session_state["token"] = "test-session"
            app.run()
            app.text_area[0].input("SELECT name FROM restaurants;")
            next(b for b in app.button if b.label == "Run SQL").click().run()
            self.assertFalse(app.exception)
            run.assert_called_once_with("test-session", "SELECT name FROM restaurants;")
            self.assertEqual(app.dataframe[-1].value.iloc[0, 0], "Campus Tacos")
