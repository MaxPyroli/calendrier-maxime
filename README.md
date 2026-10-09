# Ma semaine TRAME — Maxime

Le résultat principal est **une page hebdomadaire**, conformément à la demande précisée : cours par jour, horaires de Paris et navigation entre semaines. Les salles ne sont pas affichées. Aucun abonnement iCal n'est nécessaire. La page HTML fonctionne aussi en ouvrant le fichier localement.

Chaque journée avec horaires précis affiche un fin repère coloré pour le début et la fin des cours. Un repère ocre « Pause déjeuner » indique seulement la durée libre autour de midi. Il est calculé à partir des cours affichés : ce n'est pas une pause officielle. Pour un atelier continu, aucune pause n'est inventée et une mention signale l'absence de précision.

Les événements toute la journée (ou intitulés « journée ») apparaissent en violet, sur une ligne à droite du jour. Ceux sur plusieurs jours apparaissent en bleu sur chaque jour concerné. Ils ne sont pas dupliqués dans la liste des cours.

La progression de la semaine forme une seule vague : toute date passée, y compris dans les semaines précédentes et même sans cours identifié, est remplie uniformément d'eau bleue et reste immobile. Le jour en cours est le seul à conserver la vague douce animée ; les jours futurs restent vides. La couche d'eau active est volontairement plus large et plus haute que la carte, mais elle est découpée par les bords arrondis de celle-ci. Son mouvement vertical, plus ample et plus lent, ne devient donc visible qu'à la surface basse, jamais au-dessus de la carte. Le pourcentage de la journée, sans libellé, se place à l'extérieur de la carte, à droite et à la hauteur moyenne de la vague ; il se recale aussi au redimensionnement, sans animer ses petits ajustements horaires. Chaque cours est présenté dans son propre bloc, sans bande colorée latérale. Les jours s'affichent sur une seule colonne, avec une largeur maximale de 640 px. L'animation est désactivée si l'appareil demande de réduire les animations. Ce repère n'est pas affiché quand la journée ne contient pas de créneau horaire exploitable.

## Mise en place gratuite : GitHub Actions + Pages

1. Créer un dépôt **public** GitHub nommé, par exemple, `calendrier-trame`, avec une branche `main`.
2. Y copier le **contenu** de ce dossier, y compris `.github/workflows/calendar.yml` et `.gitignore`. Le dossier `.github` peut être masqué dans certains explorateurs.
3. Dans **Settings → Pages → Build and deployment → Source**, choisir **GitHub Actions**.
4. Dans **Actions → Actualiser le calendrier → Run workflow**, lancer la première génération sur `main` (ou pousser un commit).
5. Ouvrir `https://VOTRE-COMPTE.github.io/calendrier-trame/`. Ajouter cette adresse aux favoris, ou à l'écran d'accueil du téléphone.

Le workflow télécharge la source et reconstruit la page toutes les six heures, à la minute 17 (UTC). Il ne nécessite aucun secret ni serveur. Pages est disponible pour les dépôts publics avec GitHub Free et les runners standard Actions sont gratuits pour les dépôts publics. Les données affichées et le code seront publics. Les descriptions ne sont pas affichées ; elles servent uniquement au filtrage.

Les tâches planifiées peuvent être retardées par GitHub. Elles sont désactivées après 60 jours sans activité dans un dépôt public : vérifier Actions et réactiver le workflow si nécessaire. Ce service n'est donc pas une notification garantie de changement de salle de dernière minute. La date de mise à jour figure en bas de page. En cas d'échec de téléchargement ou de validation, le dernier déploiement reste en place.

## Exécution locale

Python 3.11 ou supérieur :

```sh
python -m venv .venv
# Windows : .venv\Scripts\activate
# macOS / Linux : source .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python weekly.py
```

Ouvrir `public/index.html`. Pour une autre date ou une source téléchargée :

```sh
python weekly.py --week 2026-09-28
python weekly.py --input source.ics --week 2026-10-05
```

La page contient 25 semaines : douze avant et douze après la semaine choisie. Les flèches et le sélecteur naviguent dans cette période. À l'ouverture, la page affiche directement la semaine en cours et défile jusqu'au jour actuel (le lundi, premier jour de la semaine, elle reste en haut) ; la semaine choisie à la génération n'est qu'un repère pour la plage de 25 semaines. Le bouton « Cette semaine » fait de même et, dans une ancienne copie dont la plage ne contient plus aujourd'hui, revient à la limite disponible sans défiler. Le fichier local est un instantané ; la version hébergée est reconstruite automatiquement. Recharger la page pour voir une nouvelle génération.

## Filtrage et limites explicites

Correction du 29/09/2026 fondée sur le livret M2 TRAME 2026–2027 fourni : les UE obligatoires « Réseaux et territoires » (p. 5), « Transitions socio-écologiques et environnementales » (p. 6), « Planification, gouvernance, politiques et action publique » (p. 7) et « Usages, usagers, pratiques sociales » (p. 8) sont reconnues explicitement, en plus des enjeux et controverses déjà couverts. Les intitulés de professionnalisation (p. 39) sont également reconnus. Les intitulés abrégés exacts « Transition » et « Transitions » sont rattachés à l'UE commune ; « High tech / low tech » est rattaché au cours RIS et exclu. Les choix personnels d'options restent ceux indiqués par Maxime, même lorsqu'un cours non choisi figure au catalogue TM. Aucun numéro UE seul n'autorise un événement : ces numéros se répètent entre blocs.

`rules.json` contient les motifs nommés. Normalisation des accents, casse, apostrophes, tirets, ponctuation et entités HTML. Le titre et la description sont examinés séparément. **Exclusion prioritaire**, puis liste d'autorisation ; un cours inconnu est masqué et consigné dans `audit.json`. Les expressions reconnaissent les noms complets des cours avec des préfixes UE/EC et suffixes de salle ; il ne s'agit pas d'une recherche générique du mot « transport ».

- ACOST / Analyse et conception des systèmes de transport est autorisé ; Conception systèmes transport et mobilité est exclu.
- Économie des réseaux est autorisé à tous niveaux. Économie des transports débutants n'est pas assimilé à ce cours et reste masqué.
- SIG est exclu sauf lorsque le même champ précise les données de mobilité autorisées.
- Les intitulés « Atelier », « Atelier (journée) », ateliers TM, restitutions et certains suffixes de salle sont considérés comme le projet commun. Tout atelier portant un autre nom doit être explicitement reconnu.
- « Semaine transversale 1/2 » sans nom d'atelier reste masqué. Les codes historiques EC seuls ne suffisent pas à établir une équivalence avec les cours attribués.
- Une description listant à la fois un cours autorisé et un cours exclu provoque l'exclusion : revoir le rapport pour les descriptions génériques.
- Aucun filtre d'année n'est appliqué à la source ; seule la fenêtre hebdomadaire limite l'affichage.

La source réelle contient des intitulés historiques dont l'équivalence au profil actuel n'est pas démontrée. Ajouter des alias dans `rules.json` seulement après confirmation pédagogique, puis relancer le workflow. Consulter `audit.json` localement, ou télécharger l'artefact `audit-filtrage` d'une exécution GitHub (conservé sept jours). `classification` indique keep/exclude/unknown et `kept` la décision finale.

Les récurrences sont développées par `recurring-ical-events` avec les exceptions et fuseaux. Les événements annulés ne sont pas affichés. Les journées entières et événements sur plusieurs jours sont pris en compte. Par prudence, une série récurrente contenant une exception interdite ou ambiguë est entièrement masquée : cela évite de réintroduire une occurrence interdite par sa règle de récurrence. Une exception sans texte hérite du maître autorisé.

## Ancienne piste iCal

`filter_calendar.py` conserve le moteur et une commande d'export optionnelle (`python filter_calendar.py`). Le workflow principal **ne génère ni ne publie de nouveau fichier .ics**. Cette piste est conservée pour une éventuelle reprise ; les UID, dates, SEQUENCE, règles de récurrence, alarmes et fuseaux des événements gardés restent préservés dans cet export.

## Fichiers et reprise

- `weekly.py` : génération hebdomadaire et développement des récurrences.
- `template.html` : interface autonome, données distantes insérées comme texte.
- `filter_calendar.py`, `rules.json` : moteur de filtrage.
- `tests/test_calendar.py` : cas de filtrage, récurrence, stabilité, sécurité d'affichage.
- `MEMOIRE.md` : historique, vérifications et tâches restantes.

## Références

- [Source publique M2 TM](https://calendar.google.com/calendar/ical/m2.tm.orga%40gmail.com/public/basic.ics)
- [GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages)
- [Facturation Actions](https://docs.github.com/en/billing/concepts/product-billing/github-actions)
- [Déclencheurs et limites des tâches planifiées](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)
- [Bibliothèque icalendar](https://icalendar.readthedocs.io/en/latest/how-to/usage.html)
