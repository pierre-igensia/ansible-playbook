# Lab 09 – Rôles Ansible

## 🎯 Objectifs
- Créer un rôle Ansible avec `ansible-galaxy init`
- Comprendre la structure d'un rôle (tasks, handlers, templates, defaults, vars, files, meta)
- Utiliser un rôle dans un playbook
- Définir les dépendances entre rôles

## 📋 Prérequis
- Labs 01–08 complétés
- Maîtrise des playbooks, handlers et templates

## ⏱️ Durée estimée
75 minutes

## 🏗️ Mise en place
1. Activer l'environnement virtuel : `source .venv/bin/activate`
2. Se placer dans le répertoire `labs/lab-09-roles/`
3. Vérifier ansible.cfg pointe vers le bon chemin de rôles

## 📚 Concepts expliqués

### Pourquoi les rôles ?
Les rôles permettent de **réutiliser** et **partager** du code Ansible. Un rôle est une unité autonome qui regroupe tasks, handlers, variables, templates et fichiers liés à une fonctionnalité spécifique.

### Structure d'un rôle
```
mon-role/
├── tasks/
│   └── main.yml       # Tâches principales
├── handlers/
│   └── main.yml       # Handlers
├── templates/
│   └── *.j2           # Templates Jinja2
├── files/
│   └── *              # Fichiers statiques
├── vars/
│   └── main.yml       # Variables (priorité haute)
├── defaults/
│   └── main.yml       # Variables par défaut (priorité basse)
├── meta/
│   └── main.yml       # Métadonnées et dépendances
└── README.md
```

### Priorité des variables dans un rôle
- `defaults/main.yml` : priorité la plus basse → facilement surchargées
- `vars/main.yml` : priorité plus haute → difficiles à surcharger

### Création d'un rôle
```bash
ansible-galaxy init mon-role
```

### Utiliser un rôle dans un playbook
```yaml
- hosts: webservers
  roles:
    - role: mon-role
      vars:
        ma_variable: valeur
```

## 🛠️ Exercices

### Exercice 1 – Initialiser un rôle
**But :** Créer la structure d'un rôle avec ansible-galaxy.
**Instructions :**
1. Se placer dans `labs/lab-09-roles/`
2. Exécuter : `ansible-galaxy init roles/serveur-web`
3. Explorer la structure créée avec `tree roles/serveur-web`

**Résultat attendu :** Arborescence complète du rôle avec tous les sous-répertoires.

### Exercice 2 – Écrire les tâches du rôle
**But :** Remplir le rôle `serveur-web` avec des tâches de configuration.
**Instructions :**
1. Modifier `roles/serveur-web/defaults/main.yml` avec les variables par défaut
2. Modifier `roles/serveur-web/tasks/main.yml` avec les tâches
3. Ajouter un template dans `roles/serveur-web/templates/`

**Résultat attendu :** Le rôle crée les fichiers de configuration et les répertoires nécessaires.

### Exercice 3 – Utiliser le rôle dans un playbook
**But :** Appeler le rôle depuis un playbook.
**Instructions :**
1. Créer `playbooks/site.yml` qui utilise le rôle
2. Exécuter : `ansible-playbook -i inventory/hosts.ini playbooks/site.yml`
3. Vérifier que les fichiers ont été créés

**Résultat attendu :** Tous les fichiers du rôle sont créés avec les bonnes permissions.

### Exercice 4 – Dépendances de rôles
**But :** Définir une dépendance entre deux rôles.
**Instructions :**
1. Créer un second rôle `roles/base-securite`
2. Ajouter la dépendance dans `roles/serveur-web/meta/main.yml`
3. Relancer le playbook et observer l'ordre d'exécution

**Résultat attendu :** Le rôle `base-securite` s'exécute avant `serveur-web`.

## ✅ Validation
```bash
# Vérifier la structure du rôle
tree roles/serveur-web

# Exécuter le playbook
ansible-playbook -i inventory/hosts.ini playbooks/site.yml

# Vérifier l'idempotence (2ème exécution = aucun changed)
ansible-playbook -i inventory/hosts.ini playbooks/site.yml
```

## 🔍 Pour aller plus loin
- [Documentation Ansible sur les rôles](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_reuse_roles.html)
- [Ansible Galaxy](https://galaxy.ansible.com/)
- **Défi 1** : Publier votre rôle sur Ansible Galaxy (créer un compte, `ansible-galaxy role import`)
- **Défi 2** : Installer un rôle depuis Galaxy avec `ansible-galaxy install geerlingguy.docker`

## 💡 Solutions
<details>
<summary>Solution</summary>

### Solution Exercice 1
```bash
cd labs/lab-09-roles/
ansible-galaxy init roles/serveur-web
tree roles/serveur-web
```

### Solution Exercice 2
Contenu de `roles/serveur-web/defaults/main.yml` :
```yaml
---
serveur_web_port: 80
serveur_web_racine: /tmp/www
serveur_web_nom: "mon-serveur"
```

Contenu de `roles/serveur-web/tasks/main.yml` :
```yaml
---
- name: Créer le répertoire web
  ansible.builtin.file:
    path: "{{ serveur_web_racine }}"
    state: directory
    mode: '0755'

- name: Déployer la page d'accueil
  ansible.builtin.template:
    src: index.html.j2
    dest: "{{ serveur_web_racine }}/index.html"
    mode: '0644'
  notify: Recharger le serveur web
```

### Solution Exercice 3
```yaml
---
- name: Déploiement du serveur web
  hosts: local
  roles:
    - role: serveur-web
      vars:
        serveur_web_port: 8080
```

```bash
ansible-playbook -i inventory/hosts.ini playbooks/site.yml
```
</details>
