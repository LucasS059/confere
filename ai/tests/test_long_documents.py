import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from prepare_long_documents import long_rows
from evaluate_long_documents import gates, full_file_gate, supported_citations
from confere_ai.grounding import judge
from confere_ai.project_review import input_ids
from confere_ai.tokenizer import ByteBPE
from confere_ai.training_data import encode_sample


class LongDocumentsTests(unittest.TestCase):
    def test_full_file_gate_requires_actual_fixture_support(self):
        statuses=["atendido","evidencia_insuficiente","atendido"]
        audit=dict(expected_statuses=statuses,invalid_calls=0)
        rows=[dict(status=s,conflicting_evidence=i==1,evidence=[]) for i,s in enumerate(statuses)]
        self.assertFalse(full_file_gate(dict(requirements=rows),audit))
        phrases=[[("atendido","O projeto inclui testes.")],[("atendido","O projeto inclui backup."),("nao_atendido","O projeto não inclui backup.")],[("atendido","O projeto inclui relatórios.")]]
        for row,pairs in zip(rows,phrases):row["evidence"]=[dict(model_status=s,quote=t) for s,t in pairs]
        self.assertTrue(full_file_gate(dict(requirements=rows),audit))
        self.assertEqual(supported_citations(dict(requirements=rows)),4)
        rows[0]["evidence"][0]["quote"]="Equipe: registro de atividades."
        self.assertFalse(full_file_gate(dict(requirements=rows),audit))
        self.assertEqual(supported_citations(dict(requirements=rows)),3)

    def test_joint_gate_rejects_invalid_output_and_family_regression(self):
        import copy
        docs=dict(total=3,correct=3,valid=3,references=3,families={"grounded_atendido":[1,1],"grounded_nao_atendido":[1,1],"grounded_evidencia_insuficiente":[1,1]})
        before=dict(conversation=dict(total=10,correct=9,families={"conversation_a":[5,5],"conversation_b":[4,5]}),short_documents=docs,long_documents=docs)
        after=copy.deepcopy(before)
        self.assertTrue(all(gates(before,after).values()))
        after["conversation"]["families"]={"conversation_a":[4,5],"conversation_b":[5,5]}
        self.assertFalse(gates(before,after)["conversation"])
        after["long_documents"]["valid"]=2
        self.assertFalse(gates(before,after)["long_documents"])

    def test_budget_polarity_positions_and_split_isolation(self):
        tokenizer=ByteBPE([])
        train=long_rows(tokenizer,"train",108)
        validation=long_rows(tokenizer,"validation",108)
        self.assertFalse({r["project_id"] for r in train}&{r["project_id"] for r in validation})
        self.assertFalse({r["requirement"] for r in train}&{r["requirement"] for r in validation})
        self.assertEqual(train,long_rows(tokenizer,"train",108))
        self.assertEqual(len({r["prompt"] for r in train+validation}),216)
        positions=set()
        for row in train+validation:
            self.assertTrue(judge(row["target"],row)["exact_match"])
            self.assertLessEqual(len(input_ids(row["requirement"],row["units"],tokenizer))+64,1024)
            encode_sample(row,tokenizer,1024)
            target=json.loads(row["target"])
            if target["unit"]:
                text=next(u["text"] for u in row["units"] if u["id"]==target["unit"])
                feature=row["requirement"].removeprefix("O projeto deve incluir ").rstrip(".")
                self.assertIn(feature,text)
                if target["status"]=="nao_atendido":self.assertTrue("não" in text or "ausência" in text or "Não existe" in text)
                positions.add(target["unit"])
        self.assertEqual(positions,{"page:1","page:2","page:3","page:4"})
