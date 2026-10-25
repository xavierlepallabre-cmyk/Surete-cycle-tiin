# Sûreté & Cycle TIIN

Parcours interactifs pour le Bac Pro TIIN (Lycée Alexis de Tocqueville) : cycle du combustible (amont, REP 1300, La Hague, Andra), sûreté nucléaire et accidents.
Site statique, installable sur smartphone et tablette, utilisable entièrement hors connexion après la première visite.

Projet indépendant de Nucléa TIIN : dépôt, cache hors ligne (`surete-cycle-tiin-…`) et réglages séparés.

## Contenu

| Fichier | Rôle |
|---|---|
| `index.html` | page d’accueil et navigation entre les six parcours |
| `amont.html`, `rep1300.html`, `lahague.html`, `andra.html` | cycle du combustible |
| `surete.html`, `accidents.html` | sûreté nucléaire, accidents et retour d’expérience |
| `manifest.json` | installation sur l’écran d’accueil |
| `service-worker.js` | mise en cache pour l’usage hors ligne |
| `icons/` | icônes de l’application (le dossier doit rester un dossier : le manifeste et le cache y pointent) |
| `tools/version.py` | calcule la version du cache à partir du contenu des fichiers |
| `tests/test_site.py` | tests de non-régression dans un vrai navigateur |
| `SOURCES.md` | sources de chaque donnée datée ou réglementaire |
| `.nojekyll` | publication des fichiers telle quelle par GitHub Pages |

Chaque page est autonome : aucun fichier externe, aucune police ni bibliothèque en ligne.

## Publier une mise à jour

1. Remplacer les fichiers HTML modifiés.
2. Lancer `python tools/version.py` : la version du cache est recalculée à partir du contenu.
3. Lancer `python tests/test_site.py` (voir plus bas) : 36 vérifications doivent réussir.
4. Commiter et pousser. Au prochain passage en ligne, les élèves voient « Une nouvelle version des parcours est disponible » et cliquent sur « Mettre à jour ».

## Tests

Une fois : `pip install playwright` puis `python -m playwright install chromium`.
Ensuite : `python tests/test_site.py`. Le script vérifie la version du cache, l’ouverture des sept pages en thème clair et sombre, toutes les vues, étapes et mises en situation de Sûreté et Accidents, l’absence de débordement à 360 px, les liens entre parcours, le fonctionnement hors ligne et la proposition de mise à jour.

Si une nouvelle page est ajoutée, l’ajouter aussi dans la liste `ASSETS` de `service-worker.js` et dans `PAGES` de `index.html`.

## Tester en local

Le service worker ne fonctionne pas en ouvrant les fichiers par double-clic (`file://`). Lancer un petit serveur dans le dossier :

```
python -m http.server 8000
```

puis ouvrir http://localhost:8000.
