# Système de Gestion d'un Bureau d'Architecte

Application web interne développée avec Django pour la gestion des clients, des projets, des employés et des tâches d'un bureau d'architecte.

## 1. Présentation du projet

Ce projet a pour objectif de faciliter la gestion des activités d'un bureau d'architecte à travers une application web interne.

L'application permet de gérer les clients, les projets, les architectes et les tâches, ainsi que de consulter les principales statistiques depuis un tableau de bord.

Elle propose trois rôles :

- **Administrateur :** gestion complète du système.
- **Architecte :** consultation des projets qui lui sont attribués et mise à jour des projets et des tâches.
- **Assistant :** consultation des informations avec un accès en lecture seule.

## 2. Technologies utilisées

- **Backend :** Python, Django
- **Frontend :** HTML, JavaScript, Tailwind CSS
- **Base de données :** MySQL
- **Bibliothèques JavaScript :** Chart.js, Lucide
- **Outils :** Git, GitHub, VS Code

## 3. Fonctionnalités principales

- Authentification et déconnexion.
- Gestion des utilisateurs et des rôles.
- Gestion des clients.
- Gestion des projets.
- Attribution des projets aux architectes.
- Gestion des tâches liées aux projets.
- Tableau de bord avec statistiques.
- Consultation des projets et des tâches selon le rôle.
- Validation des formulaires et gestion des erreurs.

## 4. Prérequis

Avant d'installer le projet, assurez-vous de disposer des éléments suivants :

- Python 3.14
- pip
- Node.js et npm
- MySQL Server 8.4
- Git

## 5. Installation

### 5.1 Cloner le projet

```bash
git clone https://github.com/ElFirdaous28/architecture-office-management.git

cd architecture-office-management
```

### 5.2 Créer un environnement virtuel

```bash
python3 -m venv .venv
```

Activer l'environnement virtuel :

```bash
source .venv/bin/activate
```

### 5.3 Installer les dépendances Python

```bash
pip install -r requirements.txt
```

### 5.4 Configurer MySQL

Créer une base de données MySQL :

```sql
CREATE DATABASE architecture_office
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

Créer un utilisateur MySQL pour l'application :

```sql
CREATE USER 'architecture_user'@'localhost'
IDENTIFIED BY 'your_password';
```

Accorder les permissions nécessaires :

```sql
GRANT ALL PRIVILEGES ON architecture_office.*
TO 'architecture_user'@'localhost';

FLUSH PRIVILEGES;
```

Remplacer `your_password` par un mot de passe sécurisé.

### 5.5 Configurer les variables d'environnement

Créer le fichier `.env` :

```bash
cp .env.example .env
```

### 5.6 Appliquer les migrations

```bash
python manage.py migrate
```

### 5.7 Installer les dépendances frontend

```bash
npm install
```

### 5.8 Compiler les fichiers frontend

Compiler les fichiers CSS et JavaScript :

```bash
npm run build
```

Cette commande génère :

- Le CSS optimisé.
- Le JavaScript du tableau de bord administrateur.
- Le JavaScript du tableau de bord architecte.
- Le JavaScript du tableau de bord assistant.

Pour compiler uniquement les fichiers CSS :

```bash
npm run build:css
```

Pour compiler le JavaScript :

```bash
npm run build:js
npm run build:architect-js
npm run build:assistant-js
```

Pour lancer la compilation automatique du CSS pendant le développement :

```bash
npm run dev
```

### 5.9 Créer un compte administrateur

```bash
python manage.py createsuperuser
```

Suivre les instructions pour créer le compte.

### 5.10 Lancer l'application

```bash
python manage.py runserver
```

Ouvrir l'application dans le navigateur :

http://127.0.0.1:8000/

## 6. Utilisation de l'application

### Administrateur

L'administrateur peut :

- Consulter le tableau de bord.
- Gérer les utilisateurs.
- Gérer les clients.
- Créer et modifier les projets.
- Attribuer les projets aux architectes.
- Gérer les tâches.

### Architecte

L'architecte peut :

- Consulter son tableau de bord.
- Consulter les projets qui lui sont attribués.
- Mettre à jour les projets et les tâches selon ses permissions.

### Assistant

L'assistant peut consulter les informations disponibles dans l'application.

Ses permissions sont limitées à la consultation.

## 7. Tests

Les tests automatisés sont organisés dans les applications principales :

- `accounts/tests.py`
- `clients/tests.py`
- `projects/tests.py`
- `tasks/tests.py`

Pour exécuter les tests :

```bash
python manage.py test
```

## 8. Structure du projet

```text
architecture-office-management/
├── accounts/
├── clients/
├── projects/
├── tasks/
├── config/
├── core/
├── diagrams/
├── static/
├── templates/
├── manage.py
├── requirements.txt
├── package.json
└── README.md
```

## 9. Auteur

Projet réalisé dans le cadre d'un stage de développement web.