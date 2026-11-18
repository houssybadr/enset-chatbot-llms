Amélioration et évaluation d’un chatbot basé sur des LLMs locaux

Compte rendu de travaux pratiques

ENSET

Réalisé par Houssy Badr

Enseignant Pr OUHMIDA

18 novembre 2026

1 Présentation du travail

Le point de départ de ce TP est une application Streamlit qui permet de discuter avec un modèle local. Le script fourni propose déjà le choix du modèle, les paramètres de génération et l’affichage progressif des réponses. J’ai repris cette base pour ajouter la gestion de plusieurs conversations, la comparaison de deux modèles et les mesures demandées dans le sujet.

Les essais portent sur Llama 3.2 et Qwen 0.5B. Sur les cinq questions retenues, Qwen répond plus vite et occupe moins de mémoire GPU. Ses réponses sont toutefois moins fiables pour le raisonnement, le code et la synthèse. Le rapport présente les résultats mesurés et les réponses qui permettent de faire ce constat.

Organisation de l’application

L’interface et les conversations restent dans ENSET_Chatbot.py. Les appels à Ollama et les mesures sont regroupés dans core.py. Le script experiment.py envoie les cinq questions aux deux modèles et enregistre les résultats. Le script de départ est conservé sans modification dans le dossier original.

Lorsqu’une question est envoyée, l’interface appelle Ollama sur la machine. Les fragments reçus sont affichés au fur et à mesure. En parallèle, un suivi relève le CPU, la RAM et, lorsque cela est possible, le GPU. Les résultats sont ensuite ajoutés aux tableaux de l’application.

L’application récupère la liste des modèles réellement installés. Si Ollama est inaccessible ou si la génération échoue, elle affiche un message d’erreur. Un indicateur reste visible pendant l’attente de la réponse. Les deux modes sont accessibles depuis la barre latérale.

2 Gestion des conversations

Le bouton « Nouvelle conversation » ouvre une discussion vide. Les discussions précédentes restent accessibles dans la liste de la session. Une conversation sélectionnée peut être supprimée ou téléchargée en TXT ou en JSON. Ces exports permettent de conserver son contenu après la fermeture de la session.

Figure 1  Dialogue réel avec Qwen dans l’application

Figure 2  Commandes de création de suppression et d’export

La figure 2 montre les deux formats d’export et le modèle utilisé. Les captures de cette partie illustrent des essais de l’interface. Les chiffres de l’étude comparative proviennent, eux, des dix observations enregistrées dans le dossier resultats.

3 Comparaison et consultation de l’historique

Figure 3  Deux conversations conservées dans la même session

La liste de la figure 3 permet de revenir à la première discussion après en avoir créé une seconde. Le contenu est conservé dans st.session_state, pendant la session Streamlit. Il n’y a pas de base de données de conversations.

Figure 4  Question commune et réponses affichées sur deux colonnes

Dans le mode comparaison, l’utilisateur choisit deux modèles distincts parmi ceux qui sont installés. La même question et les mêmes paramètres sont transmis aux deux modèles. Les générations se font l’une après l’autre pour limiter leur concurrence sur le matériel. La figure 4 montre un essai de traduction réalisé dans ce mode.

4 Matériel et protocole expérimental

Ces informations figurent dans resultats/conditions.json. La capacité mémoire de la carte NVIDIA a été relevée avec nvidia-smi. Les valeurs de RAM exprimées en Go dans l’interface sont calculées sur une base de 1 024 et correspondent donc à des Gio.

Le nom Qwen 0.5B est celui du sujet et de l’étiquette installée. Ollama annonce 620 millions de paramètres pour ce fichier. Les deux modèles n’ont ni la même taille ni la même quantification ; la comparaison décrit donc ces versions précises.

Les réglages sont identiques : température de 0,7, top-k de 40, top-p de 0,9, maximum de 512 tokens, contexte de 2 048 tokens et graine fixée à 42. Chaque question est envoyée dans un contexte neuf. Un échauffement précède chaque série, puis le modèle précédent est déchargé avant de passer au suivant.

J’ai retenu cinq tâches : expliquer la différence entre RAM et stockage, résoudre un petit problème de prix, écrire une fonction Python, résumer un texte et traduire une phrase. Les formulations exactes apparaissent dans les captures des réponses. Chaque question a été exécutée une fois par modèle, dans le même ordre, Llama avant Qwen.

Lecture des mesures

Le temps de réponse va du début de l’appel à la fin du flux. Le TTFT correspond à l’attente avant le premier fragment de texte reçu. Le nombre de tokens vient du compteur eval_count d’Ollama. Le débit est calculé en divisant ce nombre par eval_duration converti en secondes. Il porte sur la génération, alors que le temps total comprend aussi le traitement de la question.

5 Temps de réponse observés

Tableau 1  Les dix générations mesurées le 18 novembre 2026

Figure 5  Durée totale de chaque réponse après échauffement

Qwen a le temps le plus faible pour chacune des cinq questions. Sa moyenne est de 0,364 s, contre 1,048 s pour Llama. L’écart change selon la tâche : il est d’environ 1,33 s pour le raisonnement, mais de 0,10 s pour la traduction. Les réponses ne sont pas toutes aussi longues ni aussi pertinentes, ce qui compte dans l’interprétation de ces durées.

6 Débit et attente du premier fragment

Figure 6  Vitesse de génération calculée avec les compteurs Ollama

Qwen produit en moyenne 395,9 tokens par seconde, contre 118,9 pour Llama. Il est donc environ 3,3 fois plus rapide sur cet indicateur. Ces valeurs sont les moyennes des cinq débits. Un débit élevé renseigne sur la vitesse du modèle, mais ne permet pas de juger si sa réponse résout la question.

Figure 7  Délai avant le premier fragment de texte reçu

Le premier fragment arrive en moyenne après 0,098 s pour Qwen et 0,126 s pour Llama. L’écart est moins marqué que pour le débit. Ces mesures ont été prises après échauffement. Lors d’un premier appel à un modèle déchargé, il faut aussi attendre son chargement ; les captures fonctionnelles peuvent donc afficher un temps supérieur à celui de cette série.

Les dix valeurs sont lisibles dans le tableau 1 et dans le fichier mesures.csv. La capture de la figure 16, en fin de rapport, montre également leur lecture à partir des données archivées.

7 Utilisation des ressources

Tableau 2  Moyenne des cinq observations pour chaque modèle

Figure 8  Comparaison des pics de mémoire relevés pendant les réponses

L’écart le plus net concerne la mémoire GPU : le pic moyen est d’environ 3 115 Mio pour Llama, contre 1 413 Mio pour Qwen. La RAM système est plus proche, avec environ 9,07 Gio contre 8,77 Gio. Ces chiffres incluent les autres logiciels présents sur le poste ; ils ne correspondent pas à la mémoire du seul modèle.

Figure 9  Affichage du CPU de la RAM et du GPU dans l’application

Le CPU moyen relevé est plus élevé pour Qwen, à 26,2 % contre 14,6 %. Il faut rester prudent : plusieurs réponses de Qwen durent moins d’une demi-seconde et ne donnent qu’un seul échantillon. Le suivi espace les relevés d’au moins 0,4 s et mesure le CPU sur 0,1 s. Il peut manquer des pics. Ces valeurs ne suffisent donc pas pour comparer l’énergie consommée ou la charge totale des deux modèles.

8 Explication de la RAM et du stockage

La première question demande une explication en français, en trois phrases. La capture ci-dessous reproduit les réponses enregistrées lors de l’étude. Les vues de lecture des figures 10 à 12 et 14 à 16 utilisent directement reponses.json : elles permettent de consulter les textes d’origine sans relancer les modèles.

Figure 10  Réponses archivées à la question sur la RAM et le stockage

Llama distingue bien la mémoire temporaire du stockage persistant. Sa réponse respecte les trois phrases demandées. Une partie reste inexacte : le lancement d’une nouvelle tâche n’efface pas automatiquement les données de la RAM. L’explication est donc utilisable comme point de départ, mais cette phrase doit être corrigée.

Qwen commence par deux phrases peu compréhensibles et insère des caractères chinois, puis termine en anglais. La dernière phrase exprime la différence entre temporaire et permanent, mais l’ensemble ne constitue pas une explication claire en français. Il a répondu en 0,494 s, contre 1,573 s pour Llama ; ici, le gain de temps s’accompagne d’une baisse nette de qualité.

9 Résolution du problème de prix

Figure 11  Calcul de Llama et réponse hors sujet de Qwen dans le fichier archivé

Le stylo coûte 2 dirhams. Si son prix est x, celui du livre est x + 18. La somme donne 2x + 18 = 22, donc x = 2. La figure 11 montre que Llama suit ce calcul et arrive à la bonne valeur. Pour garder le calcul lisible, seule la fin de sa réponse est affichée dans cette vue ; la réponse complète reste dans le fichier source.

Qwen parle de l’architecture et des performances d’un stylo, sans utiliser les deux prix du problème. Il ne donne pas de solution. Sa durée est pourtant quatre fois plus courte environ, à 0,435 s contre 1,763 s. Ce cas montre pourquoi la durée ne doit pas être utilisée seule pour choisir un modèle.

10 Génération de code Python

Figure 12  Fonctions et exemples proposés pour la question Python

Llama propose une fonction est_palindrome. Elle retire les espaces avec une expression régulière, transforme le texte en minuscules et le compare à son inverse. Cela répond à la consigne. Le premier exemple contient cependant un commentaire erroné : la chaîne « Madame, je suis une letrine. » n’est pas un palindrome, alors que le modèle annonce True.

Qwen utilise le nom is_palindrome sans définir la fonction. Le bloc de code ne peut donc pas être exécuté tel quel. Il annonce aussi une valeur 1 sans la justifier et donne cinq textes d’exemple alors que deux tests étaient demandés. Sa réponse est plus longue en tokens que celle de Llama, mais elle reste incomplète.

11 Vérification de la fonction proposée

Figure 13  Exécution locale de la fonction de Llama sur quatre chaînes

J’ai vérifié séparément la fonction de Llama sur deux palindromes, un mot ordinaire et la chaîne de son premier exemple. Elle renvoie les bonnes valeurs pour les trois premiers cas. Pour la dernière chaîne, elle renvoie False : l’erreur vient du commentaire généré, pas du mécanisme de comparaison utilisé par la fonction.

Cette vérification complète la lecture du code. Les résultats sont conservés dans rapport_assets/verification_code.json. Elle n’a pas servi à recalculer les temps du tableau 1, qui correspondent uniquement aux dix générations initiales.

Pour cette tâche, Llama est le meilleur des deux modèles testés, mais ses exemples doivent être exécutés avant d’être repris. Qwen ne fournit pas le code demandé. Une réponse rapide ou bien présentée ne dispense donc pas de vérifier qu’une fonction existe et qu’elle passe des tests simples.

12 Synthèse et traduction

Figure 14  Réponses archivées à la demande de synthèse en deux phrases

Llama rassemble les informations dans deux phrases et conserve la durée des travaux ainsi que le maintien des cours. Il ajoute toutefois des formulations sur les perturbations de l’enseignement qui ne figurent pas explicitement dans le texte. Qwen recopie les quatre phrases du départ. Les informations restent présentes, mais la consigne de synthèse en deux phrases n’est pas respectée.

Figure 15  Traductions enregistrées pour la même phrase française

Les deux traductions restent compréhensibles et proches du sens demandé. Llama utilise « design » pour « concevoir », ce qui est plus direct que « develop », choisi par Qwen. Sur cette tâche courte, Qwen fournit une réponse acceptable en 0,129 s, contre 0,227 s pour Llama.

13 Vérification des valeurs et limites de l’étude

Figure 16  Lecture des dix mesures dans le fichier de résultats archivé

La capture ci-dessus permet de retrouver les valeurs du tableau 1. Les graphiques sont calculés à partir de ces mêmes observations. Les arrondis servent seulement à rendre les tableaux lisibles ; les fichiers JSON et CSV gardent les valeurs mesurées.

Le classement de vitesse est le même pour les cinq questions, mais cela ne prouve pas qu’il sera identique pour toutes les utilisations. Une seule génération a été réalisée pour chaque question et chaque modèle. L’ordre des modèles est fixe, et les autres logiciels du poste peuvent influencer les ressources relevées.

Les compteurs Ollama donnent un débit de génération, tandis que le TTFT est mesuré du côté de l’application, au premier fragment reçu. Ce fragment peut contenir plusieurs tokens. Il s’agit donc d’une approximation du temps au premier token, et non d’une mesure interne du moteur.

Les essais de l’interface et la vérification du code ont été réalisés séparément. Ils illustrent les fonctionnalités ou vérifient une erreur précise ; ils ne remplacent pas les observations du protocole comparatif.

14 Bilan et choix du modèle

Sur ce poste, Qwen 0.5B est le plus rapide des deux modèles. Il présente le temps de réponse le plus faible pour les cinq questions et le débit moyen le plus élevé. Son occupation de la mémoire GPU est aussi nettement plus faible. Ces résultats en font une option intéressante lorsque la mémoire disponible est limitée.

Je le réserverais cependant à des tâches simples dont la réponse peut être vérifiée facilement. La traduction testée est acceptable, mais le raisonnement, le code et la synthèse montrent des limites importantes. Pour ces usages, Llama 3.2 offre des réponses plus utiles dans ce corpus, avec un coût mémoire plus élevé. Il reste nécessaire de contrôler ses explications et ses exemples Python.

Les écarts ne sont pas constants en valeur : ils changent avec la question et la longueur de la réponse. Le choix dépend donc de la tâche, de la mémoire disponible et du niveau d’erreur acceptable. Une série de tests répétée sur un corpus plus large serait nécessaire avant de tirer une recommandation générale.

Vérifications de l’application

Les cinq tests fonctionnels de l’application passent. Ils couvrent la gestion des conversations et la présence des exports, l’envoi des mêmes paramètres aux deux modèles, une erreur de génération, l’absence de service Ollama et l’absence de modèles installés. Les réponses utilisées dans ces tests sont isolées des mesures expérimentales. Les captures de l’interface montrent également son exécution avec les modèles locaux.

Fichiers remis

Le projet contient l’application, requirements.txt, les instructions d’installation, le script initial, les données expérimentales, les captures et ce rapport Word. Les consignes de remise sont conservées dans CONSIGNES_RAPPORT.md. Les environnements Python utilisés pour les essais et la préparation du rapport sont temporaires et sont nettoyés après vérification.

Sources

Sujet du TP de Pr OUHMIDA : TP_Ameliorations_LLMs.pdf. Script initial : ENSET_Chatbot.py. Mesures et réponses : resultats/conditions.json, resultats/mesures.csv et resultats/reponses.json, relevés le 18 novembre 2026. Documentation des compteurs Ollama : github.com/ollama/ollama/blob/main/docs/api.md.