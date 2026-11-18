"""Étude reproductible : cinq tâches, deux modèles, mesures non simulées."""
import json
import platform
import subprocess
from pathlib import Path
from datetime import datetime, timezone

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import ollama
import pandas as pd
import psutil
from core import generate, resources

QUESTIONS = [
    ("Concept", "Explique en français la différence entre RAM et stockage en trois phrases."),
    ("Raisonnement", "Un livre et un stylo coûtent 22 dirhams. Le livre coûte 18 dirhams de plus que le stylo. Quel est le prix du stylo ? Explique brièvement."),
    ("Code Python", "Écris une fonction Python est_palindrome(texte) qui ignore les espaces et la casse. Donne deux exemples de test."),
    ("Synthèse", "Résume en deux phrases : Une école installe des panneaux solaires pour réduire sa facture. Les travaux dureront trois mois. Les cours continueront pendant les travaux. Les économies financeront du matériel pédagogique."),
    ("Traduction", "Traduis uniquement en anglais : Les étudiants travaillent ensemble pour concevoir une application simple et utile."),
]
OPTIONS = dict(temperature=0.7, top_k=40, top_p=0.9, num_predict=512, seed=42, num_ctx=2048)


def main():
    out = Path(__file__).parent / "resultats"
    out.mkdir(exist_ok=True)
    hardware = subprocess.check_output(["powershell", "-NoProfile", "-Command",
        "Get-CimInstance Win32_Processor | Select-Object Name,NumberOfCores,NumberOfLogicalProcessors | ConvertTo-Json; Get-CimInstance Win32_VideoController | Select-Object Name,AdapterRAM | ConvertTo-Json"], text=True)
    metadata = dict(date=datetime.now(timezone.utc).isoformat(), system=platform.platform(),
                    ram_gb=psutil.virtual_memory().total/1024**3, hardware=hardware, resources=resources(),
                    options=OPTIONS, models=[m.model_dump(mode="json") for m in ollama.list().models],
                    protocol="Un passage par question et modèle, contexte neuf, modèles séquentiels, échauffement avant chaque série. Échantillons système espacés d'au moins 0,4 s, avec mesure CPU sur 0,1 s et interrogation GPU NVIDIA. Pas de moyenne sur répétitions.")
    (out / "conditions.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    records = []
    for model in ["llama3.2:latest", "qwen:0.5b"]:
        ollama.chat(model=model, messages=[dict(role="user", content="Bonjour")], options=dict(OPTIONS, num_predict=8), keep_alive=0)
        # Charger puis échauffer le modèle ; ce coût est exclu des cinq mesures.
        ollama.chat(model=model, messages=[dict(role="user", content="Bonjour")], options=dict(OPTIONS, num_predict=8))
        for task, question in QUESTIONS:
            print(model, task, flush=True)
            answer, metrics = generate(model, [dict(role="user", content=question)], OPTIONS)
            records.append(dict(Tâche=task, Question=question, Réponse=answer, **metrics))
            (out / "reponses.json").write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
            pd.DataFrame(records).drop(columns=["Question", "Réponse"]).to_csv(out / "mesures.csv", index=False, encoding="utf-8-sig")
        ollama.generate(model=model, keep_alive=0)
    data = pd.DataFrame(records)
    for field, filename in [("Temps (s)", "temps.png"), ("Tokens/s", "vitesse.png"), ("ram_gb_max", "ram.png"), ("TTFT (s)", "ttft.png")]:
        ax = data.pivot(index="Tâche", columns="Modèle", values=field).plot.bar(figsize=(9,4), color=["#32665c", "#c78c51"])
        ax.set_ylabel(field)
        ax.set_xlabel("")
        plt.xticks(rotation=15)
        plt.tight_layout()
        plt.savefig(out / filename, dpi=160)
        plt.close()


if __name__ == "__main__":
    main()
