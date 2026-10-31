# IslamicTikTokAutomation

Automated Arabic and French Islamic reminder videos.

## Objectif

Préparer deux vidéos verticales de rappel islamique par jour : une en arabe et une en français.

## Règles essentielles

- Vérifier les textes religieux et leurs sources avant toute utilisation.
- Ne jamais inventer un verset, un hadith, une attribution ou une traduction.
- Demander une validation humaine avant toute publication.
- La publication automatique reste désactivée par défaut.
- Commencer avec des outils gratuits et limiter les dépendances.

## Format vidéo

- Vertical : 1080 × 1920 (9:16)
- Fréquence cible : 30 FPS
- Langues : arabe et français

## Structure actuelle

- `src/` : code source
- `config/` : exemples de configuration
- `requirements.txt` : dépendances Python (à définir)
- `outputs/` : vidéos générées (non suivies par Git)
- `assets/generated/` : ressources générées (non suivies par Git)

## État du projet

Structure initiale uniquement. Aucun générateur vidéo, service externe ou publication n'est encore configuré.

## Démarrage

Après installation de Python 3.10 ou plus récent :

```bash
python src/main.py
```
