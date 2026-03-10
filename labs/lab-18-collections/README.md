# Lab 18 – Collections Ansible

## 🎯 Objectifs

- Comprendre le concept de collections Ansible
- Installer des collections depuis Ansible Galaxy et Automation Hub
- Utiliser des modules et rôles issus de collections dans les playbooks
- Créer un fichier `requirements.yml` pour gérer les dépendances
- Découvrir la structure interne d'une collection

## 📋 Prérequis

- Labs 01–17 complétés
- Maîtrise des rôles Ansible (Lab 09)
- Environnement virtuel Python activé

## ⏱️ Durée estimée

60 minutes

## 🏗️ Mise en place

```bash
# Activer l'environnement virtuel
source ~/ansible-venv/bin/activate

# Se placer dans le répertoire du lab
cd labs/lab-18-collections/

# Vérifier la version d'Ansible (collections disponibles depuis 2.9+)
ansible --version
```

## 📚 Concepts expliqués

### Qu'est-ce qu'une collection ?

Une collection est un **format de distribution** qui regroupe :
- Des **modules** (plugins)
- Des **rôles**
- Des **plugins** (filter, callback, inventory, etc.)
- De la **documentation**

Avant les collections, chaque module était intégré au cœur d'Ansible. Depuis Ansible 2.10, la majorité des modules sont distribués via des collections.

### Nommage FQCN (Fully Qualified Collection Name)

```yaml
# Ancien style (déprécié)
- name: Copier un fichier
  copy:
    src: fichier.txt
    dest: /tmp/

# Nouveau style avec FQCN (recommandé)
- name: Copier un fichier
  ansible.builtin.copy:
    src: fichier.txt
    dest: /tmp/
```

Le format est : `namespace.collection.module`

### Collections populaires

| Collection | Description |
|-----------|-------------|
| `ansible.builtin` | Modules de base intégrés |
| `community.general` | Modules communautaires généraux |
| `community.docker` | Gestion de Docker |
| `amazon.aws` | Services AWS |
| `google.cloud` | Services GCP |
| `community.mysql` | Gestion MySQL |
| `ansible.posix` | Modules POSIX (cron, sysctl, etc.) |

### Installer des collections

```bash
# Depuis Galaxy
ansible-galaxy collection install community.general

# Depuis un fichier requirements.yml
ansible-galaxy collection install -r requirements.yml

# Dans un répertoire spécifique
ansible-galaxy collection install community.docker -p ./collections/
```

### Fichier requirements.yml

```yaml
---
collections:
  - name: community.general
    version: ">=7.0.0"
  - name: community.docker
    version: "3.4.0"
  - name: ansible.posix
```

## 🛠️ Exercices

### Exercice 1 – Lister et installer des collections

**But :** Découvrir les collections disponibles et en installer.

**Instructions :**

1. Lister les collections déjà installées :
```bash
ansible-galaxy collection list
```

2. Installer la collection `community.general` :
```bash
ansible-galaxy collection install community.general
```

3. Vérifier l'installation :
```bash
ansible-galaxy collection list | grep community.general
```

4. Explorer la documentation d'un module de la collection :
```bash
ansible-doc community.general.ini_file
```

**Résultat attendu :** La collection est installée et les modules sont accessibles.

---

### Exercice 2 – Utiliser des modules de collections

**But :** Écrire un playbook utilisant des modules issus de collections.

**Instructions :**

1. Examiner le playbook fourni :
```bash
cat playbooks/collections_demo.yml
```

2. Installer les dépendances :
```bash
ansible-galaxy collection install -r requirements.yml
```

3. Exécuter le playbook :
```bash
ansible-playbook -i inventory/mononode.yml playbooks/collections_demo.yml
```

**Résultat attendu :** Le playbook utilise des modules avec FQCN et s'exécute correctement.

---

### Exercice 3 – Gérer les dépendances avec requirements.yml

**But :** Utiliser un fichier de dépendances pour installer les collections nécessaires.

**Instructions :**

1. Examiner le fichier `requirements.yml` :
```bash
cat requirements.yml
```

2. Installer toutes les dépendances :
```bash
ansible-galaxy collection install -r requirements.yml -p ./collections/
```

3. Vérifier que les collections sont installées localement :
```bash
ls collections/ansible_collections/
```

4. Configurer `ansible.cfg` pour utiliser le répertoire local :
```ini
[defaults]
collections_path = ./collections:~/.ansible/collections
```

**Résultat attendu :** Les collections sont installées dans le répertoire local `collections/`.

---

### Exercice 4 – Explorer la structure d'une collection

**But :** Comprendre l'organisation interne d'une collection.

**Instructions :**

1. Explorer la structure de `community.general` :
```bash
tree ~/.ansible/collections/ansible_collections/community/general/ -L 2
```

2. Observer les différents types de plugins :
```bash
ls ~/.ansible/collections/ansible_collections/community/general/plugins/modules/ | head -20
```

3. Lire le fichier `MANIFEST.json` :
```bash
cat ~/.ansible/collections/ansible_collections/community/general/MANIFEST.json | python3 -m json.tool | head -20
```

**Résultat attendu :** Vous comprenez l'organisation en `plugins/`, `roles/`, `docs/`, etc.

## ✅ Validation

```bash
# Vérifier les collections installées
ansible-galaxy collection list

# Exécuter le playbook de démonstration
ansible-playbook -i inventory/mononode.yml playbooks/collections_demo.yml

# Vérifier qu'un module de collection est accessible
ansible-doc community.general.ini_file --short
```

## 🔍 Pour aller plus loin

- [Documentation Ansible sur les collections](https://docs.ansible.com/ansible/latest/collections_guide/index.html)
- [Ansible Galaxy – Collections](https://galaxy.ansible.com/)
- [Créer sa propre collection](https://docs.ansible.com/ansible/latest/dev_guide/developing_collections.html)
- **Défi 1** : Créez votre propre collection contenant un module personnalisé (Lab 15) et un rôle (Lab 09), puis installez-la localement.
- **Défi 2** : Utilisez la collection `community.docker` pour déployer un conteneur avec un playbook Ansible.

## 💡 Solutions

<details>
<summary>Solution – Exercice 1 : Lister et installer</summary>

```bash
# Lister les collections
ansible-galaxy collection list

# Installer
ansible-galaxy collection install community.general
# Starting galaxy collection install process
# Process install dependency map
# Installing 'community.general:X.X.X' to '/home/user/.ansible/collections/...'

# Vérifier
ansible-galaxy collection list | grep community.general
# community.general    X.X.X
```

</details>

<details>
<summary>Solution – Exercice 2 : Utiliser les modules</summary>

```yaml
# playbooks/collections_demo.yml
---
- name: Démonstration des collections Ansible
  hosts: local
  gather_facts: true
  tasks:
    - name: Créer un fichier INI avec community.general
      community.general.ini_file:
        path: /tmp/collections_demo/app.ini
        section: application
        option: nom
        value: "demo-collections"
        mode: '0644'

    - name: Utiliser ansible.builtin.debug (FQCN)
      ansible.builtin.debug:
        msg: "Collections Ansible fonctionnent correctement"
```

</details>

<details>
<summary>Solution – Exercice 3 : Requirements</summary>

```yaml
# requirements.yml
---
collections:
  - name: community.general
    version: ">=7.0.0"
  - name: ansible.posix
```

```bash
ansible-galaxy collection install -r requirements.yml -p ./collections/
ls collections/ansible_collections/
# ansible  community
```

</details>
