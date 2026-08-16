# AnonBox

Projet dédié à AnonBox. Ce dépôt contient l'application Android, l'interface web publique et les workflows de compilation/déploiement.

## Architecture

- `android/` : application Android installable pour le propriétaire de la boîte.
- `web/` : interface navigateur pour l'espace privé et les pages publiques de messages.
- `.github/workflows/anonbox-android.yml` : compilation automatique de l'APK.
- `.github/workflows/pages.yml` : déploiement de l'interface web avec GitHub Pages.

## Backend

AnonBox utilise Supabase pour l'authentification, les profils, les boîtes et les messages.

## Important

Pour que le lien public GitHub Pages et le téléchargement APK soient accessibles sans connexion GitHub, ce dépôt doit être public. Une fois GitHub Pages activé, l'URL prévue est :

`https://nadmit21-ux.github.io/AnonBox/`
