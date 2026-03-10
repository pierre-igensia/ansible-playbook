# Lab 06 – Conditions et Boucles

## Objectifs

À la fin de ce lab, vous serez capable de :

- Utiliser la clause `when` pour conditionner l'exécution des tâches
- Maîtriser les opérateurs de comparaison et les tests Jinja2
- Itérer sur des listes et des dictionnaires avec `loop`
- Utiliser `loop_control` pour personnaliser le comportement des boucles
- Implémenter des boucles avec `until` pour les tentatives répétées

## Prérequis

- Labs 01–05 complétés
- Notions de base en YAML et Jinja2
- Compréhension des variables et facts Ansible

## Durée estimée

60 minutes

## Mise en place

```bash
# Depuis la racine du dépôt
cd labs/lab-06-conditions-et-boucles

# Vérifier l'inventaire
cat inventory/mononode.yml

# Tester la connectivité
ansible local -m ping
```

---

## Concepts expliqués

### La clause `when` – Conditions

La directive `when` permet d'exécuter une tâche uniquement si une condition est vraie. Elle accepte des expressions Jinja2 (sans les accolades `{{ }}`).

```yaml
- name: Tâche conditionnelle
  ansible.builtin.debug:
    msg: "Exécuté seulement sur Debian"
  when: ansible_os_family == "Debian"
```

#### Opérateurs de comparaison

| Opérateur | Signification | Exemple |
|-----------|---------------|---------|
| `==` | Égal à | `env == "production"` |
| `!=` | Différent de | `env != "dev"` |
| `>` | Supérieur à | `ansible_memtotal_mb > 1024` |
| `>=` | Supérieur ou égal | `ansible_memtotal_mb >= 512` |
| `<` | Inférieur à | `version < "3.0"` |
| `<=` | Inférieur ou égal | `retries <= 5` |
| `in` | Contenu dans | `env in ["prod", "staging"]` |
| `not in` | Non contenu dans | `env not in ["dev"]` |

#### Tests Jinja2 courants

```yaml
# Check if a variable is defined
when: my_variable is defined

# Check if a variable is not defined
when: my_variable is not defined

# Check if a value is truthy
when: debug_mode is truthy

# Check software version
when: app_version is version("2.0", ">=")

# Check if a string matches a pattern
when: hostname is match("web.*")

# Check if a list is empty
when: my_list | length > 0
```

#### Conditions multiples

```yaml
# All conditions must be true (logical AND)
when:
  - env == "production"
  - ansible_memtotal_mb >= 2048
  - app_version is defined

# At least one condition must be true (logical OR)
when: env == "production" or env == "staging"

# Combined AND / OR
when: >
  (env == "production" and ansible_memtotal_mb >= 4096) or
  (env == "staging" and ansible_memtotal_mb >= 2048)
```

---

### Boucles avec `loop`

La directive `loop` remplace les anciens `with_items`, `with_dict`, etc. (toujours fonctionnels mais dépréciés).

#### Boucle sur une liste simple

```yaml
- name: Installer des paquets
  ansible.builtin.debug:
    msg: "Installer {{ item }}"
  loop:
    - git
    - curl
    - vim
```

#### Boucle sur une liste de dictionnaires

```yaml
- name: Créer des utilisateurs
  ansible.builtin.debug:
    msg: "Créer {{ item.name }} avec le shell {{ item.shell }}"
  loop:
    - { name: alice, shell: /bin/bash }
    - { name: bob, shell: /bin/sh }
```

#### Boucle sur un dictionnaire avec `dict2items`

```yaml
vars:
  service_ports:
    http: 80
    https: 443
    ssh: 22

tasks:
  - name: Afficher les services
    ansible.builtin.debug:
      msg: "Service {{ item.key }} sur le port {{ item.value }}"
    loop: "{{ service_ports | dict2items }}"
```

---

### `loop_control` – Contrôle des boucles

`loop_control` permet de personnaliser l'affichage et le comportement des boucles.

#### `label` – Personnaliser l'affichage

```yaml
- name: Boucle avec label personnalisé
  ansible.builtin.debug:
    msg: "Traitement de {{ item.name }}"
  loop: "{{ users }}"
  loop_control:
    label: "{{ item.name }}"   # affiche seulement le nom, pas tout le dict
```

#### `index_var` – Accéder à l'index

```yaml
- name: Boucle avec compteur
  ansible.builtin.debug:
    msg: "[{{ idx + 1 }}/{{ items | length }}] {{ item }}"
  loop: "{{ items }}"
  loop_control:
    index_var: idx
```

#### `pause` – Pause entre les itérations

```yaml
- name: Boucle avec pause
  ansible.builtin.debug:
    msg: "Traitement de {{ item }}"
  loop: "{{ elements }}"
  loop_control:
    pause: 2   # 2 secondes entre chaque itération
```

> **Attention** : `pause` dans `loop_control` peut poser des problèmes de résolution de portée lorsqu'il est combiné avec des expressions Jinja2 qui accèdent aux variables de boucle. Préférez `include_tasks` avec un module `ansible.builtin.pause` séparé si vous avez besoin de logique complexe (voir exercice 4).

---

### Boucle `until` – Tentatives répétées

La boucle `until` répète une tâche jusqu'à ce qu'une condition soit vraie, utile pour attendre qu'un service soit disponible.

```yaml
- name: Attendre que le service soit prêt
  ansible.builtin.command: curl -s http://localhost:8080/health
  register: health_check
  until: health_check.rc == 0
  retries: 10      # nombre maximum de tentatives
  delay: 5         # secondes entre chaque tentative
```

---

## Exercices

### Exercice 1 – Tâches conditionnelles avec `when`

**Objectif** : Comprendre comment les conditions contrôlent l'exécution des tâches.

1. Exécutez le playbook de conditions :

```bash
ansible-playbook playbooks/conditions.yml
```

2. Observez quelles tâches sont exécutées (status `ok`) et lesquelles sont ignorées (status `skipping`).

3. Modifiez la variable `env` pour observer les changements :

```bash
ansible-playbook playbooks/conditions.yml -e "env=development"
```

**Questions de réflexion :**
- Pourquoi la tâche « Condition multiple (OU) » est-elle ignorée lors de la première exécution ?
- Que se passe-t-il si vous passez `-e "min_memory_mb=999999"` ?

---

### Exercice 2 – Boucles simples avec `loop`

**Objectif** : Itérer sur des listes pour automatiser des tâches répétitives.

1. Exécutez le playbook de boucles :

```bash
ansible-playbook playbooks/boucles.yml
```

2. Vérifiez que les fichiers de configuration ont bien été créés :

```bash
cat /tmp/nginx.conf
cat /tmp/apache.conf
cat /tmp/mysql.conf
```

3. Créez votre propre playbook `playbooks/my_loop.yml` qui crée 5 répertoires numérotés dans `/tmp/lab06/` :

```yaml
---
- name: Créer des répertoires numérotés
  hosts: local
  gather_facts: false
  tasks:
    - name: Créer les répertoires
      ansible.builtin.file:
        path: "/tmp/lab06/dir{{ item }}"
        state: directory
        mode: '0755'
      loop: "{{ range(1, 6) | list }}"
```

---

### Exercice 3 – Boucles sur des dictionnaires

**Objectif** : Utiliser `dict2items` pour itérer sur des structures de données complexes.

Créez un playbook `playbooks/dict_loop.yml` qui gère une liste de services avec leurs ports et états :

```yaml
---
- name: Gestion de services
  hosts: local
  gather_facts: false
  vars:
    services:
      nginx:
        port: 80
        active: true
      mysql:
        port: 3306
        active: true
      redis:
        port: 6379
        active: false
  tasks:
    - name: Afficher l'état des services
      ansible.builtin.debug:
        msg: >
          Service {{ item.key }} (port {{ item.value.port }}) :
          {{ 'ACTIF' if item.value.active else 'INACTIF' }}
      loop: "{{ services | dict2items }}"
      loop_control:
        label: "{{ item.key }}"
```

---

### Exercice 4 – Simulation de déploiement avec `include_tasks`

**Objectif** : Simuler un déploiement séquentiel avec pause entre chaque composant, en utilisant `include_tasks` pour éviter les conflits de portée de `pause` dans `loop_control`.

Le playbook `boucles.yml` inclut un second play « Simulation de déploiement » qui utilise `include_tasks` pour combiner affichage et pause par composant :

```bash
ansible-playbook playbooks/boucles.yml
```

Examinez le fichier `playbooks/deploy_component.yml` pour comprendre comment la logique est déportée dans un fichier de tâches séparé, évitant ainsi le problème de résolution de portée entre `pause` et les variables de boucle.

---

## Validation

```bash
# 1. Le playbook conditions.yml s'exécute sans erreur
ansible-playbook playbooks/conditions.yml

# 2. Le playbook boucles.yml crée bien les fichiers attendus
ansible-playbook playbooks/boucles.yml
ls -la /tmp/nginx.conf /tmp/apache.conf /tmp/mysql.conf

# 3. Vérifier le contenu d'un fichier créé par la boucle
cat /tmp/nginx.conf

# 4. La condition de surcharge fonctionne
ansible-playbook playbooks/conditions.yml \
  -e "env=development"
```

**Critères de réussite :**
- [ ] `conditions.yml` s'exécute et les tâches appropriées sont ignorées/exécutées
- [ ] `boucles.yml` crée les 3 fichiers de configuration dans `/tmp/`
- [ ] La simulation de déploiement s'exécute avec une pause entre chaque composant
- [ ] `loop_control` avec `index_var` affiche le bon index
- [ ] La surcharge via `-e "env=development"` modifie bien l'exécution

---

## Pour aller plus loin

- **`with_subelements`** : Itérer sur des sous-listes dans des structures imbriquées
- **`with_nested`** / `loop` avec `product` : Boucles imbriquées (produit cartésien)
- **`when` avec `register`** : Conditions basées sur la sortie d'une tâche précédente
- **`failed_when` / `changed_when`** : Personnaliser quand Ansible considère une tâche comme échouée ou modifiée
- **Filtres Jinja2** : `select`, `reject`, `selectattr`, `rejectattr` pour filtrer des listes

```yaml
# Filter a list with selectattr
- name: Afficher seulement les utilisateurs actifs
  ansible.builtin.debug:
    msg: "{{ item.name }}"
  loop: "{{ users | selectattr('active', 'equalto', true) | list }}"
```

---

## Solutions

<details>
<summary>Solution Exercice 2 – Créer 5 répertoires numérotés</summary>

```yaml
---
- name: Créer des répertoires numérotés
  hosts: local
  gather_facts: false
  tasks:
    - name: Créer le répertoire parent
      ansible.builtin.file:
        path: /tmp/lab06
        state: directory
        mode: '0755'

    - name: Créer les sous-répertoires
      ansible.builtin.file:
        path: "/tmp/lab06/dir{{ item }}"
        state: directory
        mode: '0755'
      loop: "{{ range(1, 6) | list }}"
      loop_control:
        label: "dir{{ item }}"

    - name: Vérifier les répertoires créés
      ansible.builtin.command: ls -la /tmp/lab06/
      register: result
      changed_when: false

    - name: Afficher le résultat
      ansible.builtin.debug:
        var: result.stdout_lines
```

</details>

<details>
<summary>Solution Exercice 3 – Boucle sur dictionnaire de services</summary>

```yaml
---
- name: Gestion de services
  hosts: local
  gather_facts: false
  vars:
    services:
      nginx:
        port: 80
        active: true
      mysql:
        port: 3306
        active: true
      redis:
        port: 6379
        active: false
  tasks:
    - name: Afficher l'état des services
      ansible.builtin.debug:
        msg: >
          Service {{ item.key }} (port {{ item.value.port }}) :
          {{ 'ACTIF' if item.value.active else 'INACTIF' }}
      loop: "{{ services | dict2items }}"
      loop_control:
        label: "{{ item.key }}"

    - name: Lister seulement les services actifs
      ansible.builtin.debug:
        msg: "Services actifs : {{ services | dict2items | selectattr('value.active') | map(attribute='key') | list | join(', ') }}"
```

</details>

<details>
<summary>Solution Exercice 4 – Déploiement avec include_tasks</summary>

Le playbook `boucles.yml` contient le play « Simulation de déploiement » qui boucle sur les composants avec `include_tasks`. Le fichier `deploy_component.yml` contient les tâches exécutées pour chaque composant :

```yaml
# playbooks/deploy_component.yml
---
- name: "Déploiement de {{ item.name }}"
  ansible.builtin.debug:
    msg: "[{{ idx + 1 }}/{{ components | length }}] Déploiement de {{ item.name }}..."

- name: "Pause entre les composants"
  ansible.builtin.pause:
    seconds: "{{ delay_seconds }}"
  when: idx < (components | length - 1)
```

Cette approche évite le conflit de portée entre `pause` dans `loop_control` et les variables de boucle (`item`, `idx`). En déportant la pause dans un fichier inclus, chaque variable est résolue dans son propre contexte.

</details>
