# Lab 29 – Dépannage et débogage

## 🎯 Objectifs

- Maîtriser les niveaux de verbosité (`-v` à `-vvvv`)
- Utiliser le mot-clé `debugger` pour le débogage interactif
- Utiliser les modules `debug` et `assert` pour la validation
- Diagnostiquer les problèmes de connexion SSH
- Identifier et résoudre les erreurs courantes Ansible

## 📋 Prérequis

- Labs 01–28 complétés
- Environnement virtuel Python activé

## ⏱️ Durée estimée

75 minutes

## 🏗️ Mise en place

```bash
# Activer l'environnement virtuel
source ~/ansible-venv/bin/activate

# Se placer dans le répertoire du lab
cd labs/lab-29-depannage-debogage/
```

## 📚 Concepts expliqués

### Niveaux de verbosité

```bash
ansible-playbook site.yml -v      # Résultats des tâches
ansible-playbook site.yml -vv     # + Détails des modules
ansible-playbook site.yml -vvv    # + Détails des connexions SSH
ansible-playbook site.yml -vvvv   # + Tout (scripts, variables, connexions)
```

| Niveau | Information affichée |
|--------|---------------------|
| `-v` | Résultats des tâches, valeurs de retour |
| `-vv` | Paramètres d'entrée des modules |
| `-vvv` | Détails des connexions (SSH), chemins des fichiers |
| `-vvvv` | Scripts exécutés sur les hôtes distants |

### Le mot-clé debugger

```yaml
- name: Tâche avec debugger
  ansible.builtin.command: /bin/false
  debugger: on_failed    # S'active quand la tâche échoue

# Options du debugger :
# always     → Toujours s'arrêter
# never      → Ne jamais s'arrêter
# on_failed  → S'arrêter en cas d'échec
# on_unreachable → S'arrêter si l'hôte est inatteignable
# on_skipped → S'arrêter si la tâche est ignorée
```

Commandes dans le debugger :
```
p task        → Afficher la tâche
p task.args   → Afficher les arguments
p result      → Afficher le résultat
p vars        → Afficher les variables
task.args['_raw_params'] = '/bin/true'  → Modifier la commande
redo          → Relancer la tâche
continue      → Continuer l'exécution
quit          → Arrêter
```

### Module assert

```yaml
- name: Vérifier les prérequis
  ansible.builtin.assert:
    that:
      - ansible_distribution == "Ubuntu"
      - ansible_memtotal_mb >= 2048
      - ansible_processor_vcpus >= 2
    fail_msg: "Le serveur ne respecte pas les prérequis minimum"
    success_msg: "Tous les prérequis sont satisfaits"
```

### Variables d'environnement de débogage

```bash
# Activer le débogage complet
ANSIBLE_DEBUG=1 ansible-playbook site.yml

# Afficher les chemins de recherche
ANSIBLE_CONFIG=./ansible.cfg ansible-playbook site.yml -vvv

# Log dans un fichier
ANSIBLE_LOG_PATH=/tmp/ansible.log ansible-playbook site.yml
```

### Erreurs courantes et solutions

| Erreur | Cause probable | Solution |
|--------|---------------|----------|
| `Unreachable` | SSH échoue | Vérifier la connectivité, les clés SSH |
| `Permission denied` | Mauvais utilisateur/clé | Vérifier `ansible_user`, `ansible_ssh_private_key_file` |
| `Module failure` | Mauvais arguments | Consulter `ansible-doc module_name` |
| `Undefined variable` | Variable manquante | Vérifier `vars`, `defaults`, `group_vars` |
| `Syntax error` | YAML invalide | `ansible-playbook --syntax-check`, `yamllint` |

## 🛠️ Exercices

### Exercice 1 – Niveaux de verbosité

**But :** Explorer les différents niveaux de verbosité.

**Instructions :**

1. Exécuter le playbook de diagnostic à différents niveaux :
```bash
ansible-playbook -i inventory/mononode.yml playbooks/diagnostic.yml -v
ansible-playbook -i inventory/mononode.yml playbooks/diagnostic.yml -vv
ansible-playbook -i inventory/mononode.yml playbooks/diagnostic.yml -vvv
```

2. Comparer les sorties et noter les informations supplémentaires à chaque niveau.

**Résultat attendu :** Chaque niveau révèle plus d'informations de débogage.

---

### Exercice 2 – Trouver et corriger des erreurs

**But :** Diagnostiquer et corriger des playbooks cassés.

**Instructions :**

1. Examiner le playbook avec des erreurs intentionnelles :
```bash
cat playbooks/erreurs_a_corriger.yml
```

2. Exécuter et observer les erreurs :
```bash
ansible-playbook -i inventory/mononode.yml playbooks/erreurs_a_corriger.yml
```

3. Identifier et comprendre chaque erreur.

4. Comparer avec la version corrigée dans les solutions.

**Résultat attendu :** Toutes les erreurs sont identifiées et comprises.

---

### Exercice 3 – Utiliser assert pour la validation

**But :** Valider l'état du système avec des assertions.

**Instructions :**

1. Examiner le playbook de validation :
```bash
cat playbooks/validation_assert.yml
```

2. Exécuter le playbook :
```bash
ansible-playbook -i inventory/mononode.yml playbooks/validation_assert.yml
```

3. Observer les assertions qui passent et celles qui échouent.

**Résultat attendu :** Les assertions valident l'état du système.

---

### Exercice 4 – Journal de débogage

**But :** Configurer la journalisation pour le débogage.

**Instructions :**

1. Exécuter avec un fichier de log :
```bash
ANSIBLE_LOG_PATH=/tmp/ansible_debug.log \
ansible-playbook -i inventory/mononode.yml playbooks/diagnostic.yml -vv
```

2. Consulter le log :
```bash
cat /tmp/ansible_debug.log
```

**Résultat attendu :** Les logs complets sont disponibles dans le fichier.

## ✅ Validation

```bash
# Diagnostic avec verbosité
ansible-playbook -i inventory/mononode.yml playbooks/diagnostic.yml -vv

# Validation avec assert
ansible-playbook -i inventory/mononode.yml playbooks/validation_assert.yml

# Journal de débogage
ANSIBLE_LOG_PATH=/tmp/ansible_debug.log \
ansible-playbook -i inventory/mononode.yml playbooks/diagnostic.yml -v
cat /tmp/ansible_debug.log
```

## 🔍 Pour aller plus loin

- [Documentation Ansible – Débogage](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_debugger.html)
- [Module assert](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/assert_module.html)
- [Dépannage réseau](https://docs.ansible.com/ansible/latest/network/user_guide/network_debug_troubleshooting.html)
- **Défi 1** : Utilisez le `debugger: on_failed` pour corriger interactivement un playbook qui échoue.
- **Défi 2** : Créez un playbook de pré-vol (preflight check) qui vérifie tous les prérequis avant un déploiement.

## 💡 Solutions

<details>
<summary>Solution – Exercice 2 : Erreurs corrigées</summary>

```yaml
# Erreur 1 : Variable non définie
# ❌ msg: "{{ variable_inexistante }}"
# ✅ msg: "{{ variable_existante | default('valeur_defaut') }}"

# Erreur 2 : Indentation YAML incorrecte
# ❌ Les éléments de la liste ne sont pas alignés
# ✅ Utiliser 2 espaces par niveau d'indentation

# Erreur 3 : Module inexistant
# ❌ ansible.builtin.module_inexistant
# ✅ Utiliser ansible-doc -l pour trouver le bon module

# Erreur 4 : Mauvais type d'argument
# ❌ mode: 755 (entier)
# ✅ mode: '0755' (chaîne)
```

</details>

<details>
<summary>Solution – Exercice 3 : Validation assert</summary>

```yaml
- name: Validation de l'environnement
  hosts: local
  gather_facts: true
  tasks:
    - name: Vérifier l'OS
      ansible.builtin.assert:
        that:
          - ansible_os_family in ['Debian', 'RedHat', 'Darwin']
        success_msg: "OS supporté : {{ ansible_os_family }}"

    - name: Vérifier la RAM
      ansible.builtin.assert:
        that:
          - ansible_memtotal_mb >= 512
        success_msg: "RAM suffisante : {{ ansible_memtotal_mb }} Mo"
```

</details>
