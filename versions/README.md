# 3 nouvelles versions de l'interface

Les trois versions ont **exactement les mêmes fonctionnalités** que `app.py` : connexion Google et
code d'invitation, FR/EN, projets (création, édition, membres, suppression par le propriétaire,
export .ics), tâches (cocher, responsable, deadline, durée estimée, modifier/supprimer), « Mes tâches »,
avancement par projet, charge de travail (heures restantes / aujourd'hui / semaine, vues Semaine et
Mois, navigation, sélection d'un jour, tâches ouvertes et terminées), export JSON, Google Calendar
(connexion, synchro, déconnexion confirmée) et déconnexion.

La logique (Supabase, Google Calendar, calculs, actions, dialogues) est partagée dans `core.py`
à la racine. Chaque version ne contient que son interface. `app.py` n'est pas modifié.

| Version | DA | UX |
|---|---|---|
| `v1_atelier` | Éditoriale « papier » : crème, encre noire, vermillon, serif Fraunces | Pas de barre latérale. Bandeau type journal + 3 rubriques (Projets · Planning · Réglages). Index de projets en lignes, colonne « Mes tâches » cochable, tableau de tâches réglé. |
| `v2_console` | Brutaliste / terminal : noir, vert acide, monospace, titres condensés | Rail de commande latéral (navigation, projets avec barres ASCII, système). Projet en Kanban par urgence (En retard · ≤ 3 j · Plus tard · Fait) + ajout rapide d'une tâche en une ligne. |
| `v3_bento` | Douce et ludique : pervenche, tuiles pastel, très arrondi, dégradé corail → violet | Nouvel **Accueil** bento (focus du jour cochable, heures, mini-graphe semaine, projets en anneaux). Barre d'onglets flottante (Accueil · Projets · Planning · Compte). Projet en deux colonnes À faire / Terminées. |

## Lancer en local

Les secrets sont les mêmes que pour `app.py` (`.streamlit/secrets.toml` dans le dossier d'où tu lances).

```bash
cd versions/v1_atelier && streamlit run app.py
```

## Tester sur Streamlit Community Cloud

Crée une nouvelle app sur le même dépôt et indique comme *Main file path* :
`versions/v1_atelier/app.py`, `versions/v2_console/app.py` ou `versions/v3_bento/app.py`,
avec les mêmes Secrets. Pour Google Calendar, ajoute l'URL de la nouvelle app dans
`GOOGLE_REDIRECT_URI` (et dans les URI de redirection autorisées côté Google Cloud).

Le thème (clair/sombre, couleurs) est appliqué par chaque version au démarrage ; le
`.streamlit/config.toml` de chaque dossier sert pour les lancements en local.

## Adopter une version

Quand tu as choisi : remplace le contenu de `app.py` par celui de la version retenue
(et garde `core.py`), ou pointe simplement ton app Streamlit vers le fichier de la version.
