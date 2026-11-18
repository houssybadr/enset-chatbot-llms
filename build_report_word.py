"""Rapport Word en Times New Roman à partir des mesures et captures archivées."""
import json
from pathlib import Path
from statistics import mean
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from PIL import Image

ROOT = Path(__file__).parent
ASSETS = ROOT/'rapport_assets'
records = json.loads((ROOT/'resultats/reponses.json').read_text(encoding='utf-8'))
document = Document()
section = document.sections[0]
section.page_width, section.page_height = Inches(8.5), Inches(11)
section.top_margin = section.bottom_margin = Inches(.72)
section.left_margin = section.right_margin = Inches(.75)
section.footer_distance = Inches(.3)
for style in document.styles:
    if style.type in (1,2):
        style.font.name = 'Times New Roman'
        style.font.color.rgb = RGBColor(0,0,0)
        rpr = style.element.get_or_add_rPr()
        fonts = rpr.find(qn('w:rFonts'))
        if fonts is None:
            fonts=OxmlElement('w:rFonts');rpr.insert(0,fonts)
        for key in ['ascii','hAnsi','eastAsia','cs']:
            fonts.set(qn('w:'+key),'Times New Roman')
        for key in ['asciiTheme','hAnsiTheme','eastAsiaTheme','cstheme']:
            fonts.attrib.pop(qn('w:'+key),None)
        for border in list(style.element.iter(qn('w:pBdr'))):
            border.getparent().remove(border)
normal=document.styles['Normal']
normal.font.size=Pt(12)
normal.paragraph_format.line_spacing=1.12
normal.paragraph_format.space_after=Pt(7)
normal.paragraph_format.widow_control=True
for name,size in [('Title',19),('Heading 1',15),('Heading 2',13),('Caption',10.5)]:
    style=document.styles[name]
    style.font.size=Pt(size)
    style.font.bold=name!='Caption'
    style.paragraph_format.space_before=Pt(10 if name.startswith('Heading') else 0)
    style.paragraph_format.space_after=Pt(8)
    style.paragraph_format.keep_with_next=name!='Caption'
document.styles['Caption'].font.italic=True
document.styles['Caption'].paragraph_format.line_spacing=1.0
settings=document.settings.element
compression=OxmlElement('w:doNotAutoCompressPictures');settings.append(compression)
document.core_properties.author='Houssy Badr'
document.core_properties.title='Amélioration et évaluation d’un chatbot basé sur des LLMs locaux'
document.core_properties.subject='Compte rendu du TP de Pr OUHMIDA'
document.core_properties.keywords='Streamlit, Ollama, Llama 3.2, Qwen 0.5B'
footer=section.footer.paragraphs[0]
footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
footer.add_run('Page ').font.size=Pt(10)
field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');footer._p.append(field)
outline=[]


def p(text, style=None):
    para=document.add_paragraph(text,style)
    if style is None:
        para.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
    outline.append(text)
    return para


def h(text,level=1):
    p(text,'Heading '+str(level))


def page():
    document.add_page_break()


def picture(name, caption, width=7, max_height=None):
    file=ASSETS/name
    im=Image.open(file)
    if max_height:
        width=min(width,max_height*im.width/im.height)
    para=document.add_paragraph()
    para.alignment=WD_ALIGN_PARAGRAPH.CENTER
    para.paragraph_format.space_after=Pt(3)
    para.paragraph_format.keep_with_next=True
    run=para.add_run()
    drawing=run.add_picture(str(file),width=Inches(width))
    drawing._inline.docPr.set('descr',caption)
    p(caption,'Caption')


def table(headers,rows,widths):
    tbl=document.add_table(rows=1,cols=len(headers))
    tbl.alignment=WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit=False
    pr=tbl._tbl.tblPr
    borders=OxmlElement('w:tblBorders')
    for side in ['top','left','bottom','right','insideH','insideV']:
        edge=OxmlElement('w:'+side);edge.set(qn('w:val'),'single');edge.set(qn('w:sz'),'5');edge.set(qn('w:color'),'D9D9D9');borders.append(edge)
    pr.append(borders)
    repeat=OxmlElement('w:tblHeader');tbl.rows[0]._tr.get_or_add_trPr().append(repeat)
    for row_values,row in [(headers,tbl.rows[0])]+[(values,tbl.add_row()) for values in rows]:
        for i,(value,cell) in enumerate(zip(row_values,row.cells)):
            cell.width=Inches(widths[i])
            cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            cp=cell._tc.get_or_add_tcPr()
            margins=OxmlElement('w:tcMar')
            for side in ['top','left','bottom','right']:
                el=OxmlElement('w:'+side);el.set(qn('w:w'),'90');el.set(qn('w:type'),'dxa');margins.append(el)
            cp.append(margins)
            para=cell.paragraphs[0]
            para.paragraph_format.space_after=Pt(0)
            para.paragraph_format.line_spacing=1.05
            para.alignment=WD_ALIGN_PARAGRAPH.LEFT if i==0 else WD_ALIGN_PARAGRAPH.CENTER
            run=para.add_run(str(value));run.font.size=Pt(10.5 if row is tbl.rows[0] else 11)
        cant=OxmlElement('w:cantSplit');row._tr.get_or_add_trPr().append(cant)
    for cell in tbl.rows[0].cells:
        shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'EEEEEE');cell._tc.get_or_add_tcPr().append(shade)
        for run in cell.paragraphs[0].runs:
            run.bold=True
    for col,w in zip(tbl.columns,widths):col.width=Inches(w)
    document.add_paragraph().paragraph_format.space_after=Pt(0)


def short(model):
    return 'Llama 3.2' if model.startswith('llama') else 'Qwen 0.5B'


title=p('Amélioration et évaluation d’un chatbot basé sur des LLMs locaux','Title')
title.alignment=WD_ALIGN_PARAGRAPH.CENTER
for line in ['Compte rendu de travaux pratiques','ENSET','Réalisé par Houssy Badr','Enseignant Pr OUHMIDA','18 novembre 2026']:
    para=p(line);para.alignment=WD_ALIGN_PARAGRAPH.CENTER;para.paragraph_format.space_after=Pt(4)
h('1 Présentation du travail')
p('Le point de départ de ce TP est une application Streamlit qui permet de discuter avec un modèle local. Le script fourni propose déjà le choix du modèle, les paramètres de génération et l’affichage progressif des réponses. J’ai repris cette base pour ajouter la gestion de plusieurs conversations, la comparaison de deux modèles et les mesures demandées dans le sujet.')
p('Les essais portent sur Llama 3.2 et Qwen 0.5B. Sur les cinq questions retenues, Qwen répond plus vite et occupe moins de mémoire GPU. Ses réponses sont toutefois moins fiables pour le raisonnement, le code et la synthèse. Le rapport présente les résultats mesurés et les réponses qui permettent de faire ce constat.')
h('Organisation de l’application',2)
p('L’interface et les conversations restent dans ENSET_Chatbot.py. Les appels à Ollama et les mesures sont regroupés dans core.py. Le script experiment.py envoie les cinq questions aux deux modèles et enregistre les résultats. Le script de départ est conservé sans modification dans le dossier original.')
p('Lorsqu’une question est envoyée, l’interface appelle Ollama sur la machine. Les fragments reçus sont affichés au fur et à mesure. En parallèle, un suivi relève le CPU, la RAM et, lorsque cela est possible, le GPU. Les résultats sont ensuite ajoutés aux tableaux de l’application.')
p('L’application récupère la liste des modèles réellement installés. Si Ollama est inaccessible ou si la génération échoue, elle affiche un message d’erreur. Un indicateur reste visible pendant l’attente de la réponse. Les deux modes sont accessibles depuis la barre latérale.')

page()
h('2 Gestion des conversations')
p('Le bouton « Nouvelle conversation » ouvre une discussion vide. Les discussions précédentes restent accessibles dans la liste de la session. Une conversation sélectionnée peut être supprimée ou téléchargée en TXT ou en JSON. Ces exports permettent de conserver son contenu après la fermeture de la session.')
picture('application_dialogue.png','Figure 1  Dialogue réel avec Qwen dans l’application',width=7)
picture('application_conversations.png','Figure 2  Commandes de création de suppression et d’export',width=2.8,max_height=4)
p('La figure 2 montre les deux formats d’export et le modèle utilisé. Les captures de cette partie illustrent des essais de l’interface. Les chiffres de l’étude comparative proviennent, eux, des dix observations enregistrées dans le dossier resultats.')

page()
h('3 Comparaison et consultation de l’historique')
picture('application_historique.png','Figure 3  Deux conversations conservées dans la même session',width=2.8,max_height=2.8)
p('La liste de la figure 3 permet de revenir à la première discussion après en avoir créé une seconde. Le contenu est conservé dans st.session_state, pendant la session Streamlit. Il n’y a pas de base de données de conversations.')
picture('application_comparaison.png','Figure 4  Question commune et réponses affichées sur deux colonnes',width=7)
p('Dans le mode comparaison, l’utilisateur choisit deux modèles distincts parmi ceux qui sont installés. La même question et les mêmes paramètres sont transmis aux deux modèles. Les générations se font l’une après l’autre pour limiter leur concurrence sur le matériel. La figure 4 montre un essai de traduction réalisé dans ce mode.')

page()
h('4 Matériel et protocole expérimental')
table(['Élément','Configuration utilisée'],[
    ['Système','Windows 10 version 19045'],
    ['Processeur','AMD Ryzen 5 5600H — 6 cœurs et 12 processeurs logiques'],
    ['Mémoire vive','15,35 Gio utilisables'],
    ['GPU','NVIDIA GeForce RTX 3060 Laptop GPU — 6 144 Mio de mémoire'],
    ['Autre GPU présent','AMD Radeon intégré'],
],[1.6,5.4])
p('Ces informations figurent dans resultats/conditions.json. La capacité mémoire de la carte NVIDIA a été relevée avec nvidia-smi. Les valeurs de RAM exprimées en Go dans l’interface sont calculées sur une base de 1 024 et correspondent donc à des Gio.')
table(['Modèle demandé','Étiquette Ollama','Taille annoncée','Quantification'],[
    ['Llama 3.2','llama3.2:latest','3,2 milliards','Q4_K_M'],
    ['Qwen 0.5B','qwen:0.5b','620 millions','Q4_0'],
],[1.5,1.9,1.8,1.8])
p('Le nom Qwen 0.5B est celui du sujet et de l’étiquette installée. Ollama annonce 620 millions de paramètres pour ce fichier. Les deux modèles n’ont ni la même taille ni la même quantification ; la comparaison décrit donc ces versions précises.')
p('Les réglages sont identiques : température de 0,7, top-k de 40, top-p de 0,9, maximum de 512 tokens, contexte de 2 048 tokens et graine fixée à 42. Chaque question est envoyée dans un contexte neuf. Un échauffement précède chaque série, puis le modèle précédent est déchargé avant de passer au suivant.')
p('J’ai retenu cinq tâches : expliquer la différence entre RAM et stockage, résoudre un petit problème de prix, écrire une fonction Python, résumer un texte et traduire une phrase. Les formulations exactes apparaissent dans les captures des réponses. Chaque question a été exécutée une fois par modèle, dans le même ordre, Llama avant Qwen.')
h('Lecture des mesures',2)
p('Le temps de réponse va du début de l’appel à la fin du flux. Le TTFT correspond à l’attente avant le premier fragment de texte reçu. Le nombre de tokens vient du compteur eval_count d’Ollama. Le débit est calculé en divisant ce nombre par eval_duration converti en secondes. Il porte sur la génération, alors que le temps total comprend aussi le traitement de la question.')

page()
h('5 Temps de réponse observés')
table(['Tâche','Modèle','Temps en s','Tokens','Tokens par s','TTFT en s'],[
    [r['Tâche'],short(r['Modèle']),f"{r['Temps (s)']:.3f}".replace('.',','),r['Tokens'],f"{r['Tokens/s']:.1f}".replace('.',','),f"{r['TTFT (s)']:.3f}".replace('.',',')] for r in records
],[1.25,1.25,1.1,.75,1.35,1.3])
p('Tableau 1  Les dix générations mesurées le 18 novembre 2026','Caption')
picture('temps_nb.png','Figure 5  Durée totale de chaque réponse après échauffement',width=7)
p('Qwen a le temps le plus faible pour chacune des cinq questions. Sa moyenne est de 0,364 s, contre 1,048 s pour Llama. L’écart change selon la tâche : il est d’environ 1,33 s pour le raisonnement, mais de 0,10 s pour la traduction. Les réponses ne sont pas toutes aussi longues ni aussi pertinentes, ce qui compte dans l’interprétation de ces durées.')

page()
h('6 Débit et attente du premier fragment')
picture('debit_nb.png','Figure 6  Vitesse de génération calculée avec les compteurs Ollama',width=7)
p('Qwen produit en moyenne 395,9 tokens par seconde, contre 118,9 pour Llama. Il est donc environ 3,3 fois plus rapide sur cet indicateur. Ces valeurs sont les moyennes des cinq débits. Un débit élevé renseigne sur la vitesse du modèle, mais ne permet pas de juger si sa réponse résout la question.')
picture('ttft_nb.png','Figure 7  Délai avant le premier fragment de texte reçu',width=7)
p('Le premier fragment arrive en moyenne après 0,098 s pour Qwen et 0,126 s pour Llama. L’écart est moins marqué que pour le débit. Ces mesures ont été prises après échauffement. Lors d’un premier appel à un modèle déchargé, il faut aussi attendre son chargement ; les captures fonctionnelles peuvent donc afficher un temps supérieur à celui de cette série.')
p('Les dix valeurs sont lisibles dans le tableau 1 et dans le fichier mesures.csv. La capture de la figure 16, en fin de rapport, montre également leur lecture à partir des données archivées.')

page()
h('7 Utilisation des ressources')
models=['llama3.2:latest','qwen:0.5b']
summary=[]
for model in models:
    rows=[r for r in records if r['Modèle']==model]
    summary.append([short(model),f"{mean(r['cpu_pct_mean'] for r in rows):.1f}",f"{mean(r['ram_gb_max'] for r in rows):.2f}",f"{mean(r['gpu_pct_mean'] for r in rows):.1f}",f"{mean(r['vram_mb_max'] for r in rows):.0f}"])
table(['Modèle','CPU moyen en %','Pic RAM moyen en Gio','GPU moyen en %','Pic VRAM moyen en Mio'],summary,[1.3,1.3,1.5,1.3,1.6])
p('Tableau 2  Moyenne des cinq observations pour chaque modèle','Caption')
picture('memoire_nb.png','Figure 8  Comparaison des pics de mémoire relevés pendant les réponses',width=7)
p('L’écart le plus net concerne la mémoire GPU : le pic moyen est d’environ 3 115 Mio pour Llama, contre 1 413 Mio pour Qwen. La RAM système est plus proche, avec environ 9,07 Gio contre 8,77 Gio. Ces chiffres incluent les autres logiciels présents sur le poste ; ils ne correspondent pas à la mémoire du seul modèle.')
picture('application_ressources.png','Figure 9  Affichage du CPU de la RAM et du GPU dans l’application',width=7)
p('Le CPU moyen relevé est plus élevé pour Qwen, à 26,2 % contre 14,6 %. Il faut rester prudent : plusieurs réponses de Qwen durent moins d’une demi-seconde et ne donnent qu’un seul échantillon. Le suivi espace les relevés d’au moins 0,4 s et mesure le CPU sur 0,1 s. Il peut manquer des pics. Ces valeurs ne suffisent donc pas pour comparer l’énergie consommée ou la charge totale des deux modèles.')

page()
h('8 Explication de la RAM et du stockage')
p('La première question demande une explication en français, en trois phrases. La capture ci-dessous reproduit les réponses enregistrées lors de l’étude. Les vues de lecture des figures 10 à 12 et 14 à 16 utilisent directement reponses.json : elles permettent de consulter les textes d’origine sans relancer les modèles.')
picture('preuve_concept.png','Figure 10  Réponses archivées à la question sur la RAM et le stockage',width=7)
p('Llama distingue bien la mémoire temporaire du stockage persistant. Sa réponse respecte les trois phrases demandées. Une partie reste inexacte : le lancement d’une nouvelle tâche n’efface pas automatiquement les données de la RAM. L’explication est donc utilisable comme point de départ, mais cette phrase doit être corrigée.')
p('Qwen commence par deux phrases peu compréhensibles et insère des caractères chinois, puis termine en anglais. La dernière phrase exprime la différence entre temporaire et permanent, mais l’ensemble ne constitue pas une explication claire en français. Il a répondu en 0,494 s, contre 1,573 s pour Llama ; ici, le gain de temps s’accompagne d’une baisse nette de qualité.')

page()
h('9 Résolution du problème de prix')
picture('preuve_raisonnement.png','Figure 11  Calcul de Llama et réponse hors sujet de Qwen dans le fichier archivé',width=7)
p('Le stylo coûte 2 dirhams. Si son prix est x, celui du livre est x + 18. La somme donne 2x + 18 = 22, donc x = 2. La figure 11 montre que Llama suit ce calcul et arrive à la bonne valeur. Pour garder le calcul lisible, seule la fin de sa réponse est affichée dans cette vue ; la réponse complète reste dans le fichier source.')
p('Qwen parle de l’architecture et des performances d’un stylo, sans utiliser les deux prix du problème. Il ne donne pas de solution. Sa durée est pourtant quatre fois plus courte environ, à 0,435 s contre 1,763 s. Ce cas montre pourquoi la durée ne doit pas être utilisée seule pour choisir un modèle.')

page()
h('10 Génération de code Python')
picture('preuve_code.png','Figure 12  Fonctions et exemples proposés pour la question Python',width=7)
p('Llama propose une fonction est_palindrome. Elle retire les espaces avec une expression régulière, transforme le texte en minuscules et le compare à son inverse. Cela répond à la consigne. Le premier exemple contient cependant un commentaire erroné : la chaîne « Madame, je suis une letrine. » n’est pas un palindrome, alors que le modèle annonce True.')
p('Qwen utilise le nom is_palindrome sans définir la fonction. Le bloc de code ne peut donc pas être exécuté tel quel. Il annonce aussi une valeur 1 sans la justifier et donne cinq textes d’exemple alors que deux tests étaient demandés. Sa réponse est plus longue en tokens que celle de Llama, mais elle reste incomplète.')

page()
h('11 Vérification de la fonction proposée')
picture('preuve_verification_code.png','Figure 13  Exécution locale de la fonction de Llama sur quatre chaînes',width=7)
p('J’ai vérifié séparément la fonction de Llama sur deux palindromes, un mot ordinaire et la chaîne de son premier exemple. Elle renvoie les bonnes valeurs pour les trois premiers cas. Pour la dernière chaîne, elle renvoie False : l’erreur vient du commentaire généré, pas du mécanisme de comparaison utilisé par la fonction.')
p('Cette vérification complète la lecture du code. Les résultats sont conservés dans rapport_assets/verification_code.json. Elle n’a pas servi à recalculer les temps du tableau 1, qui correspondent uniquement aux dix générations initiales.')
p('Pour cette tâche, Llama est le meilleur des deux modèles testés, mais ses exemples doivent être exécutés avant d’être repris. Qwen ne fournit pas le code demandé. Une réponse rapide ou bien présentée ne dispense donc pas de vérifier qu’une fonction existe et qu’elle passe des tests simples.')

page()
h('12 Synthèse et traduction')
picture('preuve_synthese.png','Figure 14  Réponses archivées à la demande de synthèse en deux phrases',width=7)
p('Llama rassemble les informations dans deux phrases et conserve la durée des travaux ainsi que le maintien des cours. Il ajoute toutefois des formulations sur les perturbations de l’enseignement qui ne figurent pas explicitement dans le texte. Qwen recopie les quatre phrases du départ. Les informations restent présentes, mais la consigne de synthèse en deux phrases n’est pas respectée.')
picture('preuve_traduction.png','Figure 15  Traductions enregistrées pour la même phrase française',width=7)
p('Les deux traductions restent compréhensibles et proches du sens demandé. Llama utilise « design » pour « concevoir », ce qui est plus direct que « develop », choisi par Qwen. Sur cette tâche courte, Qwen fournit une réponse acceptable en 0,129 s, contre 0,227 s pour Llama.')

page()
h('13 Vérification des valeurs et limites de l’étude')
picture('preuve_mesures.png','Figure 16  Lecture des dix mesures dans le fichier de résultats archivé',width=7)
p('La capture ci-dessus permet de retrouver les valeurs du tableau 1. Les graphiques sont calculés à partir de ces mêmes observations. Les arrondis servent seulement à rendre les tableaux lisibles ; les fichiers JSON et CSV gardent les valeurs mesurées.')
p('Le classement de vitesse est le même pour les cinq questions, mais cela ne prouve pas qu’il sera identique pour toutes les utilisations. Une seule génération a été réalisée pour chaque question et chaque modèle. L’ordre des modèles est fixe, et les autres logiciels du poste peuvent influencer les ressources relevées.')
p('Les compteurs Ollama donnent un débit de génération, tandis que le TTFT est mesuré du côté de l’application, au premier fragment reçu. Ce fragment peut contenir plusieurs tokens. Il s’agit donc d’une approximation du temps au premier token, et non d’une mesure interne du moteur.')
p('Les essais de l’interface et la vérification du code ont été réalisés séparément. Ils illustrent les fonctionnalités ou vérifient une erreur précise ; ils ne remplacent pas les observations du protocole comparatif.')

page()
h('14 Bilan et choix du modèle')
p('Sur ce poste, Qwen 0.5B est le plus rapide des deux modèles. Il présente le temps de réponse le plus faible pour les cinq questions et le débit moyen le plus élevé. Son occupation de la mémoire GPU est aussi nettement plus faible. Ces résultats en font une option intéressante lorsque la mémoire disponible est limitée.')
p('Je le réserverais cependant à des tâches simples dont la réponse peut être vérifiée facilement. La traduction testée est acceptable, mais le raisonnement, le code et la synthèse montrent des limites importantes. Pour ces usages, Llama 3.2 offre des réponses plus utiles dans ce corpus, avec un coût mémoire plus élevé. Il reste nécessaire de contrôler ses explications et ses exemples Python.')
p('Les écarts ne sont pas constants en valeur : ils changent avec la question et la longueur de la réponse. Le choix dépend donc de la tâche, de la mémoire disponible et du niveau d’erreur acceptable. Une série de tests répétée sur un corpus plus large serait nécessaire avant de tirer une recommandation générale.')
h('Vérifications de l’application',2)
p('Les cinq tests fonctionnels de l’application passent. Ils couvrent la gestion des conversations et la présence des exports, l’envoi des mêmes paramètres aux deux modèles, une erreur de génération, l’absence de service Ollama et l’absence de modèles installés. Les réponses utilisées dans ces tests sont isolées des mesures expérimentales. Les captures de l’interface montrent également son exécution avec les modèles locaux.')
h('Fichiers remis',2)
p('Le projet contient l’application, requirements.txt, les instructions d’installation, le script initial, les données expérimentales, les captures et ce rapport Word. Les consignes de remise sont conservées dans CONSIGNES_RAPPORT.md. Les environnements Python utilisés pour les essais et la préparation du rapport sont temporaires et sont nettoyés après vérification.')
h('Sources',2)
sources=p('Sujet du TP de Pr OUHMIDA : TP_Ameliorations_LLMs.pdf. Script initial : ENSET_Chatbot.py. Mesures et réponses : resultats/conditions.json, resultats/mesures.csv et resultats/reponses.json, relevés le 18 novembre 2026. Documentation des compteurs Ollama : github.com/ollama/ollama/blob/main/docs/api.md.')
sources.alignment=WD_ALIGN_PARAGRAPH.LEFT

output=ROOT/'Rapport_TP_LLMs_Houssy_Badr.docx'
document.save(output)
(ROOT/'RAPPORT.md').write_text('\n\n'.join(outline),encoding='utf-8')
print(output)
