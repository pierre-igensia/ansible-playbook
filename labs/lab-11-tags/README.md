# Lab 11 – Tags Ansible

## 🎯 Objectifs
- Comprendre l'utilité des tags dans les playbooks Ansible
- Appliquer des tags aux tâches, rôles et plays
- Utiliser `--tags` et `--skip-tags` pour contrôler l'exécution
- Mettre en place une stratégie de tags cohérente

## 📋 Prérequis
- Labs 01–10 complétés
- Maîtrise des playbooks et rôles

## ⏱️ Durée estimée
45 minutes

## 🏗️ Mise en place
1. Activer l'environnement virtuel : `source .venv/bin/activate`
2. Se placer dans `labs/lab-11-tags/`

## 📚 Concepts expliqués

### Pourquoi utiliser les tags ?
Les tags permettent d'exécuter sélectivement des parties d'un playbook sans modifier le code. Cas d'usage typiques :
- Exécuter uniquement les tâches de déploiement (sans la configuration initiale)
- Sauter les tâches de redémarrage de service en production
- Tester uniquement certains composants

### Syntaxe des tags
```yaml
# Tag sur une tâche
- name: Installer nginx
  ansible.builtin.package:
    name: nginx
  tags:
    - installation
    - web

# Tags spéciaux
# always  : tâche toujours exécutée (même avec --tags autre_tag)
# never   : tâche jamais exécutée (sauf avec --tags never)
# tagged  : toutes les tâches ayant au moins un tag
# untagged: toutes les tâches sans tag
# all     : toutes les tâches (comportement par défaut)
```

### Commandes avec tags
```bash
# Exécuter uniquement les tâches tagguées 'installation'
ansible-playbook site.yml --tags installation

# Exécuter plusieurs tags
ansible-playbook site.yml --tags "installation,configuration"

# Exclure des tags
ansible-playbook site.yml --skip-tags redémarrage

# Lister les tags disponibles
ansible-playbook site.yml --list-tags

# Lister les tâches qui seraient exécutées
ansible-playbook site.yml --tags installation --list-tasks
```

### Stratégie de tags recommandée
| Tag | Utilisation |
|-----|-------------|
| `installation` | Installation de paquets |
| `configuration` | Modification de fichiers de config |
| `service` | Démarrage/arrêt de services |
| `sécurité` | Tâches liées à la sécurité |
| `déploiement` | Déploiement d'application |
| `tests` | Tâches de validation |
| `jamais` | Tâches destructives (remplace `never`) |

## 🛠️ Exercices

### Exercice 1 – Taguer un playbook existant
**But :** Ajouter des tags à un playbook de configuration.
**Instructions :**
1. Ouvrir `playbooks/serveur_complet.yml`
2. Ajouter les tags appropriés à chaque tâche
3. Lister tous les tags disponibles

**Résultat attendu :** `ansible-playbook --list-tags` affiche tous les tags définis.

### Exercice 2 – Exécution sélective
**But :** Exécuter seulement certaines parties du playbook.
**Instructions :**
1. Exécuter uniquement les tâches d'installation
2. Exécuter uniquement la configuration
3. Ignorer les tâches de démarrage

**Résultat attendu :** Chaque commande n'exécute que les tâches correspondant aux tags.

### Exercice 3 – Tags spéciaux
**But :** Utiliser les tags `always` et `never`.
**Instructions :**
1. Marquer la tâche de vérification avec le tag `always`
2. Marquer une tâche destructive avec le tag `never`
3. Tester le comportement avec différentes combinaisons de `--tags`

### Exercice 4 – Tags sur les rôles
**But :** Appliquer des tags à un rôle entier.
**Instructions :**
1. Modifier `playbooks/site_avec_roles.yml` pour ajouter des tags aux rôles
2. Observer comment les tags se propagent aux tâches du rôle

## ✅ Validation
```bash
# Lister tous les tags
ansible-playbook -i inventory/hosts.ini playbooks/serveur_complet.yml --list-tags

# Exécuter uniquement installation
ansible-playbook -i inventory/hosts.ini playbooks/serveur_complet.yml --tags installation

# Exécuter avec skip
ansible-playbook -i inventory/hosts.ini playbooks/serveur_complet.yml --skip-tags service
```

## 🔍 Pour aller plus loin
- [Documentation Ansible sur les tags](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_tags.html)
- **Défi 1** : Créer un playbook de déploiement avec les tags `préparer`, `déployer`, `tester`, `nettoyer`
- **Défi 2** : Utiliser les tags dans un pipeline CI pour n'exécuter que les tâches de test

## 💡 Solutions
<details>
<summary>Solution</summary>

### Solution Exercice 1
```bash
ansible-playbook -i inventory/hosts.ini playbooks/serveur_complet.yml --list-tags
```

### Solution Exercice 2
```bash
# Installation uniquement
ansible-playbook -i inventory/hosts.ini playbooks/serveur_complet.yml --tags installation

# Configuration uniquement
ansible-playbook -i inventory/hosts.ini playbooks/serveur_complet.yml --tags configuration

# Sans les redémarrages
ansible-playbook -i inventory/hosts.ini playbooks/serveur_complet.yml --skip-tags service
```

### Solution Exercice 3
```yaml
- name: Vérification toujours exécutée
  ansible.builtin.debug:
    msg: "Vérification du système..."
  tags: always

- name: Tâche dangereuse - jamais exécutée par défaut
  ansible.builtin.debug:
    msg: "ATTENTION: Suppression des données..."
  tags: never
```
</details>
