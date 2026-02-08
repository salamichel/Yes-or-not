# Yes or Not – Site vitrine du groupe

## Stack technique

- **Backend** : Django 5.2 (Python) + Gunicorn
- **Frontend** : Templates Django + CSS vanilla (dark theme) + JS vanilla
- **Base de données** : PostgreSQL 16 (Docker) / SQLite (dev local sans Docker)
- **Reverse proxy** : Nginx (sert les fichiers statiques et media)
- **Médias** : Pillow pour le traitement d'images (avatars, pochettes, affiches)
- **Email transactionnel** : Brevo (ex-Sendinblue) API v3
- **Conteneurisation** : Docker Compose (3 services : web, db, nginx)

## Structure du projet

```
Yes-or-not/
├── docker-compose.yml     # Orchestration des 3 services
├── Dockerfile             # Image Django + Gunicorn
├── entrypoint.sh          # Wait for DB + migrate + collectstatic
├── .env.example           # Variables d'environnement (template)
├── .dockerignore
├── nginx/
│   └── default.conf       # Config Nginx (proxy + static/media)
├── yesornot/              # Configuration Django
│   ├── settings.py        # Settings avec DATABASE_URL conditionnel
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
├── requirements.txt       # Django, Pillow, Gunicorn, psycopg, requests
└── manage.py
```

## Docker Compose – Services

| Service | Image               | Rôle                                    | Port exposé |
|---------|---------------------|-----------------------------------------|-------------|
| `db`    | `postgres:16-alpine`| Base de données PostgreSQL              | interne     |
| `web`   | Build depuis `./`   | Django + Gunicorn (3 workers)           | interne     |
| `nginx` | `nginx:alpine`      | Reverse proxy, fichiers statiques/media | `80`        |

### Volumes persistants

- `postgres_data` : données PostgreSQL
- `static_files` : fichiers statiques collectés (`collectstatic`)
- `media_files` : uploads utilisateurs (avatars, pochettes, affiches)

## Commandes Docker

```bash
# Copier et éditer les variables d'environnement
cp .env.example .env
# ⚠️  Modifier les valeurs dans .env (mot de passe, secret key, domaine)

# Lancer tous les services (build + démarrage)
docker compose up --build -d

# Créer un superutilisateur admin
docker compose exec web python manage.py createsuperuser

# Voir les logs
docker compose logs -f web

# Arrêter
docker compose down

# Arrêter et supprimer les volumes (⚠️ perte de données)
docker compose down -v
```

## Développement local (sans Docker)

```bash
pip install -r requirements.txt

# Sans DATABASE_URL → utilise SQLite automatiquement
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Variables d'environnement (.env)

| Variable               | Description                           | Défaut                 |
|------------------------|---------------------------------------|------------------------|
| `POSTGRES_DB`          | Nom de la base PostgreSQL             | `yesornot`             |
| `POSTGRES_USER`        | Utilisateur PostgreSQL                | `yesornot`             |
| `POSTGRES_PASSWORD`    | Mot de passe PostgreSQL               | `yesornot_secret`      |
| `DJANGO_SECRET_KEY`    | Clé secrète Django                    | (insecure par défaut)  |
| `DJANGO_DEBUG`         | Mode debug (`True`/`False`)           | `False` en Docker      |
| `DJANGO_ALLOWED_HOSTS` | Hosts autorisés (séparés par `,`)     | `localhost,127.0.0.1`  |
| `DATABASE_URL`         | URL PostgreSQL (auto-généré par compose) | –                   |
| `BREVO_API_KEY`        | Clé API Brevo (transactional emails)  | –                      |
| `BREVO_SENDER_EMAIL`   | Email expéditeur Brevo                | `contact@yesornot.fr`  |
| `BREVO_SENDER_NAME`    | Nom expéditeur Brevo                  | `Yes or Not`           |
| `BREVO_RECIPIENT_EMAIL`| Email destinataire des messages       | `contact@yesornot.fr`  |
| `PORT`                 | Port Nginx exposé sur l'hôte          | `80`                   |

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
- Settings : `DATABASE_URL` présent → PostgreSQL, absent → SQLite (dev local)

## Points d'attention / TODO

- [ ] Configurer HTTPS (Let's Encrypt / Certbot dans Nginx)
- [ ] Configurer le stockage media (S3 ou équivalent) pour la production
- [ ] Ajouter des tests unitaires
- [ ] Optimiser les images (thumbnails automatiques)
- [ ] SEO : meta descriptions, Open Graph tags
- [ ] Ajouter un sitemap.xml et robots.txt
