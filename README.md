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
| `icons/` | icônes de l’application |
| `.nojekyll` | publication des fichiers telle quelle par GitHub Pages |

Chaque page est autonome : aucun fichier externe, aucune police ni bibliothèque en ligne.

## Publier une mise à jour

1. Remplacer les fichiers HTML modifiés.
2. Dans `service-worker.js`, incrémenter `VERSION` (`'v1'` → `'v2'`…).
3. Commiter et pousser. Au prochain passage en ligne, les élèves voient « Une nouvelle version des parcours est disponible » et cliquent sur « Mettre à jour ».

Si une nouvelle page est ajoutée, l’ajouter aussi dans la liste `ASSETS` de `service-worker.js` et dans `PAGES` de `index.html`.

## Tester en local

Le service worker ne fonctionne pas en ouvrant les fichiers par double-clic (`file://`). Lancer un petit serveur dans le dossier :

```
python -m http.server 8000
```

puis ouvrir http://localhost:8000.
