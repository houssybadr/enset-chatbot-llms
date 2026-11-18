# Illustrations du rapport Word

Les fichiers `application_*.jpg` sont des captures réelles de l'application exécutée avec Ollama. Les vues sont cadrées par fonction pour conserver les commandes et le texte utiles. `application_complete.jpg` est la capture de référence du panneau utilisé pour le recadrage de la gestion des conversations.

Les fichiers `preuve_*.jpg` sont des captures d'une vue de lecture locale des réponses et mesures conservées dans `resultats/reponses.json`. Cette vue a été produite par `prepare_report_evidence.py`. Elle identifie le fichier source, les observations et son empreinte. Elle ne relance pas les modèles. Pour le raisonnement de Llama, un extrait continu de la réponse est affiché, et signalé comme tel.

`preuve_verification_code.jpg` montre une vérification supplémentaire de la fonction de Llama ; ses résultats figurent dans `verification_code.json`. La valeur True de la dernière ligne est celle annoncée par le commentaire du modèle, pas la bonne réponse attendue.

Les PNG de ces mêmes noms sont les versions en niveaux de gris insérées dans Word, sans modification des données. Les graphiques `*_nb.png` sont recalculés depuis le CSV archivé par `plot_report.py`, en noir et blanc, à 300 dpi. Les dix mesures initiales restent inchangées.
