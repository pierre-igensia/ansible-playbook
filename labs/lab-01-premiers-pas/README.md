# Lab 01 – Premiers pas avec Ansible

## 🎯 Objectifs
- Vérifier l'installation d'Ansible
- Comprendre la commande `ansible --version`
- Exécuter un premier ping sur localhost

## 📋 Prérequis
- Python 3.11+ installé
- Ansible installé (voir les instructions d'installation dans le README principal du dépôt)
- Connaissances de base en ligne de commande Linux

## ⏱️ Durée estimée
30 minutes

## 🏗️ Mise en place
1. Suivre les instructions d'installation du README principal du dépôt
2. Activer l'environnement virtuel
3. Se placer dans le répertoire `labs/lab-01-premiers-pas/`

## 📚 Concepts expliqués

### Qu'est-ce qu'Ansible ?
Ansible est un outil d'automatisation IT open-source qui permet de configurer des systèmes, déployer des applications et orchestrer des tâches. Il est **agentless** : pas besoin d'installer un agent sur les machines cibles.

### Architecture
- **Nœud de contrôle** : la machine depuis laquelle Ansible est exécuté
- **Nœuds gérés** : les machines cibles (serveurs, équipements réseau...)
- **Inventaire** : liste des nœuds gérés
- **Playbook** : fichier YAML décrivant les tâches à exécuter

### Le module ping
Le module `ping` d'Ansible vérifie la connectivité et la disponibilité Python sur les hôtes cibles. Ce n'est **pas** un ping ICMP.

```bash
ansible all -m ping
```

## 🛠️ Exercices

### Exercice 1 – Vérifier l'installation
**But :** Confirmer qu'Ansible est correctement installé.
**Instructions :**
1. Activer l'environnement virtuel : `source .venv/bin/activate`
2. Exécuter : `ansible --version`
3. Noter la version d'Ansible, le chemin de configuration, et la version de Python

**Résultat attendu :**
```
ansible [core 2.16.x]
  config file = /chemin/vers/ansible.cfg
  ...
  python version = 3.11.x
```

### Exercice 2 – Premier ping sur localhost
**But :** Exécuter une commande Ansible sur localhost.
**Instructions :**
1. Utiliser l'inventaire `inventory/mononode.yml`
2. Exécuter : `ansible localhost -m ping`
3. Observer la sortie JSON

**Résultat attendu :**
```json
localhost | SUCCESS => {
    "changed": false,
    "ping": "pong"
}
```

### Exercice 3 – Informations système
**But :** Récupérer des informations sur le système local.
**Instructions :**
1. Exécuter : `ansible localhost -m setup | head -50`
2. Identifier votre système d'exploitation et sa version
3. Trouver l'adresse IP de votre machine

**Résultat attendu :** Un dictionnaire JSON avec toutes les informations système (facts).

## ✅ Validation
```bash
# Vérifier la version d'Ansible (doit être >= 2.15)
ansible --version | head -1

# Vérifier le ping sur localhost
ansible localhost -m ping

# Lister les faits système
ansible localhost -m setup -a "filter=ansible_os_family"
```

## 🔍 Pour aller plus loin
- [Documentation officielle Ansible](https://docs.ansible.com/ansible/latest/index.html)
- [Module ping](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/ping_module.html)
- **Défi 1** : Trouver combien de modules sont disponibles dans votre installation avec `ansible-doc -l | wc -l`
- **Défi 2** : Explorer la documentation d'un module avec `ansible-doc copy`

## 💡 Solutions
<details>
<summary>Solution</summary>

### Solution Exercice 1
```bash
# Activer l'environnement virtuel
source .venv/bin/activate

# Vérifier la version
ansible --version
```

### Solution Exercice 2
```bash
# Créer le fichier d'inventaire si nécessaire
cat inventory/mononode.yml

# Exécuter le ping
ansible localhost -m ping
```

### Solution Exercice 3
```bash
# Obtenir les facts filtrés
ansible localhost -m setup -a "filter=ansible_distribution*"
```
</details>
