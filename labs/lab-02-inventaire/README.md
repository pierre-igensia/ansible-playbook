# Lab 02 – Inventaire Ansible

## 🎯 Objectifs
- Comprendre les deux formats d'inventaire : INI et YAML
- Créer des groupes d'hôtes et des groupes enfants
- Utiliser les répertoires `host_vars` et `group_vars`
- Lister et inspecter les hôtes d'un inventaire

## 📋 Prérequis
- Lab 01 complété
- Ansible installé et fonctionnel
- Environnement virtuel activé

## ⏱️ Durée estimée
45 minutes

## 🏗️ Mise en place
1. Se placer dans le répertoire `labs/lab-02-inventaire/`
2. Activer l'environnement virtuel : `source .venv/bin/activate`
3. Explorer les fichiers d'inventaire fournis dans `inventory/`

## 📚 Concepts expliqués

### Qu'est-ce qu'un inventaire ?
L'inventaire Ansible est la liste des machines (hôtes) sur lesquelles Ansible va agir. Il peut être un simple fichier statique ou un inventaire dynamique généré par un script ou un plugin.

### Format INI
Le format INI est le format classique d'Ansible. Il utilise des sections entre crochets pour définir des groupes :

```ini
[webservers]
web01 ansible_host=192.168.1.10
web02 ansible_host=192.168.1.11

[databases]
db01 ansible_host=192.168.1.20
```

### Format YAML
Le format YAML est plus expressif et recommandé pour les inventaires complexes :

```yaml
all:
  children:
    webservers:
      hosts:
        web01:
          ansible_host: 192.168.1.10
```

### Groupes et groupes enfants
Les groupes permettent d'appliquer des tâches à plusieurs hôtes simultanément. Les groupes peuvent contenir d'autres groupes grâce à la directive `children` :

```ini
[production:children]
webservers
databases
```

### host_vars et group_vars
Les répertoires `host_vars/` et `group_vars/` permettent de définir des variables spécifiques à un hôte ou à un groupe, sans alourdir le fichier d'inventaire principal :

```
inventory/
├── mononode.yml
├── host_vars/
│   └── web01.yml      # Variables spécifiques à web01
└── group_vars/
    ├── all.yml        # Variables pour tous les hôtes
    └── webservers.yml # Variables pour le groupe webservers
```

### Variables de connexion courantes
| Variable | Description |
|---|---|
| `ansible_host` | Adresse IP ou nom DNS de l'hôte |
| `ansible_user` | Utilisateur SSH |
| `ansible_port` | Port SSH (défaut : 22) |
| `ansible_connection` | Type de connexion (`ssh`, `local`, `winrm`) |
| `ansible_ssh_private_key_file` | Chemin vers la clé privée SSH |
| `ansible_python_interpreter` | Chemin vers Python sur l'hôte cible |

## 🛠️ Exercices

### Exercice 1 – Explorer l'inventaire INI
**But :** Comprendre la structure d'un inventaire INI et lister ses hôtes.
**Instructions :**
1. Ouvrir le fichier `inventory/mononode.yml`
2. Lister tous les hôtes : `ansible all --list-hosts`
3. Lister uniquement les serveurs web : `ansible webservers --list-hosts`
4. Lister le groupe `production` : `ansible production --list-hosts`

**Questions :**
- Combien d'hôtes appartiennent au groupe `production` ?
- Quel hôte a pour IP `192.168.1.20` ?

**Résultat attendu :**
```
  hosts (4):
    web01
    web02
    db01
    lb01
```

### Exercice 2 – Convertir en YAML
**But :** Comparer les formats INI et YAML.
**Instructions :**
1. Ouvrir `inventory/hosts.yml`
2. Comparer la structure avec `inventory/mononode.yml`
3. Lister les hôtes depuis l'inventaire YAML : `ansible all --list-hosts -i inventory/hosts.yml`
4. Vérifier que le résultat est identique à celui de l'inventaire INI

**Questions :**
- Quelle différence de syntaxe notez-vous entre les deux formats ?
- Lequel vous semble plus lisible pour un grand nombre d'hôtes ?

### Exercice 3 – Variables d'hôtes et de groupes
**But :** Utiliser `host_vars` et `group_vars` pour organiser les variables.
**Instructions :**
1. Ouvrir `inventory/host_vars/web01.yml` et `inventory/group_vars/webservers.yml`
2. Inspecter les variables effectives d'un hôte :
   ```bash
   ansible-inventory -i inventory/hosts.yml --host web01
   ```
3. Observer quelle valeur de `http_port` est utilisée pour `web01` (host_vars ou group_vars ?)

**Question :** Quelle est la priorité entre `host_vars` et `group_vars` ?

**Résultat attendu :** Les variables `host_vars` ont **priorité** sur les `group_vars`.

### Exercice 4 – Créer votre propre inventaire
**But :** Créer un inventaire YAML de zéro.
**Instructions :**
1. Créer un nouveau fichier `inventory/mon_inventaire.yml`
2. Y définir :
   - Un groupe `frontend` avec deux hôtes fictifs (`front01`, `front02`)
   - Un groupe `backend` avec un hôte fictif (`back01`)
   - Un groupe `app` contenant `frontend` et `backend` comme enfants
   - La variable `env: production` pour tous les hôtes
3. Vérifier avec : `ansible all --list-hosts -i inventory/mon_inventaire.yml`

## ✅ Validation
```bash
# Lister tous les hôtes de l'inventaire INI
ansible all --list-hosts

# Lister les hôtes du groupe webservers
ansible webservers --list-hosts

# Lister les hôtes depuis l'inventaire YAML
ansible all --list-hosts -i inventory/hosts.yml

# Vérifier les variables d'un hôte spécifique
ansible-inventory -i inventory/hosts.yml --host web01
```

## 🔍 Pour aller plus loin
- [Documentation sur les inventaires](https://docs.ansible.com/ansible/latest/inventory_guide/intro_inventory.html)
- [group_vars et host_vars](https://docs.ansible.com/ansible/latest/inventory_guide/intro_inventory.html#organizing-host-and-group-variables)
- [Inventaires dynamiques](https://docs.ansible.com/ansible/latest/inventory_guide/intro_dynamic_inventory.html)
- **Défi 1** : Utiliser la commande `ansible-inventory --graph -i inventory/hosts.yml` pour afficher l'arborescence des groupes
- **Défi 2** : Créer un inventaire dynamique avec un script Python simple qui retourne des hôtes au format JSON

## 💡 Solutions
<details>
<summary>Solution</summary>

### Solution Exercice 1
```bash
# Lister tous les hôtes
ansible all --list-hosts

# Lister les webservers seulement
ansible webservers --list-hosts

# Lister le groupe production (contient tous les sous-groupes)
ansible production --list-hosts
# Réponse : 4 hôtes (web01, web02, db01, lb01)
# L'hôte 192.168.1.20 est db01
```

### Solution Exercice 2
```bash
# Les deux commandes donnent le même résultat
ansible all --list-hosts
ansible all --list-hosts -i inventory/hosts.yml

# Différences : YAML est plus verbeux mais plus structuré ;
# INI est plus compact mais moins flexible pour les structures complexes.
```

### Solution Exercice 3
```bash
# Inspecter les variables effectives de web01
ansible-inventory -i inventory/hosts.yml --host web01

# Les host_vars ont PRIORITÉ sur les group_vars.
# web01 utilise http_port=80 défini dans host_vars/web01.yml.
```

### Solution Exercice 4
```yaml
---
# inventory/mon_inventaire.yml
all:
  vars:
    env: production
  children:
    frontend:
      hosts:
        front01:
          ansible_host: 10.0.0.1
        front02:
          ansible_host: 10.0.0.2
    backend:
      hosts:
        back01:
          ansible_host: 10.0.0.10
    app:
      children:
        frontend:
        backend:
```
</details>
