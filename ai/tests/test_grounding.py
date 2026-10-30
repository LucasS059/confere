import json
import unittest
from confere_ai.grounding import resolve, judge, prompt_for


class GroundingTests(unittest.TestCase):
    def setUp(self):
        self.units = [{"id":"page:1", "text":"O projeto inclui testes."}, {"id":"page:2", "text":"Tema: biblioteca."}]

    def test_quote_is_from_source_and_extra_model_quote_is_rejected(self):
        raw=json.dumps({"status":"atendido","unit":"page:1"})
        result=resolve(raw,"projeto.pdf",self.units)
        self.assertEqual(result["result"]["evidence"][0]["quote"],self.units[0]["text"])
        bad=json.dumps({"status":"atendido","unit":"page:1","quote":"inventada"})
        self.assertFalse(resolve(bad,"projeto.pdf",self.units)["valid_format"])

    def test_unknown_or_ambiguous_reference_fails_closed(self):
        for units,unit in ((self.units,"page:3"),(self.units+self.units,"page:1")):
            result=resolve(json.dumps({"status":"atendido","unit":unit}),"projeto.pdf",units)
            self.assertFalse(result["reference_valid"])
            self.assertEqual(result["result"]["status"],"evidencia_insuficiente")
            self.assertEqual(result["result"]["evidence"],[])

    def test_wrong_status_is_not_counted_as_correct_even_with_real_quote(self):
        expected=json.dumps({"status":"nao_atendido","unit":"page:1"})
        row={"document":"projeto.pdf","units":self.units,"target":expected}
        result=judge(json.dumps({"status":"atendido","unit":"page:1"}),row)
        self.assertTrue(result["reference_valid"])
        self.assertFalse(result["status_correct"])
        self.assertFalse(result["exact_match"])

    def test_invalid_outputs_and_null_evidence_are_checked(self):
        for raw in ('[]','null','texto','{"status":"atendido","unit":null}', '{"status":"evidencia_insuficiente","unit":"page:1"}', '{"status":"atendido","status":"nao_atendido","unit":"page:1"}'):
            self.assertFalse(resolve(raw,"p.pdf",self.units)["valid_format"])
        result=resolve('{"status":"evidencia_insuficiente","unit":null}',"p.pdf",self.units)
        self.assertTrue(result["reference_valid"])
        self.assertEqual(result["result"]["evidence"],[])

    def test_prompt_retains_unit_identity_and_text(self):
        prompt=prompt_for("Incluir testes",self.units)
        self.assertIn("[page:1] O projeto inclui testes.",prompt)
