# Usage (depuis backend/docker-compose.yml) : docker-compose up --build

# --- Stage 1 : build de l'app Angular ---
FROM node:22-alpine AS build

WORKDIR /app

# Installer les dépendances (couche mise en cache tant que package*.json ne change pas)
COPY package.json package-lock.json ./
RUN npm ci

# Copier le code et compiler en production
COPY . .
RUN npm run build

# --- Stage 2 : servir les fichiers statiques avec nginx ---
FROM nginx:alpine

# Config nginx (SPA fallback pour le routing Angular)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copier le build (Angular 21 génère dans dist/frontend/browser)
COPY --from=build /app/dist/frontend/browser /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
