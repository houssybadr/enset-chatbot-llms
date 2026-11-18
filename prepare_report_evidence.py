"""Prépare des vues de lecture des données réelles, sans relancer les modèles."""
import csv
import hashlib
import html
import json
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "tmp" / "rapport"
OUT.mkdir(parents=True, exist_ok=True)
records = json.loads((ROOT / "resultats/reponses.json").read_text(encoding="utf-8"))
digest = hashlib.sha256((ROOT / "resultats/reponses.json").read_bytes()).hexdigest()
style = """body{margin:0;background:white;color:black;font:28px 'Times New Roman',serif;line-height:1.25}main{padding:32px 40px}h1{font-size:38px;margin:0 0 10px}h2{font-size:32px;margin:0 0 12px}.source{font-size:22px;margin:0 0 20px;overflow-wrap:anywhere}.prompt{border-top:2px solid black;border-bottom:2px solid black;padding:15px 0;margin-bottom:22px}.columns{display:grid;grid-template-columns:1fr 1fr;gap:36px}article{min-width:0}.answer{white-space:pre-wrap;overflow-wrap:anywhere;font:28px/1.25 'Times New Roman',serif;margin:0}.code{font:23px/1.3 Consolas,monospace}.metrics{font-size:23px;margin-top:16px;border-top:1px solid #999;padding-top:8px}table{width:100%;border-collapse:collapse;font-size:25px}th,td{border:1px solid #777;padding:10px;text-align:left}th{background:#eee}.notice{font-size:23px;margin-top:18px}footer{margin-top:22px;font-size:20px;border-top:1px solid black;padding-top:8px}"""
slugs = ["concept", "raisonnement", "code", "synthese", "traduction"]
for index, slug in enumerate(slugs):
    pair = [records[index], records[index + 5]]
    articles = []
    for row in pair:
        answer = row["Réponse"]
        label = "Réponse complète enregistrée"
        if slug == "raisonnement" and "llama" in row["Modèle"]:
            answer = answer[answer.index("x + (x + 18) = 22"):]
            label = "Extrait exact de la réponse enregistrée"
        cls = "answer code" if slug == "code" else "answer"
        articles.append(f'<article><h2>{html.escape(row["Modèle"])}</h2><p class="source">{label}</p><pre class="{cls}">{html.escape(answer)}</pre><div class="metrics">Temps {row["Temps (s)"]:.3f} s · {row["Tokens"]} tokens<br>Débit {row["Tokens/s"]:.1f} tokens/s · TTFT {row["TTFT (s)"]:.3f} s</div></article>')
    content = f'<h1>{html.escape(pair[0]["Tâche"])} — réponses enregistrées</h1><p class="source">Source : resultats/reponses.json · Observations {index+1} et {index+6} du 18 novembre 2026</p><div class="prompt"><b>Question</b><br>{html.escape(pair[0]["Question"])}</div><div class="columns">{"".join(articles)}</div><footer>Vue de lecture du fichier archivé. Aucune nouvelle génération. SHA-256 : {digest[:24]}…</footer>'
    (OUT / f"{slug}.html").write_text(f'<!doctype html><html lang="fr"><meta charset="utf-8"><title>Lecture des résultats — {slug}</title><style>{style}</style><main>{content}</main></html>', encoding="utf-8")

headers = ["Tâche", "Modèle", "Temps (s)", "Tokens", "Tokens/s", "TTFT (s)"]
table = "<table><tr>" + "".join(f"<th>{html.escape(h)}</th>" for h in headers) + "</tr>"
for row in records:
    values = [row["Tâche"], row["Modèle"],f'{row["Temps (s)"]:.3f}',row["Tokens"],f'{row["Tokens/s"]:.1f}',f'{row["TTFT (s)"]:.3f}']
    table += "<tr>" + "".join(f"<td>{html.escape(str(v))}</td>" for v in values) + "</tr>"
table += "</table>"
(OUT / "mesures.html").write_text(f'<!doctype html><html lang="fr"><meta charset="utf-8"><title>Mesures enregistrées</title><style>{style}</style><main><h1>Mesures expérimentales enregistrées</h1><p class="source">Source : resultats/reponses.json · Dix observations du 18 novembre 2026</p>{table}<footer>Lecture des valeurs enregistrées, arrondies pour affichage. Fichier CSV correspondant : resultats/mesures.csv.</footer></main></html>', encoding="utf-8")

# Vérification ciblée du code de Llama, relu avant exécution : aucun accès aux fichiers ni au réseau.
import re
def est_palindrome(texte):
    texte = re.sub(r'\s+', '', texte).lower()
    return texte == texte[::-1]
checks = [("Kayak",True),("Esope reste ici et se repose",True),("Bonjour",False),("Madame, je suis une letrine.",True)]
verification = [dict(texte=s, attendu=expected, obtenu=est_palindrome(s)) for s,expected in checks]
(ROOT / "rapport_assets/verification_code.json").write_text(json.dumps(verification, ensure_ascii=False, indent=2), encoding="utf-8")
rows = ''.join(f'<tr><td>{html.escape(r["texte"])}</td><td>{r["attendu"]}</td><td>{r["obtenu"]}</td></tr>' for r in verification)
(OUT / "verification_code.html").write_text(f'<!doctype html><html lang="fr"><meta charset="utf-8"><title>Vérification du code Python</title><style>{style}</style><main><h1>Vérification de la fonction de Llama</h1><p class="source">Fonction reprise de la réponse archivée de Llama 3.2 · Exécution locale supplémentaire</p><pre class="answer code">{html.escape(records[2]["Réponse"].split("# Exemples de test")[0])}</pre><br><table><tr><th>Chaîne testée</th><th>Valeur attendue ou annoncée</th><th>Résultat obtenu</th></tr>{rows}</table><p class="notice">Pour la dernière chaîne, True est la valeur annoncée dans le commentaire du modèle. La fonction retourne False : le commentaire de son exemple est donc incorrect.</p><footer>Résultats sauvegardés dans rapport_assets/verification_code.json. Les mesures de performance initiales restent inchangées.</footer></main></html>', encoding="utf-8")
print("Vues créées dans",OUT)
