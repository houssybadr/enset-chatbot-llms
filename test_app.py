"""Vérifications fonctionnelles isolées ; ces données ne servent jamais à l'étude."""
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from streamlit.testing.v1 import AppTest

METRICS = {"Modèle": "modèle-test", "Temps (s)": 1.0, "Tokens": 10,
           "Tokens/s": 10.0, "TTFT (s)": 0.2, "cpu_pct_mean": 5,
           "ram_gb_max": 2, "gpu_pct_mean": None, "vram_mb_max": None}


class ApplicationTests(unittest.TestCase):
    def setUp(self):
        self.models = patch("ollama.list", return_value=SimpleNamespace(models=[SimpleNamespace(model="a"), SimpleNamespace(model="b")]))
        self.hardware = patch("core.resources", return_value=dict(cpu_pct=5, ram_gb=2, ram_pct=20))
        self.generation = patch("core.generate", return_value=("Réponse de test", METRICS))
        self.models.start()
        self.hardware.start()
        self.mock_generate = self.generation.start()
        self.addCleanup(patch.stopall)
        self.app = AppTest.from_file("ENSET_Chatbot.py").run(timeout=20)

    def test_conversation_lifecycle_and_exports(self):
        a = self.app
        a.chat_input[0].set_value("Question test").run()
        first = a.session_state["active"]
        self.assertEqual(len(a.session_state["conversations"][first]["messages"]), 2)
        self.assertEqual(len(a.get("download_button")), 2)
        a.button[0].click().run()
        self.assertEqual(len(a.session_state["conversations"]), 2)
        a.selectbox[0].select_index(0).run()
        self.assertEqual(a.session_state["active"], first)
        self.assertEqual(len(a.chat_message), 2)
        a.button[1].click().run()
        self.assertEqual(len(a.session_state["conversations"]), 1)
        a.button[1].click().run()
        self.assertEqual(len(a.session_state["conversations"]), 1)
        self.assertFalse(a.exception)

    def test_comparison_same_question_and_parameters(self):
        a = self.app
        a.radio[0].set_value("Comparaison des modèles").run()
        a.text_area[0].set_value("Même question")
        a.button[0].click().run()
        calls = self.mock_generate.call_args_list
        self.assertEqual(len(calls), 2)
        self.assertNotEqual(calls[0].args[0], calls[1].args[0])
        self.assertEqual(calls[0].args[1:3], calls[1].args[1:3])
        self.assertEqual(len(a.session_state["comparison"]), 2)
        self.assertFalse(a.exception)

    def test_generation_error_does_not_corrupt_history(self):
        self.mock_generate.side_effect = RuntimeError("Erreur de test")
        a = self.app
        a.chat_input[0].set_value("Question").run()
        self.assertTrue(a.error)
        self.assertEqual(a.session_state["conversations"][a.session_state["active"]]["messages"], [])

    def test_service_unavailable(self):
        with patch("ollama.list", side_effect=ConnectionError("Indisponible")):
            a = AppTest.from_file("ENSET_Chatbot.py").run()
            self.assertIn("inaccessible", a.error[0].value)
            self.assertFalse(a.exception)

    def test_no_models(self):
        with patch("ollama.list", return_value=SimpleNamespace(models=[])):
            a = AppTest.from_file("ENSET_Chatbot.py").run()
            self.assertIn("Aucun modèle", a.warning[0].value)
            self.assertFalse(a.exception)


if __name__ == "__main__":
    unittest.main()
