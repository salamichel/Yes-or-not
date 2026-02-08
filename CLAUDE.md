# Yes or Not – Site vitrine du groupe

## Stack technique

- **Backend** : Django 5.2 (Python)
- **Frontend** : Templates Django + CSS vanilla (dark theme) + JS vanilla
- **Base de données** : SQLite (dev), prévoir PostgreSQL en production
- **Médias** : Pillow pour le traitement d'images (avatars, pochettes, affiches)
- **Hébergement** : Non configuré – à définir

## Structure du projet

```
Yes-or-not/
├── yesornot/              # Configuration Django (settings, urls, wsgi)
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── band/                  # Application principale
│   ├── models.py          # Modèles de données (9 modèles)
│   ├── views.py           # Vues (10 vues)
│   ├── urls.py            # Routage (9 routes)
│   ├── admin.py           # Configuration back-office
│   ├── templates/band/    # Templates HTML (10 fichiers)
│   └── migrations/
├── static/
│   ├── css/style.css      # Styles (dark theme, responsive, CSS variables)
│   └── js/main.js         # JS minimal (nav mobile, alerts)
├── media/                 # Uploads (avatars, pochettes, affiches) – gitignored
└── manage.py
```

## Modèles de données

| Modèle               | Description                                      |
|-----------------------|--------------------------------------------------|
| `SiteSettings`        | Singleton – nom du groupe, tagline, logo, réseaux sociaux, email |
| `Member`              | Membre du groupe – prénom, nom, rôle, avatar, bio, ordre |
| `MemberPortfolioItem` | Portfolio d'un membre – titre, description, image, vidéo |
| `Album`               | Album / EP – titre, pochette, date, liens streaming |
| `Track`               | Piste d'un album – titre, numéro, durée          |
| `Video`               | Vidéo (embed YouTube) – titre, URL, miniature, mise en avant |
| `Event`               | Date de concert – titre, date, lieu, ville, billetterie, affiche |
| `ContactMessage`      | Message reçu via formulaire – nom, email, sujet, message |
| `Page`                | Contenu éditorial par rubrique – titre, sous-titre, texte, bannière |

## Pages et routes

| Route                  | Vue              | Template              |
|------------------------|------------------|-----------------------|
| `/`                    | `home`           | `home.html`           |
| `/le-groupe/`          | `about`          | `about.html`          |
| `/membres/`            | `members_list`   | `members.html`        |
| `/membres/<id>/`       | `member_detail`  | `member_detail.html`  |
| `/albums/`             | `albums_list`    | `albums.html`         |
| `/albums/<id>/`        | `album_detail`   | `album_detail.html`   |
| `/videos/`             | `videos_list`    | `videos.html`         |
| `/dates/`              | `events_list`    | `events.html`         |
| `/contact/`            | `contact`        | `contact.html`        |
| `/admin/`              | Back-office Django | –                   |

## Back-office (admin)

Accessible via `/admin/`. Toutes les sections sont administrables :
- **Paramètres du site** : singleton, pas de suppression possible
- **Membres** : inline pour les éléments de portfolio, ordre modifiable en liste
- **Albums** : inline pour les pistes (tracklist)
- **Vidéos** : mise en avant éditable directement en liste
- **Événements** : filtre par ville, annulation en liste
- **Messages de contact** : lecture seule, marquage lu/non-lu
- **Pages** : contenu éditorial de chaque rubrique (titre, sous-titre, texte, bannière)

## Commandes utiles

```bash
# Installation
pip install django pillow

# Migrations
python manage.py makemigrations band
python manage.py migrate

# Créer un admin
python manage.py createsuperuser

# Lancer le serveur de dev
python manage.py runserver

# Vérification du projet
python manage.py check
```

## Design

- **Thème** : Sombre (dark), palette rock/alternative
- **Couleurs CSS** (variables dans `:root`) :
  - `--color-bg: #0a0a0a` (fond)
  - `--color-primary: #e63946` (rouge, CTA)
  - `--color-accent: #f1faee` (textes clairs)
- **Responsive** : breakpoint principal à 768px, grilles CSS adaptatives
- **Typographie** : Segoe UI (corps) + Georgia (titres)

## Conventions de code

- Langue du code : **anglais** (noms de modèles, vues, URLs)
- Labels et verbose_name : **français** (interface admin et formulaires)
- Templates : héritage via `base.html`, blocs `title`, `content`, `extra_head`, `extra_js`
- Context commun : la fonction `get_context(slug)` injecte `settings` et `page` dans chaque vue

## Points d'attention / TODO

- [ ] Ajouter un fichier `requirements.txt` complet avec versions pinées
- [ ] Configurer PostgreSQL pour la production
- [ ] Ajouter HTTPS et variables d'environnement pour `SECRET_KEY`
- [ ] Configurer le stockage media (S3 ou équivalent) pour la production
- [ ] Ajouter des tests unitaires
- [ ] Optimiser les images (thumbnails automatiques)
- [ ] SEO : meta descriptions, Open Graph tags
- [ ] Ajouter un sitemap.xml et robots.txt
