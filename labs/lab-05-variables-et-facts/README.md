# Lab 05 – Variables et Faits Ansible

## 🎯 Objectifs

À la fin de ce lab, vous serez capable de :

- Déclarer et utiliser des variables dans un playbook
- Utiliser `vars_files` pour externaliser les variables
- Comprendre et exploiter les facts Ansible
- Maîtriser la priorité des variables
- Créer des variables dynamiques avec `set_fact` et `register`

## 📋 Prérequis

- Labs 01–04 complétés
- Notions de base en YAML
- Ansible installé et fonctionnel

## ⏱️ Durée estimée

60 minutes

## 🏗️ Mise en place

```bash
# Depuis la racine du dépôt
cd labs/lab-05-variables-et-faits

# Vérifier l'inventaire
cat inventory/mononode.yml

# Tester la connectivité
ansible local -m ping
```

## 📚 Concepts expliqués

### Types de variables

Ansible propose plusieurs façons de déclarer des variables, chacune avec sa portée et son contexte d'utilisation.

#### 1. Variables dans le play (`vars`)

Déclarées directement dans le playbook, au niveau du play. Elles sont visibles par toutes les tâches du play :

```yaml
- name: Mon play
  hosts: local
  vars:
    ma_variable: "bonjour"
    mon_nombre: 42
    ma_liste:
      - élément1
      - élément2
    mon_dict:
      clé: valeur
      autre_clé: autre_valeur
```

#### 2. Variables externes (`vars_files`)

Permet d'externaliser les variables dans des fichiers YAML séparés pour une meilleure organisation :

```yaml
- name: Mon play
  hosts: local
  vars_files:
    - vars/app_config.yml
    - vars/secrets.yml
```

#### 3. Variables d'hôte (`host_vars`)

Fichiers placés dans `host_vars/<nom_hôte>.yml`, appliqués à un hôte spécifique :

```
inventory/
  host_vars/
    localhost.yml    # variables uniquement pour localhost
    serveur1.yml     # variables uniquement pour serveur1
```

#### 4. Variables de groupe (`group_vars`)

Fichiers placés dans `group_vars/<nom_groupe>.yml`, appliqués à tous les hôtes d'un groupe :

```
inventory/
  group_vars/
    all.yml          # variables pour tous les hôtes
    webservers.yml   # variables pour le groupe webservers
    databases.yml    # variables pour le groupe databases
```

#### 5. Variables en ligne de commande (`extra_vars`)

Passées avec l'option `-e` ou `--extra-vars`, elles ont la priorité la plus haute :

```bash
ansible-playbook playbook.yml -e "env=production version=2.0"
ansible-playbook playbook.yml -e @fichier_vars.yml
```

#### 6. Variables enregistrées (`register`)

Permettent de capturer la sortie d'une tâche pour la réutiliser :

```yaml
- name: Lister les fichiers
  ansible.builtin.command: ls /tmp
  register: resultat_ls

- name: Afficher le résultat
  ansible.builtin.debug:
    msg: "Fichiers: {{ resultat_ls.stdout_lines }}"
```

#### 7. Facts Ansible (`ansible_facts`)

Informations collectées automatiquement sur les hôtes gérés (voir section dédiée ci-dessous).

---

### Priorité des variables (du plus bas au plus haut)

Quand une variable est définie à plusieurs endroits, Ansible applique un ordre de priorité strict. La valeur la plus haute écrase les valeurs inférieures :

| Priorité | Source |
|----------|--------|
| 1 (la plus basse) | `defaults` de rôle |
| 2 | `group_vars/all` |
| 3 | `group_vars/<groupe>` |
| 4 | `host_vars/<hôte>` |
| 5 | `vars` dans le play |
| 6 | `vars_files` |
| 7 | `register` (variable enregistrée) |
| 8 | `set_fact` |
| 9 (la plus haute) | `extra_vars` (-e) |

> 💡 **Astuce** : En cas de doute, les `extra_vars` (`-e`) gagnent toujours. C'est utile pour les surcharges ponctuelles en CI/CD ou en dépannage.

---

### Facts Ansible

Les facts sont des informations collectées automatiquement par Ansible sur chaque hôte géré lors de la phase de « gathering facts » (activée par défaut avec `gather_facts: true`).

#### Facts couramment utilisés

| Fact | Description | Exemple |
|------|-------------|---------|
| `ansible_hostname` | Nom de la machine | `"webserver01"` |
| `ansible_distribution` | Distribution OS | `"Ubuntu"` |
| `ansible_distribution_version` | Version de l'OS | `"22.04"` |
| `ansible_os_family` | Famille de l'OS | `"Debian"` |
| `ansible_architecture` | Architecture CPU | `"x86_64"` |
| `ansible_memtotal_mb` | RAM totale en MB | `4096` |
| `ansible_processor_vcpus` | Nombre de vCPUs | `4` |
| `ansible_default_ipv4.address` | Adresse IP principale | `"192.168.1.10"` |
| `ansible_kernel` | Version du noyau | `"5.15.0-56-generic"` |
| `ansible_date_time.date` | Date actuelle | `"2024-01-15"` |
| `ansible_mounts` | Points de montage | liste de dictionnaires |
| `ansible_interfaces` | Interfaces réseau | `["lo", "eth0"]` |

#### Explorer tous les facts

```bash
# Afficher tous les facts d'un hôte
ansible localhost -m ansible.builtin.setup

# Filtrer les facts par motif
ansible localhost -m ansible.builtin.setup -a "filter=ansible_memory*"
ansible localhost -m ansible.builtin.setup -a "filter=ansible_distribution*"
```

#### Désactiver la collecte des facts

Si vous n'avez pas besoin des facts (gain de performance) :

```yaml
- name: Play sans facts
  hosts: local
  gather_facts: false
  tasks:
    - name: Simple tâche
      ansible.builtin.debug:
        msg: "Pas de facts collectés"
```

#### Facts personnalisés avec `set_fact`

```yaml
- name: Créer un fact personnalisé
  ansible.builtin.set_fact:
    mon_fact: "calculé à {{ ansible_date_time.time }}"
    est_production: "{{ env == 'production' }}"
```

---

## 🛠️ Exercices

### Exercice 1 – Variables dans un playbook

**Objectif** : Créer un playbook qui utilise des variables pour configurer une application fictive.

Exécutez le playbook de démonstration :

```bash
ansible-playbook playbooks/variables_demo.yml
```

Observez comment les différents types de variables sont utilisés et affichés.

**Questions de réflexion :**
- Quelle est la différence entre `config.port` et `config['port']` dans un template Jinja2 ?
- Comment accéder à un élément d'une liste par son index ?

---

### Exercice 2 – Variables externes (`vars_files`)

**Objectif** : Créer un fichier de variables externe et l'utiliser dans un playbook.

1. Examinez le fichier de variables existant :

```bash
cat vars/app_config.yml
```

2. Créez votre propre fichier de variables `vars/mon_app.yml` :

```yaml
---
mon_app_nom: "super-app"
mon_app_port: 9000
mon_app_auteur: "votre_nom"
fonctionnalites:
  - authentification
  - tableau-de-bord
  - api-rest
```

3. Créez un playbook `playbooks/mon_app.yml` qui utilise ce fichier :

```yaml
---
- name: Mon application
  hosts: local
  gather_facts: false
  vars_files:
    - ../vars/mon_app.yml
  tasks:
    - name: Présenter l'application
      ansible.builtin.debug:
        msg: |
          Application: {{ mon_app_nom }}
          Port: {{ mon_app_port }}
          Auteur: {{ mon_app_auteur }}
          Fonctionnalités: {{ fonctionnalites | join(', ') }}
```

4. Exécutez-le :

```bash
ansible-playbook playbooks/mon_app.yml
```

---

### Exercice 3 – Exploration des facts

**Objectif** : Explorer les facts disponibles et créer un rapport système.

1. Affichez tous les facts disponibles :

```bash
ansible localhost -m ansible.builtin.setup | head -100
```

2. Filtrez les facts de mémoire :

```bash
ansible localhost -m ansible.builtin.setup -a "filter=ansible_mem*"
```

3. Exécutez le playbook d'exploration des facts :

```bash
ansible-playbook playbooks/facts_exploration.yml
```

4. Vérifiez le rapport généré par `variables_demo.yml` :

```bash
cat /tmp/rapport_systeme.txt
```

**Défi** : Modifiez `facts_exploration.yml` pour afficher également la liste des interfaces réseau avec leur adresse IP.

---

### Exercice 4 – Variables personnalisées (`extra_vars`)

**Objectif** : Passer des variables en ligne de commande avec `-e` pour surcharger les valeurs par défaut.

1. Exécutez le playbook avec des valeurs par défaut :

```bash
ansible-playbook playbooks/variables_demo.yml
```

2. Surchargez l'environnement avec `-e` :

```bash
ansible-playbook playbooks/variables_demo.yml \
  -e "app_environment=production app_port=443"
```

3. Passez plusieurs variables via un fichier JSON :

```bash
# Créez un fichier de surcharge
cat > /tmp/override.yml << 'EOF'
app_name: "mon-app-prod"
app_version: "3.0.0"
app_environment: "production"
EOF

ansible-playbook playbooks/variables_demo.yml \
  -e @/tmp/override.yml
```

Observez que les valeurs passées avec `-e` écrasent celles définies dans `vars_files`.

---

## ✅ Validation

Pour valider votre compréhension du lab, vérifiez les points suivants :

```bash
# 1. Le playbook variables_demo.yml s'exécute sans erreur
ansible-playbook playbooks/variables_demo.yml

# 2. Le rapport système a bien été créé
ls -la /tmp/rapport_systeme.txt
cat /tmp/rapport_systeme.txt

# 3. Le playbook facts_exploration.yml s'exécute sans erreur
ansible-playbook playbooks/facts_exploration.yml

# 4. La surcharge de variables fonctionne
ansible-playbook playbooks/variables_demo.yml \
  -e "app_name=test-override"
```

**Critères de réussite :**
- [ ] `variables_demo.yml` s'exécute entièrement sans erreur
- [ ] Le fichier `/tmp/rapport_systeme.txt` est créé avec les bonnes informations
- [ ] `facts_exploration.yml` affiche l'utilisation disque
- [ ] La surcharge via `-e` fonctionne correctement

---

## 🔍 Pour aller plus loin

- **`vars_prompt`** : Demander des variables de manière interactive à l'exécution
- **`include_vars`** : Charger des variables dynamiquement pendant l'exécution d'un play
- **Facts personnalisés** : Créer des scripts dans `/etc/ansible/facts.d/` pour des facts sur mesure
- **`ansible_facts` vs variables magiques** : Différences entre `ansible_hostname` et `ansible_facts['hostname']`
- **Chiffrement avec Ansible Vault** : Protéger les variables sensibles (mots de passe, clés API)

```bash
# Chiffrer un fichier de variables
ansible-vault encrypt vars/secrets.yml

# Exécuter un playbook avec un fichier chiffré
ansible-playbook playbook.yml --ask-vault-pass
```

---

## 💡 Solutions

<details>
<summary>Solution Exercice 2 – Fichier vars/mon_app.yml</summary>

```yaml
---
mon_app_nom: "super-app"
mon_app_port: 9000
mon_app_auteur: "votre_nom"
fonctionnalites:
  - authentification
  - tableau-de-bord
  - api-rest
```

</details>

<details>
<summary>Solution Exercice 2 – Playbook playbooks/mon_app.yml</summary>

```yaml
---
- name: Mon application
  hosts: local
  gather_facts: false
  vars_files:
    - ../vars/mon_app.yml
  tasks:
    - name: Présenter l'application
      ansible.builtin.debug:
        msg: |
          Application: {{ mon_app_nom }}
          Port: {{ mon_app_port }}
          Auteur: {{ mon_app_auteur }}
          Fonctionnalités: {{ fonctionnalites | join(', ') }}

    - name: Vérifier que le port est dans une plage valide
      ansible.builtin.assert:
        that:
          - mon_app_port > 1024
          - mon_app_port < 65535
        fail_msg: "Le port {{ mon_app_port }} n'est pas dans la plage autorisée"
        success_msg: "Port {{ mon_app_port }} valide"
```

</details>

<details>
<summary>Solution Exercice 3 – Afficher les interfaces réseau avec IP</summary>

```yaml
- name: Afficher les interfaces réseau avec IP
  ansible.builtin.debug:
    msg: "Interface {{ item }} - IP: {{ hostvars[inventory_hostname]['ansible_' + item]['ipv4']['address'] | default('N/A') }}"
  loop: "{{ ansible_interfaces }}"
  when: >
    hostvars[inventory_hostname]['ansible_' + item] is defined and
    hostvars[inventory_hostname]['ansible_' + item].get('ipv4') is defined
```

</details>

<details>
<summary>Solution Exercice 4 – Utilisation de extra_vars</summary>

```bash
# Surcharger plusieurs variables en ligne de commande
ansible-playbook playbooks/variables_demo.yml \
  -e "app_name=mon-app-prod app_version=3.0.0 app_environment=production app_port=443"

# Utiliser un fichier YAML de surcharge
cat > /tmp/prod_vars.yml << 'EOF'
---
app_name: "mon-app-prod"
app_version: "3.0.0"
app_environment: "production"
app_port: 443
EOF

ansible-playbook playbooks/variables_demo.yml \
  -e @/tmp/prod_vars.yml
```

</details>
