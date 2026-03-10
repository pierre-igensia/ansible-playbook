# Lab 04 – Premier Playbook

## 🎯 Objectifs
- Écrire un playbook Ansible complet avec plusieurs tâches
- Comprendre la structure d'un play (hosts, become, vars, tasks)
- Utiliser des variables dans un playbook
- Capturer et afficher la sortie des tâches avec `register` et `debug`
- Explorer les facts Ansible avec `gather_facts`

## 📋 Prérequis
- Labs 01, 02 et 03 complétés
- Ansible installé et fonctionnel
- Environnement virtuel activé
- Notions de base YAML

## ⏱️ Durée estimée
60 minutes

## 🏗️ Mise en place
1. Se placer dans le répertoire `labs/lab-04-premier-playbook/`
2. Activer l'environnement virtuel : `source .venv/bin/activate`
3. Vérifier l'inventaire : `cat inventory/mononode.yml`

## 📚 Concepts expliqués

### Structure d'un playbook
Un playbook est un fichier YAML contenant un ou plusieurs **plays**. Chaque play cible un groupe d'hôtes et définit une liste de tâches à exécuter dans l'ordre :

```yaml
---
- name: Nom descriptif du play
  hosts: groupe_ou_hote
  become: false        # Élévation de privilèges (sudo)
  gather_facts: true   # Collecter les facts système
  vars:                # Variables locales au play
    ma_variable: valeur

  tasks:
    - name: Description de la tâche
      module.name:
        parametre: valeur
```

### Directive `become`
`become: true` permet d'exécuter les tâches avec des privilèges élevés (équivalent sudo). On peut préciser l'utilisateur cible avec `become_user`.

```yaml
- name: Installer un paquet (nécessite sudo)
  ansible.builtin.apt:
    name: nginx
    state: present
  become: true
```

### Variables dans un playbook
Les variables peuvent être définies à plusieurs niveaux :

```yaml
vars:
  app_name: "mon-app"
  app_version: "1.0.0"
  app_dir: "/opt/{{ app_name }}"  # Référence à une autre variable
```

On y accède avec la syntaxe Jinja2 : `{{ ma_variable }}`

### Le mot-clé `register`
`register` capture la sortie d'une tâche dans une variable pour un usage ultérieur :

```yaml
- name: Vérifier un fichier
  ansible.builtin.stat:
    path: /etc/hosts
  register: hosts_file

- name: Afficher le résultat
  ansible.builtin.debug:
    msg: "Le fichier existe : {{ hosts_file.stat.exists }}"
```

### Le module `debug`
`debug` affiche des informations pendant l'exécution du playbook. Utile pour inspecter des variables :

```yaml
- name: Afficher une variable
  ansible.builtin.debug:
    var: ma_variable          # Affiche la variable brute

- name: Afficher un message
  ansible.builtin.debug:
    msg: "La valeur est : {{ ma_variable }}"  # Message formaté
```

### `gather_facts` et les facts Ansible
Quand `gather_facts: true` (valeur par défaut), Ansible collecte automatiquement des informations sur le système cible avant d'exécuter les tâches. Ces informations sont accessibles via des variables préfixées par `ansible_` :

| Variable | Description |
|---|---|
| `ansible_distribution` | Nom de la distribution (Ubuntu, CentOS...) |
| `ansible_distribution_version` | Version de la distribution |
| `ansible_os_family` | Famille d'OS (Debian, RedHat...) |
| `ansible_default_ipv4.address` | Adresse IP principale |
| `ansible_memtotal_mb` | RAM totale en MB |
| `ansible_processor_vcpus` | Nombre de vCPUs |
| `ansible_hostname` | Nom de la machine |

### Idempotence dans les playbooks
Un playbook bien écrit doit être **idempotent** : l'exécuter plusieurs fois produit toujours le même résultat final. Les modules Ansible sont conçus pour cela.

## 🛠️ Exercices

### Exercice 1 – Exécuter le playbook webserver
**But :** Comprendre la structure d'un playbook en l'exécutant et en analysant sa sortie.
**Instructions :**
1. Examiner le fichier `playbooks/webserver.yml`
2. Exécuter le playbook :
   ```bash
   ansible-playbook playbooks/webserver.yml
   ```
3. Observer la sortie : couleur verte (ok), jaune (changed), rouge (failed)
4. Exécuter le playbook une **deuxième fois** et comparer la sortie

**Questions :**
- Quelles tâches sont marquées `changed` à la première exécution ?
- Que se passe-t-il à la deuxième exécution ? Pourquoi ?
- Où sont créés les fichiers sur votre système ?

**Résultat attendu (première exécution) :**
```
PLAY RECAP
localhost : ok=7  changed=3  unreachable=0  failed=0
```

### Exercice 2 – Modifier les variables
**But :** Personnaliser le playbook en changeant les variables.
**Instructions :**
1. Ouvrir `playbooks/webserver.yml`
2. Changer la variable `app_name` en `"mon-super-projet"`
3. Changer `app_version` en `"2.0.0"`
4. Exécuter le playbook et vérifier que les nouveaux chemins sont créés :
   ```bash
   ansible-playbook playbooks/webserver.yml
   ls /tmp/mon-super-projet/
   ```
5. Passer une variable en ligne de commande avec `--extra-vars` :
   ```bash
   ansible-playbook playbooks/webserver.yml \
     --extra-vars "app_name=test-cli app_version=3.0.0"
   ```

**Question :** Quelle est la priorité entre les variables définies dans `vars:` et celles passées avec `--extra-vars` ?

### Exercice 3 – Explorer les facts avec gather_facts
**But :** Utiliser `gather_facts` pour collecter et afficher des informations système.
**Instructions :**
1. Examiner le fichier `playbooks/gather_facts.yml`
2. Exécuter le playbook :
   ```bash
   ansible-playbook playbooks/gather_facts.yml
   ```
3. Observer les informations système affichées
4. Ajouter une nouvelle tâche qui affiche le nom d'hôte (`ansible_hostname`) et la version du noyau (`ansible_kernel`)

**Résultat attendu :**
```
TASK [Afficher le système d'exploitation] ***
ok: [localhost] => {
    "msg": "OS: Ubuntu 22.04"
}
```

### Exercice 4 – Utiliser register et conditions
**But :** Capturer la sortie d'une tâche et l'utiliser dans une condition.
**Instructions :**
1. Créer un nouveau playbook `playbooks/conditions.yml` avec le contenu suivant :
   ```yaml
   ---
   - name: Utiliser register et conditions
     hosts: local
     gather_facts: false

     tasks:
       - name: Vérifier si le fichier /tmp/ansible_lab_04 existe
         ansible.builtin.stat:
           path: /tmp/ansible_lab_04
         register: fichier_stat

       - name: Créer le fichier s'il n'existe pas
         ansible.builtin.copy:
           content: "Créé par le Lab 04\n"
           dest: /tmp/ansible_lab_04
           mode: '0644'
         when: not fichier_stat.stat.exists

       - name: Afficher l'état du fichier
         ansible.builtin.debug:
           msg: >
             Le fichier /tmp/ansible_lab_04
             {{ 'existait déjà' if fichier_stat.stat.exists else 'a été créé' }}.
   ```
2. Exécuter le playbook deux fois et observer la différence

## ✅ Validation
```bash
# Exécuter le playbook principal
ansible-playbook playbooks/webserver.yml

# Vérifier les fichiers créés
ls -la /tmp/mon-application/

# Exécuter le playbook gather_facts
ansible-playbook playbooks/gather_facts.yml

# Tester avec extra-vars
ansible-playbook playbooks/webserver.yml \
  --extra-vars "app_name=validation app_version=1.0.0"

# Vérifier le résultat
ls /tmp/validation/
cat /tmp/validation/config.ini

# Nettoyer
rm -rf /tmp/mon-application/ /tmp/mon-super-projet/ /tmp/validation/ /tmp/ansible_lab_04
```

## 🔍 Pour aller plus loin
- [Guide des playbooks Ansible](https://docs.ansible.com/ansible/latest/playbook_guide/index.html)
- [Module debug](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/debug_module.html)
- [Variables dans Ansible](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_variables.html)
- [Facts Ansible](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_vars_facts.html)
- **Défi 1** : Ajouter un handler qui affiche un message uniquement quand un fichier a été créé (module `notify` + `handlers`)
- **Défi 2** : Utiliser `ansible-playbook --check` pour simuler l'exécution sans rien modifier
- **Défi 3** : Ajouter un tag `setup` à certaines tâches et utiliser `--tags setup` pour n'exécuter que ces tâches

## 💡 Solutions
<details>
<summary>Solution</summary>

### Solution Exercice 1
```bash
# Première exécution : changed=3 (répertoire + config.ini + index.html créés)
ansible-playbook playbooks/webserver.yml

# Deuxième exécution : changed=0 (tout existe déjà -> idempotent)
ansible-playbook playbooks/webserver.yml

# Les fichiers sont créés dans /tmp/mon-application/
ls /tmp/mon-application/
```

### Solution Exercice 2
```bash
# Modifier les variables directement dans le fichier vars:
# app_name: "mon-super-projet"
# app_version: "2.0.0"

ansible-playbook playbooks/webserver.yml

# Passer les variables en ligne de commande (priorité maximale)
ansible-playbook playbooks/webserver.yml \
  --extra-vars "app_name=test-cli app_version=3.0.0"

# Les --extra-vars ont la PRIORITÉ la plus haute sur toutes les autres variables.
```

### Solution Exercice 3
```bash
# Exécuter le playbook
ansible-playbook playbooks/gather_facts.yml

# Tâche supplémentaire à ajouter dans gather_facts.yml :
#   - name: Afficher le nom d'hôte et le noyau
#     ansible.builtin.debug:
#       msg: "Hôte: {{ ansible_hostname }}, Noyau: {{ ansible_kernel }}"
```

### Solution Exercice 4
```yaml
---
- name: Utiliser register et conditions
  hosts: local
  gather_facts: false

  tasks:
    - name: Vérifier si le fichier /tmp/ansible_lab_04 existe
      ansible.builtin.stat:
        path: /tmp/ansible_lab_04
      register: fichier_stat

    - name: Créer le fichier s'il n'existe pas
      ansible.builtin.copy:
        content: "Créé par le Lab 04\n"
        dest: /tmp/ansible_lab_04
        mode: '0644'
      when: not fichier_stat.stat.exists

    - name: Afficher l'état du fichier
      ansible.builtin.debug:
        msg: >
          Le fichier /tmp/ansible_lab_04
          {{ 'existait déjà' if fichier_stat.stat.exists else 'a été créé' }}.
```
</details>
