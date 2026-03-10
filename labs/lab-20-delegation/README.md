# Lab 20 – Délégation et actions locales

## 🎯 Objectifs

- Comprendre et utiliser `delegate_to` pour exécuter des tâches sur un hôte différent
- Utiliser `local_action` pour exécuter des tâches sur le contrôleur Ansible
- Maîtriser `run_once` pour exécuter une tâche une seule fois
- Comprendre `delegate_facts` pour collecter les faits d'un hôte délégué
- Différencier `connection: local` et `delegate_to: localhost`

## 📋 Prérequis

- Labs 01–19 complétés
- Compréhension des playbooks et de l'inventaire
- Environnement virtuel Python activé

## ⏱️ Durée estimée

60 minutes

## 🏗️ Mise en place

```bash
# Activer l'environnement virtuel
source ~/ansible-venv/bin/activate

# Se placer dans le répertoire du lab
cd labs/lab-20-delegation/
```

## 📚 Concepts expliqués

### delegate_to

Exécute une tâche sur un hôte **différent** de celui ciblé par le play :

```yaml
- name: Ajouter l'hôte au load balancer
  ansible.builtin.command: lb_add {{ inventory_hostname }}
  delegate_to: loadbalancer.exemple.com

- name: Exécuter localement (sur le contrôleur Ansible)
  ansible.builtin.command: echo "Déploiement sur {{ inventory_hostname }}"
  delegate_to: localhost
```

### local_action

Raccourci pour `delegate_to: localhost` :

```yaml
- name: Envoyer une notification
  local_action:
    module: ansible.builtin.uri
    url: "https://hooks.slack.com/webhook"
    method: POST
    body: '{"text": "Déploiement terminé sur {{ inventory_hostname }}"}'
```

### run_once

Exécute la tâche une seule fois, quel que soit le nombre d'hôtes :

```yaml
- name: Exécuter la migration de base de données
  ansible.builtin.command: /opt/app/migrate.sh
  run_once: true
  delegate_to: db-primary.exemple.com
```

### delegate_facts

Par défaut, les faits collectés lors d'une délégation sont attribués à l'hôte **original**. Avec `delegate_facts: true`, ils sont attribués à l'hôte **délégué** :

```yaml
- name: Collecter les faits du load balancer
  ansible.builtin.setup:
  delegate_to: loadbalancer.exemple.com
  delegate_facts: true
  # Les faits sont maintenant disponibles via hostvars['loadbalancer.exemple.com']
```

### connection: local vs delegate_to: localhost

| Aspect | `connection: local` | `delegate_to: localhost` |
|--------|---------------------|--------------------------|
| Portée | Toutes les tâches du play | Une seule tâche |
| Variables | Utilise les variables de l'hôte local | Utilise les variables de l'hôte cible |
| `inventory_hostname` | `localhost` | L'hôte cible original |

## 🛠️ Exercices

### Exercice 1 – Délégation basique avec delegate_to

**But :** Exécuter des tâches sur le contrôleur Ansible via délégation.

**Instructions :**

1. Examiner le playbook :
```bash
cat playbooks/delegation_demo.yml
```

2. Exécuter le playbook :
```bash
ansible-playbook playbooks/delegation_demo.yml
```

3. Vérifier les fichiers créés localement :
```bash
cat /tmp/delegation_demo/rapport.txt
```

**Résultat attendu :** Le rapport contient les informations de l'hôte cible, mais le fichier est créé localement.

---

### Exercice 2 – run_once pour les tâches uniques

**But :** Exécuter une tâche une seule fois même avec plusieurs hôtes.

**Instructions :**

1. Examiner le playbook :
```bash
cat playbooks/run_once_demo.yml
```

2. Exécuter le playbook :
```bash
ansible-playbook playbooks/run_once_demo.yml
```

3. Observer que certaines tâches ne s'exécutent qu'une fois.

**Résultat attendu :** Les tâches marquées `run_once` ne s'exécutent qu'une seule fois.

---

### Exercice 3 – Scénario de déploiement avec délégation

**But :** Simuler un déploiement avec des actions sur différents hôtes.

**Instructions :**

1. Examiner le playbook de déploiement :
```bash
cat playbooks/deploiement_delegation.yml
```

2. Exécuter le playbook :
```bash
ansible-playbook playbooks/deploiement_delegation.yml
```

3. Vérifier les fichiers créés :
```bash
cat /tmp/delegation_demo/pre_deploy.log
cat /tmp/delegation_demo/deploy.log
cat /tmp/delegation_demo/post_deploy.log
```

**Résultat attendu :** Le workflow de déploiement s'exécute avec des étapes locales et déléguées.

## ✅ Validation

```bash
# Nettoyer
rm -rf /tmp/delegation_demo

# Exécuter la démo de délégation
ansible-playbook playbooks/delegation_demo.yml
cat /tmp/delegation_demo/rapport.txt

# Exécuter le déploiement
ansible-playbook playbooks/deploiement_delegation.yml
ls /tmp/delegation_demo/
```

## 🔍 Pour aller plus loin

- [Documentation Ansible – Délégation](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_delegation.html)
- [run_once](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_delegation.html#run-once)
- **Défi 1** : Créez un playbook qui retire un serveur du load balancer (délégation), déploie une mise à jour, puis le réinsère dans le pool.
- **Défi 2** : Utilisez `delegate_facts` pour collecter les faits d'un hôte distant et les utiliser dans une tâche locale.

## 💡 Solutions

<details>
<summary>Solution – Exercice 1 : Délégation basique</summary>

```yaml
---
- name: Démonstration de la délégation
  hosts: local
  gather_facts: true
  tasks:
    - name: Créer le répertoire de rapport
      ansible.builtin.file:
        path: /tmp/delegation_demo
        state: directory
        mode: '0755'

    - name: Générer un rapport localement (delegate_to localhost)
      ansible.builtin.copy:
        content: |
          Rapport de déploiement
          Hôte cible : {{ inventory_hostname }}
          Date : {{ ansible_date_time.iso8601 }}
          OS : {{ ansible_distribution }}
        dest: /tmp/delegation_demo/rapport.txt
        mode: '0644'
      delegate_to: localhost
```

</details>

<details>
<summary>Solution – Exercice 3 : Déploiement avec délégation</summary>

```yaml
---
- name: Déploiement avec délégation
  hosts: local
  gather_facts: true
  tasks:
    - name: Créer le répertoire de logs
      ansible.builtin.file:
        path: /tmp/delegation_demo
        state: directory
        mode: '0755'

    - name: "[PRÉ-DÉPLOIEMENT] Journaliser le début"
      ansible.builtin.copy:
        content: "Début du déploiement - {{ ansible_date_time.iso8601 }}\n"
        dest: /tmp/delegation_demo/pre_deploy.log
        mode: '0644'
      delegate_to: localhost
      run_once: true

    - name: "[DÉPLOIEMENT] Exécuter la mise à jour"
      ansible.builtin.copy:
        content: "Déploiement sur {{ inventory_hostname }} - OK\n"
        dest: /tmp/delegation_demo/deploy.log
        mode: '0644'

    - name: "[POST-DÉPLOIEMENT] Confirmer le succès"
      ansible.builtin.copy:
        content: "Déploiement terminé avec succès - {{ ansible_date_time.iso8601 }}\n"
        dest: /tmp/delegation_demo/post_deploy.log
        mode: '0644'
      delegate_to: localhost
      run_once: true
```

</details>
