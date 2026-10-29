# Kollekt / ALK IMPORT — version Django

Conversion complète de la maquette Next.js (React + Tailwind) en projet Django « pur » :
templates Django, vues, modèles, authentification et tableau de bord, sans Node ni React.

## Démarrage

```bash
python -m venv .venv && source .venv/bin/activate      # Windows : .venv\Scripts\activate
pip install -r requirements.txt

python manage.py makemigrations shop
python manage.py migrate
python manage.py seed_demo          # charge les 8 produits de la maquette
python manage.py createsuperuser    # votre compte administrateur
python manage.py runserver
```

- Boutique : http://127.0.0.1:8000/
- Tableau de bord : http://127.0.0.1:8000/gestion/ (compte staff / superuser)
- Admin Django : http://127.0.0.1:8000/admin/

## Correspondance Next.js → Django

| Next.js | Django |
|---|---|
| `app/page.tsx` (accueil) | `shop/views.py::home` + `templates/shop/home.html` |
| tableau `products` en dur | modèles `Product` / `Category` (éditables dans l'admin) |
| modale « Se connecter » | `/connexion/` (`LoginView`) |
| modale « Créer un compte » | `/inscription/` (`RegisterForm`, nom + téléphone + mot de passe) |
| modale « Rejoindre la commande » | `/offres/<slug>/rejoindre/` → crée une `Order`, décrémente le stock |
| `AdminDashboard` | `/gestion/<onglet>/` : vraies données (CA, commandes, clients, paiements, catalogue) |
| `useState(isAdmin)` | `user.is_staff` |
| `layout.tsx` / `globals.css` | `templates/base.html` (polices, Tailwind, favicons) |
| `lucide-react` | Lucide via CDN (`data-lucide`) |
| `public/` | `shop/static/shop/` |

## Changements volontaires

- **Sécurité** : l'ancien code avait l'identifiant admin et le mot de passe **écrits en clair dans le JavaScript**
  (visibles par n'importe quel visiteur). Il n'y a plus de mot de passe en dur : l'accès admin passe par un vrai compte
  Django (`createsuperuser`). Pensez à changer l'ancien mot de passe partout où vous l'utilisez.
- Le bloc « Arrivée prévue » était affiché deux fois par carte : il n'apparaît plus qu'une fois.
- La barre de progression utilisait `commandes réunies` comme pourcentage ; elle est maintenant `réunies / (réunies + restantes)`.
- « 3 offres ouvertes » est désormais calculé (nombre de produits avec des places restantes).
- Le mot de passe d'inscription est confirmé (2 champs) et validé par les validateurs Django.

## À prévoir ensuite

- **Connexion Google** : bouton présent mais désactivé. Installer `django-allauth` pour l'activer.
- **Images produits** : pour l'instant les URLs Vercel Blob de la maquette (champ `image_url`). Vous pouvez téléverser
  vos propres fichiers via le champ `image` dans l'admin (dossier `media/`). Idem pour le logo (`SITE_LOGO_URL` dans `settings.py`).
- **Tailwind** : chargé via le script navigateur (`@tailwindcss/browser`) pour que tout marche sans build.
  Pour la production, compilez le CSS (ex. `django-tailwind-cli`) et remplacez ce script.
- **Paiement** : les statuts (En attente / Confirmée / Payée / Livrée / Annulée) se gèrent à la main dans `/gestion/commandes/`.
  Aucun prestataire de paiement (Mixx, Flooz, CinetPay…) n'est branché.
- **Production** : définir `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0`, `DJANGO_ALLOWED_HOSTS`, passer à PostgreSQL,
  servir les fichiers statiques (WhiteNoise ou Nginx) après `collectstatic`.
