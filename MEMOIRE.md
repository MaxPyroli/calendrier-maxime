# Mémoire de reprise — 9 octobre 2026

## Atelier (journée) comme carte de cours — vague corrigée (9 octobre 2026)

- Signalement utilisateur : « Atelier (journée) » n'est pas placé dans la journée mais seulement affiché comme événement « toute la journée », et la vague n'avance pas correctement.
- Cause : `inDayHeading()` de `template.html` envoyait dans le badge de l'en-tête tout événement dont le titre contient « journée », même avec des horaires (règle ajoutée à la quatrième intervention). Le vendredi n'avait donc aucune carte de cours ; le calcul de la vague (`courseSurface`) s'appuie sur les cartes et renvoyait 0 : le pourcentage montait de 0 à 100 % pendant que l'eau restait en haut (reproduit dans Chromium avant correction, surface 0 px à toute heure).
- Correction : `inDayHeading(e)` ne retient plus que les événements `allDay` ou sur plusieurs jours (« Activités communes de l'EUP » reste un badge bleu). Un événement horaire d'une seule journée devient une carte normale ; il garde ses repères « Premier cours 09:00 » et « Fin des cours 18:00 » inchangés. Dix occurrences sont concernées dans la plage actuelle : les « Atelier (journée) » du vendredi, 02/10 au 18/12.
- Vérifié avec Chromium et horloge simulée le vendredi 9/10 : l'avancement de la vague dans la carte égale le pourcentage de la journée (25 % à 11 h 15, 50 % à 13 h 30, 86 % à 16 h 45), eau avant la carte à 8 h et tout le jour rempli après 18 h. Aucune erreur JavaScript. Le badge de l'atelier a disparu : la carte porte maintenant l'information avec ses horaires.
- `index.html` régénéré depuis le flux réel ; README mis à jour.

## Ouverture sur le jour actuel — reprise avec Claude Code (9 octobre 2026)

- Reprise du projet depuis Claude Code (la conversation Codex n'était pas accessible ; l'historique de ce fichier a servi de base). État constaté : aucun dossier `.github/workflows` dans le dépôt, donc pas de régénération automatique ; les données embarquées datent toujours du 29/09. Les entrées ci-dessous ne mentionnent ni la PWA ni le commit du 30/09 : PWA = `sw.js` (réseau d'abord, repli sur cache), `install.js`, `manifest.webmanifest`, icônes ; `index.html` à la racine et `public/index.html` sont des copies identiques.
- Demande utilisateur : arriver directement sur le jour actuel.
- Cause : `template.html` initialisait `current` avec `data.monday`, la semaine figée à la génération (28/09), et ne se repositionnait pas sur aujourd'hui.
- `template.html` (et les deux copies générées `public/index.html` et `index.html`, corrigées à l'identique faute de source `.ics` locale — mêmes données) : nouvelle fonction `showToday()` appelée au chargement et par le bouton « Cette semaine ». Elle sélectionne la semaine en cours (bornée à la plage de la page) puis fait défiler jusqu'à la carte marquée `.day-today`, avec `scroll-margin-top:12px`. Pas de défilement le lundi (la page reste en haut, avec le titre et la navigation) ni si aujourd'hui est hors plage ; défilement instantané à l'ouverture, doux pour le bouton, sauf si `prefers-reduced-motion`.
- Vérifié avec Chromium headless et horloge simulée (viewport mobile) : vendredi 9/10, lundi 5/10, dimanche 11/10, mardi 29/09, date hors plage et bouton « Cette semaine » ; aucune erreur JavaScript. Les 8 tests Python passent. Fichiers HTML en fins de ligne CRLF, conservées.
- Données actualisées : le flux public est téléchargeable depuis cet environnement. Régénération réelle du 09/10/2026 : 1 014 événements source, 550 retenus, 274 inconnus (contre 1 011 / 549 / 272 le 29/09). Nouveautés de la source : séances d'atelier et d'UE en décembre (déplacements), soutenance MASYT du 25/01/2027, et deux intitulés inconnus donc masqués : « Travail personnel et collectif » (10/12) et « Présentation recherche stages Sandrine Vazquez » (05/11) — à réexaminer avec Maxime avant d'ajouter une règle. Règles de filtrage inchangées.
- Libellé de plage corrigé : une semaine à cheval sur deux années affichait l'année de début pour les deux dates (« 3 janvier 2026 ») ; la dernière semaine de la plage (28/12 – 03/01) montre maintenant « 28 décembre 2026 – 3 janvier 2027 ».
- Mise en place automatique : ajout de `.github/workflows/calendar.yml` (toutes les 6 h, à la demande, et sur modification du code de génération) : tests, `weekly.py`, commit de `index.html` et `audit.json` par `github-actions[bot]` seulement si la génération réussit et change quelque chose. Pages reste configuré en « Deploy from a branch » `main` / racine : aucun réglage à changer. Le dossier `public/` (doublon exact de la racine) est supprimé ; `weekly.py` écrit `index.html` à la racine. Ajout d'un `.gitignore` et retrait du `.pyc` versionné. Les anciennes entrées de ce fichier parlant de `public/index.html` désignent désormais `index.html`.
- Avertissements : l'entrée « Publication GitHub Pages » plus bas (Pages non configuré, upload manuel) est obsolète : le site répond sur `https://maxpyroli.github.io/calendrier-maxime/`. L'export ICS reste une piste optionnelle de `filter_calendar.py` (sa sortie par défaut `public/maxime.ics` recrée le dossier si besoin).

# Mémoire de reprise — 29 septembre 2026

## Préparation au déploiement GitHub — vingt-cinquième intervention

- L'utilisateur demande que le déploiement hors Codex soit effectué par l'agent.
- Archive de déploiement à jour reconstruite depuis `outputs/calendrier-maxime`, en excluant les caches Python. La création d'un dépôt GitHub public et l'activation de GitHub Pages restent à faire après confirmation explicite au moment de publier, car elles rendent ce projet accessible publiquement sous le compte utilisateur.

## Salles masquées — vingt-quatrième intervention

- Demande utilisateur : enlever la précision de salle pour les cours.
- `template.html` : retrait de l'élément d'affichage `LOCATION` sous chaque carte de cours. La source continue d'être lue et les données de salle ne sont pas modifiées dans le calendrier source ; elles sont simplement absentes de l'aperçu.
- README et mémoire mis à jour. Page régénérée et JavaScript vérifié ; filtres inchangés.

## Eau sur toutes les dates passées — vingt-troisième intervention

- Demande utilisateur : remplir d'eau tous les jours passés, y compris ceux des semaines précédentes.
- `template.html` : la classification « jour passé » ne dépend plus de la présence d'un horaire de cours. Toute carte dont la date Paris est antérieure à aujourd'hui reçoit désormais le remplissage uniforme et immobile ; les journées vides des semaines passées sont donc également remplies. La vague active continue de nécessiter un horaire exploitable le jour courant.
- README et mémoire mis à jour. Page régénérée et JavaScript vérifié ; filtres inchangés.

## Vague limitée au jour courant — vingt-deuxième intervention

- Signalement utilisateur : une vague apparaît sur le jour précédent.
- Cause : la règle finale d'animation de `.day-progress::before` avait la même spécificité qu'une règle antérieure de jour passé et l'écrasait par ordre CSS. `template.html` définit maintenant après cette règle une variante `.day-past::before` explicite : dimensions de carte, eau uniforme, aucun clip-path, aucune transformation et aucune animation. La pseudo-surface est également masquée.
- README et mémoire mis à jour. Page régénérée et JavaScript vérifié ; filtres inchangés.

## Vague amplifiée, pourcentage stabilisé — vingt-et-unième intervention

- Retour utilisateur : le pourcentage semble se déplacer ; demande d'un mouvement de vague plus large et plus lent.
- `template.html` : le badge de pourcentage garde la position moyenne du niveau et ne fait plus de transition CSS entre les actualisations horaires, donc il ne suit pas le va-et-vient visuel de l'eau. La vague passe d'une oscillation de ±3 px sur 3,2 s à ±7 px sur 6,5 s ; son mouvement est donc plus ample et plus lent. Le clipping de la carte reste inchangé.
- README et mémoire mis à jour. Page régénérée et JavaScript vérifié ; filtres inchangés.

## Vague surdimensionnée et découpée — vingtième intervention

- Demande utilisateur : retrouver le mouvement vertical en rendant la vague plus grande que la carte, mais cachée derrière son fond afin qu'elle ne dépasse jamais en haut.
- `template.html` : la carte du jour reprend `overflow:hidden`. La couche d'eau active fait 120 % de largeur, commence 16 px au-dessus de la carte et a 16 px de hauteur supplémentaire ; le clipping des bords arrondis cache donc tout débordement. Son déplacement vertical agit toujours sur toute la couche, mais le haut est masqué et seul le bord ondulé inférieur est perceptible. Le pourcentage devient un élément frère de la carte dans la grille, ce qui lui permet de rester visible à droite malgré le clipping. Sa position est recalculée à chaque mise à jour et lors d'un redimensionnement de fenêtre.
- README et mémoire mis à jour. Page régénérée et JavaScript vérifié ; filtres inchangés.

## Surface mobile séparée du remplissage — dix-neuvième intervention

- Retour utilisateur : l'ondulation du bas ne donne pas assez le va-et-vient souhaité ; il faut le conserver sans déplacer tout le remplissage ni dépasser en haut.
- `template.html` : le volume d'eau devient fixe et se termine 8 px avant le niveau. Une pseudo-surface SVG de 18 px, remplie et arrondie, comble cette jonction puis oscille verticalement de 3 px. Cette surface est la seule partie animée ; elle est située au niveau courant et ne peut pas atteindre le haut de la carte dans l'usage normal. Les jours passés gardent leur remplissage fixe et n'affichent pas cette surface.
- README et mémoire mis à jour. Page régénérée et JavaScript vérifié ; filtres inchangés.

## Ondulation du bord inférieur uniquement — dix-huitième intervention

- Demande utilisateur : seul le bas de la vague doit bouger, sans débordement en haut de la carte ; augmenter le mouvement.
- `template.html` : suppression de la translation verticale de toute la couche d'eau. Une animation `water-bottom` modifie uniquement la découpe du bord inférieur : la masse d'eau reste fixe tandis que ses creux et crêtes bougent davantage (94–100 % de sa hauteur). Les jours passés restent immobiles.
- README et mémoire mis à jour. Page régénérée et JavaScript vérifié ; filtres inchangés.

## Mouvement vertical de la vague — dix-septième intervention

- Correction utilisateur : le mouvement demandé est vertical, pas horizontal.
- `template.html` : retrait du décalage latéral et de la largeur de sécurité associée. La vague active oscille maintenant verticalement de 2 px vers le haut puis vers le bas sur 3,2 secondes. Les jours passés restent fixes, et `prefers-reduced-motion` continue de couper l'animation.
- README et mémoire mis à jour. Page régénérée et JavaScript vérifié ; filtres inchangés.

## Mouvement de va-et-vient — seizième intervention

- Demande utilisateur : ajouter un petit mouvement avant-arrière à la vague.
- `template.html` : la couche d'eau active est élargie de 12 px puis oscille horizontalement de 3 px dans chaque direction sur 3,2 secondes. Cette marge évite tout espace vide sur les bords pendant le mouvement. Les jours passés ne bougent pas. La règle `prefers-reduced-motion` coupe également ce nouveau mouvement.
- README et mémoire mis à jour. Page régénérée et JavaScript vérifié ; filtres inchangés.

## Blocs de cours sous l'eau — quinzième intervention

- Demande utilisateur : remettre les blocs de cours derrière la vague et enlever leur bande colorée à gauche.
- `template.html` : la couche d'eau active passe au-dessus des blocs de cours (z-index 2) ; les textes de repères de journée, la pause et le pourcentage restent au-dessus pour garder leur lisibilité. La bordure gauche verte des cours est remplacée par une bordure fine uniforme tout autour du bloc.
- README et mémoire mis à jour. Page régénérée et JavaScript vérifié ; filtres inchangés.

## Retour à la vague douce et cartes de cours — quatorzième intervention

- Retours utilisateur : la dernière vague est ratée ; revenir à la précédente en adoucissant ses angles. Déplacer le pourcentage hors de la carte à droite. Rétablir les blocs distincts par cours. Réduire encore la largeur maximale.
- `template.html` : retrait de la forme SVG de vague ; retour au remplissage ondulé d'origine, dont les crêtes ont été abaissées (98–100 %) et légèrement lissées. Les jours passés conservent une eau uniforme sans vague. Le pourcentage est placé 48 px à l'extérieur du bord droit et suit le niveau. Les cours redeviennent des blocs blancs translucides à bord vert. La colonne passe de 720 à 640 px, avec adaptation mobile de la marge du pourcentage.
- README et mémoire mis à jour. Page régénérée et JavaScript vérifié ; filtres inchangés.

## Eau uniforme, vague arrondie et colonne verticale — treizième intervention

- Demande utilisateur : les jours déjà passés doivent être remplis uniformément ; le dégradé doit partir uniquement de l'extrémité de la vague active ; les angles de vague doivent être moins pointus ; le pourcentage doit être seul, à droite et suivre la vague ; les jours doivent être verticaux avec largeur maximale.
- `template.html` : les cartes sont en une colonne plafonnée à 720 px. Les jours passés utilisent désormais une eau bleue uniforme. Le jour actif a une eau presque uniforme dont le dégradé n'intervient que près de la limite ; son extrémité est une forme SVG remplie, lisse et arrondie plutôt qu'un polygone pointu. Le pourcentage est devenu « N % », positionné absolument à droite et déplacé avec le niveau d'eau. Les pseudo-lignes précédentes restent supprimées.
- README et mémoire mis à jour. Page régénérée et JavaScript vérifié ; filtres inchangés.
- Ajustement d'accessibilité : la nouvelle animation de vague respecte aussi `prefers-reduced-motion`, vérifié par ajout de la règle CSS correspondante.

## Une vague unique pour la semaine — douzième intervention

- Correction utilisateur : l'effet souhaité est une vague unique qui traverse les jours de la semaine, et non une ligne bleue sur chaque carte.
- `template.html` : suppression complète de la pseudo-ligne bleue. Les jours antérieurs à la date courante gardent seulement le dégradé bleu plein, sans vague ni animation. Le jour courant est le seul à porter la forme ondulée animée à la limite de son remplissage ; les jours futurs restent secs. La logique de classement passé/courant/futur existante sert ainsi de progression visuelle de semaine.
- README et mémoire mis à jour. Page régénérée et JavaScript vérifié ; filtres inchangés.

## Vague bleue et jours passés inondés — onzième intervention

- Demande utilisateur : les jours passés doivent être déjà inondés, la vague étant passée ; demande précédente maintenue pour une ligne bleue en petite vague.
- `template.html` : la limite de niveau est désormais un motif SVG local de vague bleue de 8 px qui défile sans ressource réseau. Une journée antérieure à la date de Paris reçoit un remplissage de 100 % et la vague est placée au bas de la carte. Le jour courant conserve son niveau proportionnel et son pourcentage ; les jours futurs ne reçoivent aucun remplissage. Cette logique ne s'applique qu'aux cartes avec horaires exploitables.
- README et mémoire mis à jour. Page régénérée et JavaScript vérifié ; filtres inchangés.

## Tentative de vague précédente — dixième intervention

- La première tentative de modifier la ligne ondulée a échoué car le texte CSS attendu ne correspondait plus exactement au fichier. Aucun fichier n'a été modifié lors de cette tentative ; le changement est appliqué dans l'intervention suivante.

## Pourcentage de progression — neuvième intervention

- Demande utilisateur : afficher le pourcentage de remplissage de la journée.
- `template.html` : ajout du badge compact « Journée · N % » à côté de la date uniquement sur le jour courant. Sa valeur réutilise le ratio déjà employé pour la vague et est mise à jour au même rythme de 30 secondes. Il ne s'affiche pas sur les autres jours, ni lorsqu'aucun horaire exploitable n'est disponible.
- README et mémoire mis à jour. La page est régénérée et le script est contrôlé avant livraison ; filtres inchangés.

## Animation du remplissage d'eau — huitième intervention

- Demande utilisateur : donner un aspect d'eau animé au remplissage de progression de la journée.
- `template.html` : le voile de progression devient bleu-vert, avec une limite découpée en vague qui ondule sur quatre secondes ; la ligne de niveau a une pulsation douce. La hauteur reste pilotée uniquement par le pourcentage horaire existant et ne modifie pas les données ou calculs du calendrier.
- Respect de `prefers-reduced-motion` : les vagues et la pulsation sont désactivées lorsque l'appareil demande une réduction des animations. README et mémoire mis à jour. Page régénérée et JavaScript vérifié avant livraison. L'archive ZIP n'est pas reconstruite pour cette modification : utiliser la page ou le dossier `calendrier-maxime` comme version à jour.
- Vérification JavaScript : le premier appel de l'utilitaire de contrôle a été lancé depuis le sous-dossier du projet et n'a donc pas trouvé son chemin relatif. Relancé depuis la racine de l'espace de travail, l'extraction et `node --check` ont réussi. Aucun fichier de production n'a été affecté par cette erreur de vérification.

## Progression en temps réel de la journée — septième intervention

- Demande utilisateur : visualiser où en est la journée par un remplissage progressif de la carte, « comme une bouteille d'eau » remplie depuis le haut.
- `template.html` : ajout, uniquement sur la carte de la date courante et lorsque ses horaires sont exploitables, d'un voile vert léger qui progresse du haut jusqu'au pourcentage écoulé entre le premier et le dernier cours. Une ligne verte horizontale suit le niveau de remplissage. Le calcul est borné à 0–100 %, repose sur les dates d'événements en heure de Paris et est rafraîchi toutes les 30 secondes. Les autres cartes restent inchangées, ainsi que les journées comportant seulement des événements longs ou sans horaires utilisables.
- README et mémoire actualisés. Page régénérée pour la semaine du 28/09 ; les 8 tests de filtrage passent et la syntaxe JavaScript a été vérifiée. Règles de filtrage inchangées ; archive ZIP reconstruite.
- Contrôle JavaScript : une tentative directe de `node --check` sur le fichier HTML a échoué car Node n'accepte pas l'extension `.html`. Le script a ensuite été extrait avec l'utilitaire local `work/check_preview.py` et `node --check work/preview.js` a réussi. Aucun fichier de production n'a été modifié par cette vérification.

## Repères horaires et déjeuner compactés — sixième intervention

- Retour utilisateur : les grands bandeaux « Premier cours » / « Fin des cours » et l'encart repas prennent trop de place.
- `template.html` : les bandeaux deviennent des lignes fines vertes, avec libellé et heure seulement. La pause déjeuner devient une ligne fine ocre « Pause déjeuner · durée » ; suppression des horaires de la pause et du texte de contexte. Le calcul des créneaux ne change pas.
- README et mémoire mis à jour. Page régénérée depuis la source locale avec filtres inchangés ; syntaxe JavaScript vérifiée. Archive ZIP reconstruite.

## Badges d'événements longs compactés — cinquième intervention

- Retour utilisateur sur le badge « Activités communes de l'EUP » : il prend trop de place. Demande appliquée : afficher uniquement le nom de l'événement sur une ligne, à côté de la date.
- `template.html` : en-tête de jour aligné au centre ; badges regroupés horizontalement à droite, un seul rang, texte tronqué avec ellipse seulement lorsqu'il ne tient pas. Suppression des dates, horaires et salles répétés dans ces badges. Les couleurs violet/bleu et la séparation de la liste de cours sont conservées.
- README et cette mémoire mis à jour. Page régénérée à partir de la source locale ; filtres inchangés. Vérification de syntaxe JavaScript effectuée avant livraison. Archive ZIP reconstruite.

## Événements longs à droite du jour — quatrième intervention

- Demande utilisateur : placer les événements sur une journée ou plusieurs jours à droite du jour, en couleur.
- template.html : ajout d'un en-tête flex avec nom du jour à gauche et badges à droite. Violet pour une journée, bleu pour plusieurs jours ; titre, plage de dates et horaires connus, salle si disponible. Sur plusieurs jours, badge répété chaque jour concerné, en respectant la fin exclusive iCal. Reconnaissance des événements allDay, des événements traversant plusieurs dates de Paris et des titres contenant « journée » (ex. Atelier (journée), 09h–18h).
- Ces événements ne sont plus dupliqués dans la liste des cours. Leur comptage hebdomadaire est conservé. Les calculs début/fin et déjeuner continuent d'examiner tous les événements afin de ne pas inventer une disponibilité pendant un événement long. Pour Atelier (journée), les bornes 09h–18h restent donc affichées.
- Page et audit régénérés depuis la source locale du 29/09, semaine du 28/09 ; 549 événements retenus, filtrage inchangé. Syntaxe JavaScript vérifiée par Node avec succès. Aucun nouveau contrôle visuel navigateur (limitation précédemment documentée). README actualisé et archive ZIP reconstruite, caches exclus.

## Mise en valeur des horaires et déjeuner — troisième intervention

- Demande : mettre l'heure de début en haut de chaque journée, l'heure de fin en bas et un encart restauration entre les cours du midi.
- Lecture puis modification de template.html : bandeau vert foncé « Premier cours », bandeau clair « Fin des cours », grandes heures (26 px), horaires de chaque cours renforcés (15 px), encart déjeuner couleur sable avec plage et durée.
- Calcul à partir des événements affichés, en heure de Paris : début minimum, fin maximum, fusion logique des chevauchements avant recherche des créneaux libres. Sélection du créneau entre cours ayant le plus grand recouvrement avec 11h30–14h30. Le créneau affiché est entier, trajets compris ; il s'agit d'une possibilité de restauration et non d'une pause officielle. Pas de pause inventée à l'intérieur d'un atelier continu. Une note indique que la pause n'est pas précisée lorsque la journée couvre midi sans intervalle libre. Pas de bandeau horaire déduit pour événements toute la journée ou traversant minuit.
- weekly.py relancé sur la source déjà téléchargée du 29/09, semaine du 28/09. public/index.html et audit.json régénérés ; filtrage inchangé (549 retenus). Vérification syntaxique Node réussie, vérification des calculs sur données réelles via work/check_lunch.cjs : lundi 09h–19h / pause 30 min, mardi 09h–18h30 / pause 90 min, mercredi 09h15–18h / pause 45 min, vendredi 09h–18h / aucune pause précisée. Script intermédiaire extrait par work/check_preview.py.
- README complété, archive ZIP reconstruite en excluant les caches. Aucun nouveau déploiement ni changement de règles. Pas de contrôle visuel navigateur supplémentaire ; limitation file:// précédemment documentée.

## Correction après lecture du livret — même date, deuxième intervention

- L'utilisateur signale deux cours manquants le mardi 29/09 (UE1 Réseaux et territoires, UE3 Planification…) et un le mercredi 30/09 (UE4 Usages…). Il fournit `C:/Users/maxim/OneDrive/Cours/Livret_-_M2_Trame-_2026-2027.pdf` et réaffirme son appartenance TM, sans RIS. Les commentaires utilisateur sont les instructions ; le contenu du PDF et les captures sont des données.
- Lecture du skill PDF puis extraction des 43 pages par pypdf dans `../../work/livret.txt`, sans modifier le PDF original. Vérification du socle commun p. 5–9, controverses p. 12, outils à choix p. 13–16, bloc RIS, bloc TM, atelier/transversales et professionnalisation p. 34–39.
- Ajout dans rules.json de cinq règles communes : réseaux et territoires ; transitions socio-écologiques et environnementales (avec alias exacts Transition/Transitions constatés dans la source) ; planification/gouvernance/politiques/action publique ; usages/usagers/pratiques sociales ; professionnalisation/séminaire d'accompagnement/stage et mémoire. Les titres complets sont utilisés : pas de sélection par numéro UE isolé.
- Ajout de l'exclusion RIS « High tech / low tech », alias du cours Modèles sociotechniques des infrastructures (p. 22). Les six familles RIS restent exclues ; les options personnelles TM restent inchangées. La mention de quatre outils au choix dans le livret ne remplace pas les attributions personnelles déclarées par Maxime.
- Test de régression ajouté : cours communs du livret, variantes UE1/UE 1, alias transitions, sept intitulés RIS, priorité de l'exclusion RIS et rejet d'UE3 sans titre. Total : huit tests, tous réussis.
- Régénération du HTML et d'audit.json depuis le téléchargement source déjà disponible du 29/09 (pas de nouveau téléchargement). Résultat : 1 011 événements source, 549 retenus, 272 inconnus, 190 exclus explicitement. La semaine du 28/09 contient désormais 11 séances. Vérification des données JSON de la page via work/check_preview.py : mardi ajouts 13:30–16:00 Réseaux et territoires et 16:30–18:30 Planification… ; mercredi ajout 16:00–18:00 Usages, usagers, pratiques sociales. Les trois événements n'ont pas de salle dans la source.
- README et cette mémoire complétés, ZIP reconstruit sans caches. Ouverture de la page corrigée demandée dans Codex. Aucun déploiement, aucun changement d'interface ni de moteur, aucune nouvelle piste abandonnée. Les limites de contrôle visuel de l'intervention précédente restent inchangées.

## Demande et décision actuelle

Utilisateur : Maxime GRASSER, M2 TRAME parcours TM. Demande initiale : télécharger le flux public, filtrer selon ses enseignements attribués et exposer un flux iCal. Il a ensuite précisé : « j'aimerais que ça me donne un aperçu de la semaine plutôt qu'un autre fichier ics ». Le livrable principal est donc désormais `public/index.html`, une page hebdomadaire autonome. Conserver cette priorité lors d'une reprise. L'utilisateur demande aussi de consigner toutes les actions, changements et pistes mises de côté dans des fichiers mémoire.

## Actions réalisées

1. Inspection du dossier initial : seuls `work/` et `outputs/` existaient. Aucun projet préexistant modifié.
2. Consultation de la documentation officielle GitHub Pages, Actions (tarification, schedule) et icalendar. Sources liées dans README. Choix Python + Actions + Pages, dépôt public : pas de serveur à maintenir.
3. Le téléchargement par outil web a échoué. PowerShell a d'abord rencontré le blocage réseau puis une erreur TLS. Permission réseau demandée et accordée pour la session. `urllib.request` Python a téléchargé correctement le flux, sans désactiver la vérification TLS : 334 536 octets, conservés dans `../../work/source.ics`.
4. Python système était un alias WindowsApps non exécutable. Runtime utilisable trouvé via load_workspace_dependencies : `C:/Users/maxim/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`. Runtime Node : même racine, `node/bin/node.exe`.
5. Inventaire des SUMMARY après dépliage des lignes. Présence d'années anciennes et intitulés ambigus. Aucun secret de connexion nécessaire au flux public. Les descriptions ne sont pas recopiées dans l'interface ni dans l'audit.
6. Création de `filter_calendar.py` : bibliothèque icalendar, validation du conteneur, UID/DTSTAMP/DTSTART, règles normalisées, exclusion prioritaire, export stable, préservation des propriétés, téléchargement borné avec délai et tentatives, écriture atomique, protection contre source vide. Séries récurrentes filtrées comme groupes UID pour éviter la réapparition d'exceptions supprimées.
7. Création de `rules.json` couvrant le profil fourni et certaines variantes constatées. Cas ambigus masqués. Pas d'équivalence implicite économie des transports / économie des réseaux ni d'assimilation automatique des anciens codes EC. Ateliers génériques du calendrier traités comme projet commun, hypothèse expliquée dans README.
8. Création du workflow `.github/workflows/calendar.yml` : tests puis génération, audit en artefact 7 jours, publication Pages seulement si génération réussie. Déclenchement manuel, push main et toutes les six heures à :17 UTC. Pas de publication externe exécutée dans cette session.
9. Après précision utilisateur : ajout de `weekly.py`, `template.html`; remplacement de la petite page de lien ICS initiale par la page générée et changement du workflow pour exécuter weekly.py. Export ICS mis de côté, disponible seulement comme fonction optionnelle du moteur. Aucun nouveau fichier ICS livré.
10. Page : 25 semaines, navigation, date, bouton semaine actuelle, 7 jours, titres/salles, dates en Europe/Paris, annulations masquées, récurrences développées, événements multi-jours. Texte distant inséré par textContent et JSON protégé contre fermeture de script. Titres et salles seulement ; aucune description affichée.
11. Trois tentatives pip ont tourné sans aboutir avec consommation CPU ; processus de ces tentatives arrêtés (27888, 52556, 58776). Installation locale de vérification effectuée par téléchargement des wheels depuis PyPI, contrôle SHA-256 et extraction sous `../../work/python-packages`, script `../../work/install_deps.py`. Aucun changement global Python. Versions : icalendar 7.3.0, recurring-ical-events 3.8.2, x-wr-timezone 2.0.1, python-dateutil 2.9.0.post0, six 1.17.0, tzdata 2026.4, typing-extensions 4.16.0, click 8.5.0. Les deux dépendances principales sont fixées dans requirements.txt ; pip normal reste la procédure de déploiement GitHub.
12. Création de 7 tests unittest : autorisations, exclusions, priorité/description/inconnus, stabilité et propriétés iCal, exclusion d'une série à exception refusée, source invalide, récurrences et échappement HTML. Tous réussis.
13. Exécution sur source réelle : 1 011 VEVENT, 509 retenus, 318 inconnus, 184 exclusions explicites. Rapport complet `audit.json`. Page centrée sur la semaine du 28/09/2026 générée avec succès, 8 séances dans cette semaine.
14. Vérification syntaxique JavaScript avec `node --check` : réussite. Script intermédiaire `../../work/check_preview.py` et extrait `../../work/preview.js`. Deux commandes Python inline ont échoué à cause d'encodage console ou guillemets ; remplacées par scripts / PYTHONIOENCODING=utf-8. Aucun impact sur livrables.
15. Demande d'ouverture de l'HTML par open_in_codex : mise en file. Lecture du skill computer-use pour éventuel contrôle. Tentative navigateur sur URL file:// refusée par la politique des protocoles (HTTP/HTTPS uniquement). Aucun contournement tenté ; pas de validation visuelle automatique revendiquée.
16. README français fourni : déploiement, utilisation locale, limites, maintenance, règles et sources. Archive ZIP créée avec le code, fichiers cachés, README, mémoire, audit et aperçu ; caches Python exclus.

## Semaine vérifiée : 28/09 au 04/10, heure de Paris

- Lundi : Organisation des transports publics 09:00–12:00 ; MASYT (ENPC) 12:30–15:30 ; Articulation transports aménagement 16:30–19:00.
- Mardi : Socio-économie de la mobilité 09:00–12:00.
- Mercredi : EC1 Économie des réseaux 09:15–11:45 ; ACOST (ENPC) 12:30–15:30.
- Jeudi : UE1 Controverses sociotechniques 09:30–12:30.
- Vendredi : Atelier (journée) 09:00–18:00.
- Salles absentes dans ces événements source. Week-end sans cours identifié.

## Pour reprendre

### Hébergement privé — option étudiée le 29/09/2026

- L'utilisateur demande si le déploiement doit être public. Aucun compte, dépôt ou site externe n'a été créé.
- GitHub permet un dépôt privé, mais GitHub Pages gratuit sert les sites depuis des dépôts publics. Un Pages privé demande une offre GitHub payante compatible.
- Pour garder le planning accessible uniquement à son propriétaire sans payer, l'option technique retenue comme la plus adaptée est Cloudflare Pages (ou Worker) protégé par Cloudflare Access / Zero Trust avec authentification par e-mail. Elle demande un nom de domaine que l'utilisateur peut rattacher à Cloudflare.
- Alternative simple : dépôt GitHub privé mais page elle-même publique ; le code reste caché, les horaires ne le sont pas. Vercel ne protège durablement un domaine de production que sur une offre payante.
- Décision et déploiement en attente du choix de l'utilisateur, ainsi que de la disponibilité d'un domaine s'il veut un accès privé réel.

### Publication GitHub Pages — démarrée le 29/09/2026

- À la demande de l'utilisateur, initialisation locale Git et commit `f356976` (`Initial personalized weekly calendar`) sur la branche `main`.
- Dépôt public créé dans l'interface GitHub connectée : `https://github.com/MaxPyroli/calendrier-maxime`.
- La première authentification GitHub CLI par code appareil a expiré côté terminal avant la validation. Le dépôt existe, mais `gh auth status` indique toujours un jeton invalide et `git push` échoue faute d'identifiants schannel.
- Tentative de téléversement via l'interface GitHub préparée ; le sélecteur de fichiers de l'environnement in-app n'a pas déclenché l'événement attendu. Aucun fichier n'a été téléversé et Pages n'est donc pas encore activé.
- À reprendre après une authentification `gh` persistante sur cette machine : configurer le dépôt comme répertoire sûr pour la commande, pousser `main`, puis vérifier le workflow Actions et l'URL Pages. Le fichier `.github/workflows/calendar.yml` est déjà inclus dans le commit.
- Nouvelle vérification après le retour utilisateur « fait » : `gh auth status` reste invalide. La page web de code appareil seule ne suffit pas lorsque le processus `gh auth login` qui l'a générée a déjà été fermé ; l'utilisateur doit lancer et laisser ouverte cette commande dans son propre terminal pendant la validation.
- Deuxième essai fait par l'agent : code appareil `FB89-303B` saisi et accepté dans la session GitHub `MaxPyroli` (page « Congratulations, you're all set! »). Le processus CLI fourni par l'environnement s'était néanmoins déjà arrêté : `gh auth status` est toujours invalide et le push échoue encore avec `SEC_E_NO_CREDENTIALS`.
- Commit local supplémentaire `ea074fe` (`Document GitHub Pages publication status`) créé pour conserver cet état. Il n'est pas sur GitHub, comme le commit initial, faute de jeton Git disponible dans cet environnement.
- L'utilisateur a finalement téléversé les fichiers dans le dépôt via l'interface. Vérification : `public/`, `tests/`, `MEMOIRE.md`, `README.md`, `audit.json`, `filter_calendar.py`, `requirements.txt` et les autres fichiers racine sont sur la branche `main`.
- Afin de rendre GitHub Pages compatible avec la publication depuis la racine, la copie de `public/index.html` vers une nouvelle édition racine `index.html` a été préparée dans l'interface (33 058 caractères collés). Au dernier contrôle, l'édition n'est pas encore commitée : le clic automatisé sur « Commit changes... » n'a pas ouvert la confirmation. Pages n'est pas encore configuré.

### Correction de la position de vague — 29/09/2026

- Problème signalé : la vague était visuellement au milieu du cours en cours alors qu'il restait peu de temps. Elle utilisait le pourcentage horaire de toute la journée, tandis que les cartes de cours ont des hauteurs fixes.
- `template.html` modifié : chaque carte porte désormais ses dates de début et de fin. La vague calcule sa position visuelle dans la carte du cours actif selon l'avancement réel de ce cours ; pendant une pause, elle s'interpole entre les deux cartes. Le pourcentage affiché reste celui de la journée entière.
- `public/index.html` régénéré depuis `work/source.ics` (549 événements retenus sur 1 011, 272 inconnus). Contrôle JavaScript `node --check` réussi. La correction est locale et devra être téléversée dans le dépôt pour modifier le site déjà publié.
- Vérification du site publié : le mardi 29 septembre affiche 42 %. Avec le premier cours à 09:00 et le dernier à 18:30, cette valeur correspond à 4 heures écoulées sur 9 h 30 entre ces bornes ; le calcul ne part donc pas de minuit, mais il inclut les pauses dans l'intervalle. Si l'utilisateur souhaite plutôt un pourcentage de temps d'enseignement effectif, il faudra exclure les pauses entre cours du dénominateur.

### Variante « Prochains cours » — 29/09/2026

- À la demande de l'utilisateur, création d'un deuxième livrable séparé : `../prochains-cours/`. Il ne modifie pas l'interface « Ma semaine ».
- Référence visuelle examinée : écran de départs de `departs.leon.gp`, et dépôt public correspondant identifié : `arnoclr/syspad`. Le dépôt ne contient pas de licence visible ; aucun de ses fichiers ou éléments graphiques n'a été copié.
- Création de `prochains-cours/template.html` : écran de départs adapté aux cours, avec bandeau TM, horloge, code de module, intitulé de cours, heure de début/fin, décompte avant le cours, état « en cours », boutons de navigation des jours et adaptation mobile.
- Création de `prochains-cours/generate.py`, qui incorpore les données déjà filtrées depuis `calendrier-maxime/public/index.html`. Résultat `prochains-cours/index.html` généré : 107 occurrences affichables. Vérification syntaxique JavaScript faite avec `node --check` sur `../../work/prochains-cours.js`.
- Cette variante est locale pour l'instant et ne remplace pas le site GitHub Pages existant.

### Variante syspad autorisée — 29/09/2026

- L'utilisateur indique avoir reçu l'accord explicite de l'auteur et autorise la reprise de `https://github.com/arnoclr/syspad.git`.
- Le clone Git et curl HTTPS échouent dans le terminal isolé (`SEC_E_NO_CREDENTIALS`). Récupération réussie avec Python `urllib` de l'archive GitHub vers `../../work/syspad-reference`; aucun script issu du dépôt n'a été exécuté.
- Création séparée de `../prochains-cours-syspad/` à partir de la base Vue/Vite autorisée. Copie du dépôt, puis remplacement de `src/App.vue` et `src/style.css` pour afficher les cours, et ajout de `src/calendar-data.json` depuis l'aperçu filtré. Les données transport JSON ont été conservées dans la copie mais ne sont plus utilisées par la nouvelle interface.
- Ajout de `ATTRIBUTION.md` afin de documenter la provenance et l'autorisation communiquée par l'utilisateur. Le site « Ma semaine » et la première maquette `../prochains-cours/` restent séparés et inchangés.
- Validation limitée : la dépendance npm n'est pas présente et le binaire npm du runtime connu n'est pas disponible, donc aucun build Vue n'a été exécuté. Vérifier ultérieurement `npm ci` puis `npm run build` dans ce dossier.

Le déploiement en ligne n'a pas été réalisé : aucun dépôt ni compte cible fourni. Les instructions sont prêtes. Une copie locale ne se met pas à jour seule. Le workflow gratuit planifié GitHub peut être retardé et se désactive après 60 jours sans activité du dépôt public. Réexaminer les inconnus avec l'utilisateur si besoin, en particulier les semaines transversales sans atelier nommé et les codes historiques. Ne pas élargir automatiquement les correspondances au risque d'ajouter des cours refusés. Contrôle visuel manuel de la page encore utile. Aucun projet externe ni autre tâche mis de côté ; seule la sortie ICS initiale a été remplacée par l'aperçu hebdomadaire.

## Commandes vérifiées dans cet environnement

Depuis ce dossier, avec PYTHONPATH pointant vers `../../work/python-packages` (chemin absolu sous PowerShell), utiliser le runtime Python indiqué ci-dessus :

```text
python -m unittest discover -s tests -v
python weekly.py --input ../../work/source.ics --week 2026-09-28
```

## Restauration réelle de la coque syspad — 29/09/2026
- Correction de la précédente adaptation : App.vue et style.css restaurés depuis work/syspad-reference. Les composants Header, Stops, AnimatedPath, StopName, MiniETA et leurs animations sont à nouveau utilisés.
- useJourneys.ts remplacé par un adaptateur des événements calendar-data.json : trois prochains cours futurs, triés, noms de cours comme destinations, DTSTART comme heure d'arrivée/départ pour le décompte. Les cours passés sont retirés ; aucun appel API transport nécessaire.
- Logo TM local et libellé « Prochain cours » ; styles du Header conservés. Horaires des codes affichés en Europe/Paris.
- Attention : ce dépôt syspad est un écran de desserte avec plan de ligne ; il ne correspond pas au tableau de départs montré initialement sur departs.leon.gp. Cette différence a été expliquée à l'utilisateur.
- Contrôle vue-tsc réussi (première étape npm run build). Chargement standard de vite.config.ts bloqué par les droits de parcours du sandbox esbuild. Ajout de build-local.mjs appelant directement Vite et son plugin Vue ; build réussi : 57 modules, dist généré. Pas de validation visuelle de cette modification revendiquée.
- Ma semaine et la première maquette restent séparées. Aucun déploiement distant fait. Les données sont un instantané ; réextraire le calendrier pour les actualiser.

## Tableau RER RATP — correction du choix de panneau
- Recherche dans arnoclr/transports-screens-hub/src/screens.ts : RER_RATP_BOARD pointe vers departs.leon.gp avec screenId=rer ; syspad est explicitement un autre écran. Le code du tableau demandé n'a pas été retrouvé dans syspad.
- App.vue/style.css de la variante prochains-cours-syspad remplacés par un tableau fidèle aux caractéristiques observées : bandeau blanc avec ligne rouge, codes violets, destinations bleues, compteurs jaune/noir, horloge supérieure droite, cinq cours actifs/futurs, heures de fin à droite. Il s'agit d'une adaptation écrite localement, pas du code original du panneau leon.gp. Polices existantes de la variante conservées.
- Les cours terminés sont retirés ; cours en cours identifiés ; attente arrondie à la minute supérieure ; indications de date pour éviter de confondre les prochains jours. Les descriptions distantes ne sont pas interprétées comme HTML.
- Vue-tsc et build Vite vérifiés. Aucune publication distante. Ma semaine inchangée. Dist constitue le livrable compilé.

## 2026-09-29 — Recherche des sources chez Leon-ED
- Demande : chercher chez Leon-ED le véritable panneau RER, sans confondre avec SYSPAD.
- Inspection via API GitHub des dépôts publics, puis arbres et fichiers bruts de transport-screens et ecran-ratp.
- transport-screens est une coque physique Angular (cadre/LED/logos) qui embarque une iframe ; app.component.ts référence departs.leon.gp screenId=rer en commentaire. Il ne contient pas le renderer RER.
- ecran-ratp contient réellement un panneau RER A statique : index.html (missions/destinations/attentes/horloge/bandeau), assets/style/style.css, polices Parisine et images RER A. Titres éditables et données fictives. Ce dépôt ancien n'est pas confirmé comme la version actuellement déployée sur departs.leon.gp.
- Aucun changement des applications ni déploiement durant cette recherche. Scripts intermédiaires : work/find_leon_source.py et work/read_leon_source.py.
- Suite possible : adapter ce vrai HTML/CSS aux données de cours ; conserver Ma semaine et ne pas affirmer une identité avec le site actuel sans preuve.

## 2026-09-29 — Adaptation effective du panneau Leon-ED/ecran-ratp
- Création de outputs/prochains-cours-rer, variante statique autonome ; Ma semaine et anciens prototypes conservés sans modification.
- Source figée au commit d713b58063c0fccc188bb431dc0fa7e7fd13832c. Original complet dans original/. Assets copiés, CSS source strictement inchangé (égalité vérifiée). Attribution et absence de LICENSE documentées sans prétendre à une licence libre.
- template.html dérivé du HTML original : suppression des champs éditables, titres de cours, lignes générées, horloge Paris, lien local Ma semaine. courses.js utilise textContent pour les données ; affiche cinq événements horaires actifs/futurs, attente, dates/heures, retire les événements terminés. Données embarquées via generate.py : 107 événements extraits de Ma semaine. Pas de rafraîchissement distant automatique.
- courses.css séparé : adaptations aux intitulés longs et viewport étroit ; aucun redessin du CSS source. Image distante du bandeau remplacée par le logo fourni dans le dépôt.
- Vérification Node : syntaxe valide ; tests ciblés tri, exclusion des événements terminés, cours actif, attente 1h40, arrondi minute et borne de fin réussis. Script work/test-rer.cjs.
- Tentative d'ouverture file:// dans navigateur intégré refusée par politique navigateur (protocoles http/https seulement). Pas de contournement ; vérification visuelle non réalisée. Livraison locale à ouvrir dans navigateur externe. Aucun déploiement.

## 2026-09-29 — Correction amplitude et progression Ma semaine
- Signalement : vagues triangulaires grandissant vers le bas et cours futurs déjà recouverts.
- Cause forme : anciens clip-path polygon utilisaient un pourcentage de toute la colonne remplie. Remplacement effectif par div.day-water, bord SVG courbe de 16px répété tous les 240px ; anciens pseudo-éléments désactivés explicitement. Oscillation verticale de 8 secondes, amplitude maximale 12px constante, masquée par le bloc jour. Dégradé sur les 70 derniers pixels uniquement ; jours passés uniformes.
- Progression courseSurface : positions DOM des cartes et horaires, interpolation dans le cours actif et les pauses ; première carte non terminée en cas de chevauchement ; borne avant toute carte future et amplitude limitée selon distance restante. Tri chronologique explicite. Avant premier cours vide, après dernier cours entièrement rempli. Pourcentage toujours basé premier/dernier cours, indépendant de l'oscillation.
- Mise à jour chaque seconde, recalcul après chargement polices/redimensionnement, nouveau rendu au changement de date.
- Modifications template.html et public/index.html (données embarquées conservées sans redownload). Script work/fix_water.py. Vérification work/test-water.cjs : syntaxe JS, bornes, 11h50 dans cours 9h–12h, simulation minute par minute sans empiètement sur cours futurs réussies.
- Pas de vérification visuelle navigateur dans ce tour ; pas de publication GitHub Pages. Variante RER non modifiée.

## 2026-09-29 — Publication autorisée et correction jours passés
- User a demandé publication puis signalé que les cartes des jours passés passaient devant l'eau. Correction avant publication : ajout du même calque day-water aux jours passés, uniforme, sans animation, z-index 2 au-dessus des cartes z-index 1. Suppression du simple fond bleu qui ne recouvrait pas les cartes.
- template.html et public/index.html régénérés sans changer les données. Tests de progression et syntaxe repassés.
- GitHub CLI fonctionne pour lire le dépôt. Pages API retourne 404 ; inspection des contenus confirme deux fichiers index.html (racine et public) de versions différentes. Publication prévue des deux avec le même HTML corrigé et du template pour conserver la correction lors des prochaines générations.
- Publication non effectuée : gh lit le dépôt public mais POST git/blobs retourne 401 Requires authentication. Navigateur connecté propriétaire ; page upload accessible mais sélecteur filechooser ne s'ouvre ni via bouton ni via input. Aucun fichier envoyé ni commit distant créé. Corrections locales prêtes. Ne pas confondre lecture publique avec authentification CLI valide.
