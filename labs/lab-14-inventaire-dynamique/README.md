# Lab 14 – Inventaire Dynamique

## 🎯 Objectifs

- Comprendre la différence entre inventaire statique et dynamique
- Utiliser les plugins d'inventaire Ansible (aws_ec2, gcp_compute, docker)
- Créer un script d'inventaire dynamique personnalisé en Python
- Combiner plusieurs sources d'inventaire

## 📋 Prérequis

- Labs 01–13 complétés
- Python 3 disponible
- Notions de base sur les APIs REST (optionnel pour les exercices avancés)

## ⏱️ Durée estimée

75 minutes

## 🏗️ Mise en place

```bash
# Activer l'environnement virtuel
source ~/ansible-venv/bin/activate

# Se placer dans le répertoire du lab
cd labs/lab-14-inventaire-dynamique/

# Rendre le script exécutable
chmod +x inventory/inventaire_dynamique.py
```

## 📚 Concepts expliqués

### Inventaire statique vs dynamique

| Aspect | Inventaire statique | Inventaire dynamique |
|--------|--------------------|--------------------|
| Format | Fichier INI ou YAML | Script Python ou plugin |
| Maintenance | Manuelle | Automatique |
| Sources | Fichiers | AWS, GCP, vSphere, CMDB, LDAP... |
| Mise à jour | À chaque changement | En temps réel |
| Recommandé pour | Petites infrastructures | Infrastructures cloud évolutives |

**Inventaire statique** (`hosts.ini`) :

```ini
[serveurs_web]
web01 ansible_host=192.168.1.10
web02 ansible_host=192.168.1.11

[serveurs_bdd]
db01 ansible_host=192.168.1.20
```

**Inventaire dynamique** : script ou plugin interrogeant une source de données externe.

### Plugins d'inventaire

Ansible fournit des plugins natifs pour les grandes plateformes cloud. Un fichier de configuration YAML suffit :

```yaml
# aws_ec2.yml
plugin: amazon.aws.aws_ec2
regions:
  - eu-west-1
filters:
  instance-state-name: running
  "tag:Environnement": production
keyed_groups:
  - key: tags.Role
    prefix: role
```

Les plugins disponibles incluent :
- `amazon.aws.aws_ec2` – Amazon Web Services EC2
- `google.cloud.gcp_compute` – Google Cloud Platform
- `azure.azcollection.azure_rm` – Microsoft Azure
- `community.vmware.vmware_vm_inventory` – VMware vSphere
- `community.docker.docker_containers` – Docker

### Script d'inventaire personnalisé

Un script d'inventaire dynamique doit :
1. Accepter l'argument `--list` et retourner tous les hôtes en JSON
2. Accepter l'argument `--host <nom>` et retourner les variables d'un hôte

**Format JSON attendu pour `--list` :**

```json
{
  "groupe1": {
    "hosts": ["hote1", "hote2"],
    "vars": { "variable_groupe": "valeur" }
  },
  "_meta": {
    "hostvars": {
      "hote1": { "ansible_host": "192.168.1.10" },
      "hote2": { "ansible_host": "192.168.1.11" }
    }
  }
}
```

### Combinaison d'inventaires

Plusieurs sources d'inventaire peuvent être combinées :

```bash
# Combiner un inventaire statique et un script dynamique
ansible-playbook -i inventory/hosts.ini -i inventory/inventaire_dynamique.py site.yml

# Utiliser un répertoire contenant plusieurs fichiers d'inventaire
ansible-playbook -i inventory/ site.yml
```

Ansible fusionne automatiquement tous les inventaires, ce qui permet d'avoir des hôtes locaux statiques et des hôtes cloud dynamiques dans le même playbook.

### Groupes imbriqués

Les inventaires dynamiques peuvent définir des groupes d'enfants (`children`) :

```json
{
  "production": {
    "children": ["serveurs_web", "serveurs_bdd"]
  }
}
```

## 🛠️ Exercices

### Exercice 1 – Script d'inventaire Python simple

Exécutez le script d'inventaire inclus et examinez sa sortie :

```bash
# Lister l'inventaire complet
python3 inventory/inventaire_dynamique.py --list

# Obtenir les variables d'un hôte
python3 inventory/inventaire_dynamique.py --host web01.exemple.com
python3 inventory/inventaire_dynamique.py --host db01.exemple.com

# Tester avec ansible-inventory
ansible-inventory -i inventory/inventaire_dynamique.py --list
ansible-inventory -i inventory/inventaire_dynamique.py --graph
```

**Attendu** : Le script retourne du JSON valide avec des groupes (`serveurs_web`, `serveurs_bdd`, etc.) et des variables par hôte.

---

### Exercice 2 – Plugin d'inventaire YAML

Examinez le fichier `inventory/aws_ec2.yml` fourni à titre de référence. Créez un fichier `inventory/inventaire_local.yml` simulant un plugin d'inventaire :

```yaml
# inventory/inventaire_local.yml
plugin: ansible.builtin.yaml
```

Puis créez `inventory/hotes_supplementaires.yml` au format YAML Ansible :

```yaml
---
all:
  children:
    serveurs_surveillance:
      hosts:
        prometheus.exemple.com:
          ansible_host: 192.168.1.40
          role: surveillance
        grafana.exemple.com:
          ansible_host: 192.168.1.41
          role: tableaux_de_bord
```

```bash
ansible-inventory -i inventory/hotes_supplementaires.yml --graph
```

---

### Exercice 3 – Combinaison d'inventaires

Combinez l'inventaire statique local et le script dynamique :

```bash
# Utiliser les deux sources d'inventaire simultanément
ansible-inventory \
  -i inventory/hosts.ini \
  -i inventory/inventaire_dynamique.py \
  --graph

# Lancer un playbook sur tous les hôtes de type 'local'
ansible-playbook \
  -i inventory/hosts.ini \
  -i inventory/inventaire_dynamique.py \
  playbooks/tester_inventaire.yml
```

**Attendu** : Ansible combine les deux inventaires et affiche les hôtes des deux sources.

---

### Exercice 4 – Étendre le script d'inventaire

Modifiez `inventory/inventaire_dynamique.py` pour ajouter un nouveau groupe `serveurs_surveillance` avec deux hôtes (`prometheus.exemple.com` sur `192.168.1.40` et `grafana.exemple.com` sur `192.168.1.41`).

```bash
# Vérifier après modification
python3 inventory/inventaire_dynamique.py --list | python3 -m json.tool
ansible-inventory -i inventory/inventaire_dynamique.py --graph
```

**Attendu** : Le groupe `serveurs_surveillance` apparaît dans le graphe d'inventaire.

## ✅ Validation

```bash
# Vérifier le script d'inventaire
python3 inventory/inventaire_dynamique.py --list
python3 inventory/inventaire_dynamique.py --host web01.exemple.com

# Utiliser avec ansible-inventory
ansible-inventory -i inventory/inventaire_dynamique.py --list
ansible-inventory -i inventory/inventaire_dynamique.py --graph

# Exécuter le playbook de test
ansible-playbook -i inventory/hosts.ini playbooks/tester_inventaire.yml
```

## 🔍 Pour aller plus loin

- [Documentation : plugins d'inventaire Ansible](https://docs.ansible.com/ansible/latest/plugins/inventory.html)
- [Plugin amazon.aws.aws_ec2](https://docs.ansible.com/ansible/latest/collections/amazon/aws/aws_ec2_inventory.html)
- [Guide : développer un plugin d'inventaire](https://docs.ansible.com/ansible/latest/dev_guide/developing_inventory.html)
- **Défi 1** : Créez un plugin d'inventaire qui lit depuis une base de données SQLite. Le fichier SQLite contiendra une table `hotes` avec les colonnes `nom`, `ip`, `groupe`, `utilisateur`.
- **Défi 2** : Créez un inventaire dynamique pour une infrastructure VMware vSphere en utilisant la collection `community.vmware`.

## 💡 Solutions

<details>
<summary>Solution – Exercice 1 : Script d'inventaire minimal</summary>

```python
#!/usr/bin/env python3
import json
import sys

inventaire = {
    "serveurs_web": {"hosts": ["web01", "web02"]},
    "serveurs_bdd": {"hosts": ["db01"]},
    "_meta": {
        "hostvars": {
            "web01": {"ansible_host": "192.168.1.10"},
            "web02": {"ansible_host": "192.168.1.11"},
            "db01":  {"ansible_host": "192.168.1.20"}
        }
    }
}

if "--list" in sys.argv:
    print(json.dumps(inventaire, indent=2))
elif "--host" in sys.argv:
    hote = sys.argv[sys.argv.index("--host") + 1]
    print(json.dumps(inventaire["_meta"]["hostvars"].get(hote, {})))
```

</details>

<details>
<summary>Solution – Exercice 4 : Ajouter le groupe surveillance</summary>

Dans `obtenir_inventaire()`, ajoutez dans le dictionnaire retourné :

```python
"serveurs_surveillance": {
    "hosts": ["prometheus.exemple.com", "grafana.exemple.com"],
    "vars": {
        "surveillance_active": True
    }
},
```

Et dans `_meta.hostvars` :

```python
"prometheus.exemple.com": {
    "ansible_host": "192.168.1.40",
    "ansible_user": "ubuntu",
    "role": "surveillance"
},
"grafana.exemple.com": {
    "ansible_host": "192.168.1.41",
    "ansible_user": "ubuntu",
    "role": "tableaux_de_bord"
},
```

</details>

<details>
<summary>Solution – Défi 1 : Inventaire depuis SQLite</summary>

```python
#!/usr/bin/env python3
"""Inventaire dynamique lisant depuis une base SQLite."""
import json
import sys
import sqlite3

def obtenir_inventaire_sqlite(chemin_db="inventaire.db"):
    conn = sqlite3.connect(chemin_db)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT nom, ip, groupe, utilisateur FROM hotes")
    hotes = cursor.fetchall()
    conn.close()

    groupes = {}
    hostvars = {}

    for hote in hotes:
        # Ajouter au groupe
        if hote["groupe"] not in groupes:
            groupes[hote["groupe"]] = {"hosts": []}
        groupes[hote["groupe"]]["hosts"].append(hote["nom"])

        # Variables de l'hôte
        hostvars[hote["nom"]] = {
            "ansible_host": hote["ip"],
            "ansible_user": hote["utilisateur"]
        }

    groupes["_meta"] = {"hostvars": hostvars}
    return groupes

if "--list" in sys.argv:
    print(json.dumps(obtenir_inventaire_sqlite(), indent=2))
elif "--host" in sys.argv:
    print(json.dumps({}))
```

</details>
