# Lab 16 – Includes et Imports

## 🎯 Objectifs

- Comprendre la différence entre `include_tasks` et `import_tasks`
- Utiliser `import_playbook` pour organiser les playbooks en plusieurs fichiers
- Inclure des rôles dynamiquement avec `include_role`
- Maîtriser le passage de variables aux includes et imports

## 📋 Prérequis

- Labs 01–15 complétés
- Maîtrise des rôles Ansible (Lab 09)
- Environnement virtuel Python activé

## ⏱️ Durée estimée

60 minutes

## 🏗️ Mise en place

```bash
# Activer l'environnement virtuel
source ~/ansible-venv/bin/activate

# Se placer dans le répertoire du lab
cd labs/lab-16-includes-imports/

# Vérifier la structure du lab
find . -type f | sort
```

## 📚 Concepts expliqués

### import vs include : la différence fondamentale

| Aspect | `import_*` (statique) | `include_*` (dynamique) |
|--------|----------------------|------------------------|
| Traitement | Au moment du parsing | À l'exécution |
| Tags | Propagés aux tâches incluses | Non propagés (par défaut) |
| Variables | Limitées (pas de `register`) | Complètes |
| Boucles (`loop`) | ❌ Impossible | ✅ Possible |
| Condition `when` | Appliquée à chaque tâche | Appliquée à l'inclusion entière |
| Noms de tâches dynamiques | ❌ Non | ✅ Oui (avec variables) |
| Lister les tâches (`--list-tasks`) | ✅ Visible | ❌ Non visible au parsing |

**Règle pratique :**
- Utilisez `import_*` par défaut (prévisible, compatible avec les tags)
- Utilisez `include_*` quand vous avez besoin de dynamisme (boucles, noms de fichiers calculés)

### import_tasks et include_tasks

```yaml
# Statique - résolu au parsing, tâches visibles dans --list-tasks
- name: Installer les paquets
  ansible.builtin.import_tasks: taches/installation.yml

# Dynamique - résolu à l'exécution, permet les noms de fichiers variables
- name: Configuration selon l'OS
  ansible.builtin.include_tasks: "taches/{{ ansible_os_family | lower }}.yml"

# Dynamique avec une boucle (impossible avec import_tasks)
- name: Déployer chaque composant
  ansible.builtin.include_tasks: taches/deployer_composant.yml
  loop: "{{ composants }}"
  loop_control:
    loop_var: composant
```

### import_playbook

`import_playbook` permet de découper un grand playbook en plusieurs fichiers réutilisables :

```yaml
# site.yml - Point d'entrée unique
- name: "Étape 1 : Infrastructure"
  ansible.builtin.import_playbook: playbooks/infrastructure.yml

- name: "Étape 2 : Application"
  ansible.builtin.import_playbook: playbooks/application.yml

- name: "Étape 3 : Vérification"
  ansible.builtin.import_playbook: playbooks/validation_finale.yml
```

> **Note** : Dans ce lab, le fichier `site.yml` importe `deploiement.yml` qui contient déjà les trois phases (installation, configuration, validation). La structure ci-dessus illustre le principe général avec plusieurs fichiers séparés.

Avantages :
- Un seul point d'entrée (`site.yml`)
- Chaque fichier peut être exécuté indépendamment
- Réutilisation dans différents contextes

### include_role vs import_role

```yaml
# import_role : statique, résolu au parsing
- name: Appliquer le rôle serveur-web
  ansible.builtin.import_role:
    name: serveur-web
  vars:
    port: 80

# include_role : dynamique, peut être dans une boucle
- name: Déployer plusieurs services
  ansible.builtin.include_role:
    name: "{{ item.role }}"
  vars:
    port: "{{ item.port }}"
  loop:
    - { role: serveur-web, port: 80 }
    - { role: serveur-api, port: 8080 }
    - { role: serveur-cache, port: 6379 }
```

### Passage de variables

Les variables peuvent être passées aux includes de plusieurs manières :

```yaml
# Via vars (priorité haute)
- ansible.builtin.include_tasks: taches/deployer.yml
  vars:
    app_port: 8080
    app_env: "production"

# Via apply (pour import_tasks, applique les vars à toutes les tâches)
- ansible.builtin.import_tasks: taches/deployer.yml
  vars:
    app_port: 8080
```

### Organisation recommandée d'un projet

```
projet/
├── site.yml                    ← Point d'entrée (import_playbook)
├── playbooks/
│   ├── infrastructure.yml      ← Playbook infrastructure
│   ├── application.yml         ← Playbook application
│   └── verification.yml        ← Playbook vérification
├── tasks/
│   ├── installation.yml        ← Tâches réutilisables
│   ├── configuration.yml
│   └── validation.yml
└── roles/
    └── mon-role/
```

## 🛠️ Exercices

### Exercice 1 – Découper un playbook avec import_tasks

Exécutez le playbook de déploiement qui utilise `import_tasks` :

```bash
# Exécuter le playbook
ansible-playbook playbooks/deploiement.yml

# Lister les tâches (les tâches importées sont visibles car statiques)
ansible-playbook playbooks/deploiement.yml --list-tasks

# Vérifier le résultat
ls /tmp/includes_demo/
cat /tmp/includes_demo/config/app.conf
cat /tmp/includes_demo/install/journal.log
```

**Attendu** : Les tâches des fichiers `installation.yml`, `configuration.yml` et `validation.yml` sont toutes visibles dans `--list-tasks`.

---

### Exercice 2 – Include dynamique selon l'OS

Créez un fichier `tasks/debian.yml` et `tasks/redhat.yml` pour simuler des tâches spécifiques à l'OS :

```yaml
# tasks/debian.yml
---
- name: Tâche spécifique Debian/Ubuntu
  ansible.builtin.debug:
    msg: "Système Debian/Ubuntu détecté : {{ ansible_distribution }} {{ ansible_distribution_version }}"
```

```yaml
# tasks/redhat.yml
---
- name: Tâche spécifique RedHat/CentOS
  ansible.builtin.debug:
    msg: "Système RedHat/CentOS détecté : {{ ansible_distribution }} {{ ansible_distribution_version }}"
```

Puis créez un playbook qui inclut dynamiquement le bon fichier selon l'OS :

```yaml
# playbooks/os_specifique.yml
---
- name: Tâches spécifiques à l'OS
  hosts: local
  gather_facts: true
  tasks:
    - name: Inclure les tâches selon l'OS
      ansible.builtin.include_tasks: "../tasks/{{ ansible_os_family | lower }}.yml"
```

```bash
ansible-playbook playbooks/os_specifique.yml
```

---

### Exercice 3 – Organiser avec import_playbook

Exécutez le playbook principal `site.yml` qui utilise `import_playbook` :

```bash
# Exécuter le playbook site.yml
ansible-playbook playbooks/site.yml

# Lister toutes les tâches du site complet
ansible-playbook playbooks/site.yml --list-tasks

# Utiliser les tags (possibles car import est statique)
ansible-playbook playbooks/site.yml --list-tags
```

**Attendu** : `site.yml` exécute le déploiement puis la confirmation finale.

---

### Exercice 4 – include_tasks avec boucle

Créez un fichier de tâches réutilisable `tasks/creer_utilisateur.yml` et utilisez-le dans une boucle :

```yaml
# tasks/creer_utilisateur.yml
---
- name: Créer le répertoire de l'utilisateur {{ utilisateur.nom }}
  ansible.builtin.file:
    path: "/tmp/includes_demo/utilisateurs/{{ utilisateur.nom }}"
    state: directory
    mode: '0700'

- name: Créer le fichier de profil de {{ utilisateur.nom }}
  ansible.builtin.copy:
    content: |
      nom={{ utilisateur.nom }}
      role={{ utilisateur.role }}
      email={{ utilisateur.email }}
    dest: "/tmp/includes_demo/utilisateurs/{{ utilisateur.nom }}/profil.conf"
    mode: '0600'
```

Puis utilisez-le avec `include_tasks` en boucle (impossible avec `import_tasks`) :

```yaml
# Dans un playbook :
- name: Créer les utilisateurs
  ansible.builtin.include_tasks: ../tasks/creer_utilisateur.yml
  loop:
    - { nom: "alice", role: "admin", email: "alice@exemple.com" }
    - { nom: "bob", role: "dev", email: "bob@exemple.com" }
    - { nom: "carol", role: "ops", email: "carol@exemple.com" }
  loop_control:
    loop_var: utilisateur
```

```bash
ansible-playbook playbooks/utilisateurs.yml
ls /tmp/includes_demo/utilisateurs/
```

## ✅ Validation

```bash
# Nettoyer l'environnement de test
rm -rf /tmp/includes_demo

# Exécuter le playbook de déploiement
ansible-playbook playbooks/deploiement.yml

# Vérifier les fichiers créés
ls -la /tmp/includes_demo/
ls -la /tmp/includes_demo/config/
cat /tmp/includes_demo/config/app.conf

# Exécuter le site complet
ansible-playbook playbooks/site.yml

# Lister les tâches (import_tasks visible, include_tasks non visible au parsing)
ansible-playbook playbooks/deploiement.yml --list-tasks
```

## 🔍 Pour aller plus loin

- [Documentation : réutiliser du contenu Ansible](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_reuse.html)
- [Comparatif includes vs imports](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_reuse_includes.html)
- [import_playbook](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/import_playbook_module.html)
- **Défi 1** : Créez une structure de playbook avec `import_playbook` pour 3 environnements (dev, staging, prod), chaque environnement ayant ses propres variables et tâches spécifiques.
- **Défi 2** : Utilisez `include_tasks` avec une boucle pour appliquer plusieurs rôles dynamiquement, en passant des variables différentes à chaque itération.

## 💡 Solutions

<details>
<summary>Solution – Exercice 1 : import_tasks</summary>

```bash
# Exécution
ansible-playbook playbooks/deploiement.yml

# Les tâches importées sont visibles car statiques
ansible-playbook playbooks/deploiement.yml --list-tasks
# Affiche toutes les tâches de installation.yml, configuration.yml ET validation.yml

# Vérification
cat /tmp/includes_demo/config/app.conf
```

</details>

<details>
<summary>Solution – Exercice 2 : Include dynamique selon l'OS</summary>

```bash
# Créer les fichiers de tâches OS
cat > tasks/debian.yml << 'EOF'
---
- name: Tâche spécifique Debian/Ubuntu
  ansible.builtin.debug:
    msg: "Système {{ ansible_distribution }} {{ ansible_distribution_version }} détecté"
EOF

cat > tasks/redhat.yml << 'EOF'
---
- name: Tâche spécifique RedHat/CentOS
  ansible.builtin.debug:
    msg: "Système {{ ansible_distribution }} {{ ansible_distribution_version }} détecté"
EOF

# Créer le playbook
cat > playbooks/os_specifique.yml << 'EOF'
---
- name: Tâches spécifiques à l'OS
  hosts: local
  gather_facts: true
  tasks:
    - name: Inclure les tâches selon l'OS
      ansible.builtin.include_tasks: "../tasks/{{ ansible_os_family | lower }}.yml"
EOF

ansible-playbook playbooks/os_specifique.yml
```

</details>

<details>
<summary>Solution – Exercice 4 : include_tasks avec boucle</summary>

```yaml
# tasks/creer_utilisateur.yml
---
- name: Créer le répertoire de {{ utilisateur.nom }}
  ansible.builtin.file:
    path: "/tmp/includes_demo/utilisateurs/{{ utilisateur.nom }}"
    state: directory
    mode: '0700'

- name: Créer le profil de {{ utilisateur.nom }}
  ansible.builtin.copy:
    content: |
      nom={{ utilisateur.nom }}
      role={{ utilisateur.role }}
      email={{ utilisateur.email }}
    dest: "/tmp/includes_demo/utilisateurs/{{ utilisateur.nom }}/profil.conf"
    mode: '0600'
```

```yaml
# playbooks/utilisateurs.yml
---
- name: Gérer les utilisateurs
  hosts: local
  gather_facts: false
  tasks:
    - ansible.builtin.file:
        path: /tmp/includes_demo/utilisateurs
        state: directory
        mode: '0755'

    - ansible.builtin.include_tasks: ../tasks/creer_utilisateur.yml
      loop:
        - { nom: "alice", role: "admin", email: "alice@exemple.com" }
        - { nom: "bob",   role: "dev",   email: "bob@exemple.com" }
        - { nom: "carol", role: "ops",   email: "carol@exemple.com" }
      loop_control:
        loop_var: utilisateur
```

</details>

<details>
<summary>Solution – Défi 1 : Multi-environnements avec import_playbook</summary>

Structure du projet :

```
site_multi_env.yml
playbooks/
  commun.yml
  dev.yml
  staging.yml
  prod.yml
vars/
  dev.yml
  staging.yml
  prod.yml
```

```yaml
# site_multi_env.yml
---
- ansible.builtin.import_playbook: playbooks/commun.yml
- ansible.builtin.import_playbook: playbooks/dev.yml
  when: environnement == 'dev'
- ansible.builtin.import_playbook: playbooks/staging.yml
  when: environnement == 'staging'
- ansible.builtin.import_playbook: playbooks/prod.yml
  when: environnement == 'prod'
```

```bash
# Déployer en dev
ansible-playbook site_multi_env.yml -e "environnement=dev"

# Déployer en production
ansible-playbook site_multi_env.yml -e "environnement=prod"
```

</details>
