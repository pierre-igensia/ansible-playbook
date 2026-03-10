# Lab 24 – Plugins de callback et logs

## 🎯 Objectifs

- Comprendre le système de plugins de callback d'Ansible
- Activer et configurer les plugins intégrés (timer, profile_tasks, json)
- Créer un plugin de callback personnalisé en Python
- Mettre en place une journalisation centralisée avec ARA
- Configurer la sortie YAML et JSON pour l'exploitation des logs

## 📋 Prérequis

- Labs 01–23 complétés
- Notions de base en Python
- Environnement virtuel Python activé

## ⏱️ Durée estimée

75 minutes

## 🏗️ Mise en place

```bash
# Activer l'environnement virtuel
source ~/ansible-venv/bin/activate

# Installer ARA (optionnel)
uv pip install ara[server]

# Se placer dans le répertoire du lab
cd labs/lab-24-callback-logs/
```

## 📚 Concepts expliqués

### Qu'est-ce qu'un plugin de callback ?

Les plugins de callback sont déclenchés à différents moments de l'exécution Ansible :
- **Début/fin** d'un playbook, d'un play, d'une tâche
- **Résultat** d'une tâche (ok, changed, failed, skipped, unreachable)
- **Statistiques** de fin d'exécution

### Types de callbacks

| Type | Description | Exemple |
|------|-------------|---------|
| `stdout` | Contrôle la sortie standard | `yaml`, `json`, `dense` |
| `notification` | Envoie des alertes | `slack`, `mail` |
| `aggregate` | Collecte des données | `timer`, `profile_tasks` |

### Plugins intégrés populaires

```ini
# ansible.cfg
[defaults]
# Sortie YAML (plus lisible)
stdout_callback = yaml

# Activer des plugins supplémentaires
callbacks_enabled = ansible.posix.timer, ansible.posix.profile_tasks, ansible.posix.profile_roles
```

| Plugin | Description |
|--------|-------------|
| `ansible.posix.timer` | Affiche le temps total d'exécution |
| `ansible.posix.profile_tasks` | Temps de chaque tâche |
| `ansible.posix.profile_roles` | Temps de chaque rôle |
| `ansible.builtin.json` | Sortie JSON complète |
| `ansible.builtin.yaml` | Sortie YAML lisible |
| `community.general.log_plays` | Journalise dans un fichier |

### Structure d'un plugin de callback

```python
from ansible.plugins.callback import CallbackBase

class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'mon_callback'

    def v2_runner_on_ok(self, result):
        """Appelé quand une tâche réussit"""
        host = result._host
        task = result._task
        self._display.display(f"✅ {host}: {task.name}")

    def v2_runner_on_failed(self, result, ignore_errors=False):
        """Appelé quand une tâche échoue"""
        host = result._host
        self._display.display(f"❌ {host}: {result._task.name}")
```

### ARA (Ansible Run Analysis)

ARA enregistre automatiquement chaque exécution Ansible dans une base de données consultable via une interface web.

```bash
# Installer
uv pip install ara[server]

# Configurer (ajouter dans ansible.cfg)
# [defaults]
# callback_plugins = $(python3 -m ara.setup.callback_plugins)
```

## 🛠️ Exercices

### Exercice 1 – Activer les plugins de profiling

**But :** Mesurer les performances d'exécution avec les plugins intégrés.

**Instructions :**

1. Examiner le playbook de démonstration :
```bash
cat playbooks/callback_demo.yml
```

2. Exécuter avec le plugin timer :
```bash
ANSIBLE_CALLBACKS_ENABLED=ansible.posix.timer \
ansible-playbook -i inventory/mononode.yml playbooks/callback_demo.yml
```

3. Exécuter avec profile_tasks :
```bash
ANSIBLE_CALLBACKS_ENABLED=ansible.posix.profile_tasks \
ansible-playbook -i inventory/mononode.yml playbooks/callback_demo.yml
```

4. Combiner les plugins :
```bash
ANSIBLE_CALLBACKS_ENABLED=ansible.posix.timer,ansible.posix.profile_tasks \
ansible-playbook -i inventory/mononode.yml playbooks/callback_demo.yml
```

**Résultat attendu :** Chaque tâche affiche son temps d'exécution et le total est affiché à la fin.

---

### Exercice 2 – Sortie JSON et YAML

**But :** Changer le format de sortie d'Ansible.

**Instructions :**

1. Exécuter avec la sortie YAML :
```bash
ANSIBLE_STDOUT_CALLBACK=yaml \
ansible-playbook -i inventory/mononode.yml playbooks/callback_demo.yml
```

2. Exécuter avec la sortie JSON :
```bash
ANSIBLE_STDOUT_CALLBACK=json \
ansible-playbook -i inventory/mononode.yml playbooks/callback_demo.yml > /tmp/sortie_ansible.json
```

3. Analyser la sortie JSON :
```bash
python3 -m json.tool /tmp/sortie_ansible.json | head -30
```

**Résultat attendu :** La sortie est formatée en YAML ou JSON selon le plugin choisi.

---

### Exercice 3 – Créer un plugin de callback personnalisé

**But :** Écrire un plugin de callback qui journalise dans un fichier.

**Instructions :**

1. Examiner le plugin personnalisé :
```bash
cat callback_plugins/journal_formation.py
```

2. Exécuter le playbook avec le plugin :
```bash
ANSIBLE_CALLBACK_PLUGINS=./callback_plugins \
ANSIBLE_CALLBACKS_ENABLED=journal_formation \
ansible-playbook -i inventory/mononode.yml playbooks/callback_demo.yml
```

3. Vérifier le journal :
```bash
cat /tmp/ansible_journal.log
```

**Résultat attendu :** Un fichier de log contient les événements de chaque tâche.

---

### Exercice 4 – Journalisation avec log_plays

**But :** Configurer la journalisation automatique dans un fichier.

**Instructions :**

1. Configurer le répertoire de logs :
```bash
mkdir -p /tmp/ansible_logs
```

2. Exécuter avec log_plays :
```bash
ANSIBLE_CALLBACKS_ENABLED=community.general.log_plays \
ANSIBLE_LOG_FOLDER=/tmp/ansible_logs \
ansible-playbook -i inventory/mononode.yml playbooks/callback_demo.yml
```

3. Vérifier les logs :
```bash
ls /tmp/ansible_logs/
cat /tmp/ansible_logs/localhost
```

**Résultat attendu :** Les exécutions sont journalisées dans des fichiers par hôte.

## ✅ Validation

```bash
# Tester le profiling
ANSIBLE_CALLBACKS_ENABLED=ansible.posix.profile_tasks \
ansible-playbook -i inventory/mononode.yml playbooks/callback_demo.yml

# Tester le plugin personnalisé
ANSIBLE_CALLBACK_PLUGINS=./callback_plugins \
ANSIBLE_CALLBACKS_ENABLED=journal_formation \
ansible-playbook -i inventory/mononode.yml playbooks/callback_demo.yml
cat /tmp/ansible_journal.log
```

## 🔍 Pour aller plus loin

- [Documentation Ansible – Callback plugins](https://docs.ansible.com/ansible/latest/plugins/callback.html)
- [ARA Records Ansible](https://ara.readthedocs.io/)
- [Développer des plugins](https://docs.ansible.com/ansible/latest/dev_guide/developing_plugins.html#callback-plugins)
- **Défi 1** : Créez un plugin de callback qui envoie un résumé des exécutions vers un webhook (Slack, Discord, etc.).
- **Défi 2** : Installez ARA et analysez les résultats de plusieurs exécutions via son interface web.

## 💡 Solutions

<details>
<summary>Solution – Exercice 1 : Profiling</summary>

```bash
# Timer uniquement
ANSIBLE_CALLBACKS_ENABLED=ansible.posix.timer \
ansible-playbook -i inventory/mononode.yml playbooks/callback_demo.yml
# Playbook run took 0 days, 0 hours, 0 minutes, 5 seconds

# Profile tasks
ANSIBLE_CALLBACKS_ENABLED=ansible.posix.profile_tasks \
ansible-playbook -i inventory/mononode.yml playbooks/callback_demo.yml
# Simuler un traitement lent -------- 2.05s
# Collecter des informations -------- 0.45s
# Créer un fichier de test ---------- 0.12s
```

</details>

<details>
<summary>Solution – Exercice 3 : Plugin personnalisé</summary>

Le plugin `callback_plugins/journal_formation.py` journalise :
- Le début de chaque play
- Le résultat de chaque tâche (ok, changed, failed)
- Le résumé final

```bash
cat /tmp/ansible_journal.log
# [2024-01-15 14:30:00] PLAY START: Démonstration des callbacks
# [2024-01-15 14:30:01] OK: localhost - Collecter des informations
# [2024-01-15 14:30:03] CHANGED: localhost - Créer un fichier de test
# [2024-01-15 14:30:05] OK: localhost - Simuler un traitement
# [2024-01-15 14:30:05] STATS: localhost - ok=3 changed=1 failures=0
```

</details>
