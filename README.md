# ENSET Chatbot — Amélioration et évaluation de LLMs locaux

Application Streamlit issue du script fourni, conservé dans `original/`. Périmètre : les cinq améliorations du TP, sans service distant de génération.

## Installer et lancer (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
ollama pull llama3.2
ollama pull qwen:0.5b
.venv\Scripts\python -m streamlit run ENSET_Chatbot.py
```

Ollama doit être démarré (application Ollama ou `ollama serve`). Ouvrir l'adresse locale affichée. Les conversations restent disponibles pendant la session Streamlit ; elles ne sont pas sauvegardées après sa fermeture. Les exports TXT et JSON permettent de les conserver.

## Reproduire l'étude

```powershell
.venv\Scripts\python experiment.py
```

Cinq tâches : concept, raisonnement, code Python, synthèse et traduction. Les réponses brutes, les conditions matérielles, le tableau CSV et les graphiques se trouvent dans `resultats/`. Les deux modèles tournent successivement avec des paramètres identiques. Les mesures CPU/RAM concernent le système entier. GPU et mémoire GPU sont disponibles via `nvidia-smi` si le matériel le permet ; sinon l'interface l'indique explicitement. Le TTFT mesure le premier fragment de texte reçu côté client. Le débit utilise `eval_count / eval_duration × 10^9`, conformément à l'API Ollama : https://github.com/ollama/ollama/blob/main/docs/api.md.

## Architecture

- `ENSET_Chatbot.py` : interface, session, conversations, comparaison, exports.
- `core.py` : génération en streaming, durée, TTFT et échantillonnage matériel.
- `experiment.py` : protocole reproductible et graphiques du rapport.
- `original/ENSET_Chatbot.py` : base initiale inchangée.
- `Rapport_TP_LLMs_Houssy_Badr.docx` : rapport technique à rendre, en Times New Roman, avec captures de l’interface en couleur et mise en page en noir et blanc.
- `rapport_assets/` : captures lisibles des fonctionnalités, preuves des analyses et graphiques du rapport.

Le rapport à rendre est désormais **Rapport_TP_LLMs_Houssy_Badr.docx**. Il remplace la première version PDF. Les exigences de remise et les corrections de présentation sont conservées dans `CONSIGNES_RAPPORT.md`.

## Vérifications et rapport

```powershell
.venv\Scripts\python -m unittest test_app -v
.venv\Scripts\python -m pip install -r requirements-rapport.txt
.venv\Scripts\python plot_report.py
.venv\Scripts\python build_report_word.py
```

Les cinq tests vérifient les conversations et exports, la comparaison avec paramètres identiques, les erreurs de génération, l'absence de service et l'absence de modèles. Leurs réponses de test sont isolées des données expérimentales. Le rapport distingue les captures de l'application, les captures de lecture des réponses archivées et la vérification supplémentaire du code. Chaque analyse de tâche renvoie aux réponses exactes dont elle parle. Les captures de l’interface sont en couleur ; les graphiques et les captures de lecture des résultats restent en niveaux de gris. Les captures sources sont aussi conservées.

Étude effectuée le 18 novembre 2026 : cinq questions par modèle, après échauffement. Durées moyennes observées : Llama 3.2, 1,048 s ; Qwen 0.5B, 0,364 s. Qwen est plus rapide mais échoue sur plusieurs tâches ; consulter le rapport pour l'analyse et les limites. Ces chiffres ne sont pas une garantie pour une autre machine.

Le dossier `.venv` est temporaire, exclu de Git et peut être supprimé après arrêt de l'application. Le recréer avec les commandes ci-dessus pour une nouvelle exécution.
