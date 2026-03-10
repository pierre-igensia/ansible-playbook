# Lab 08 – Gestion des Fichiers

## 🎯 Objectifs

À la fin de ce lab, vous serez capable de :

- Gérer des fichiers, répertoires et liens symboliques avec le module `file`
- Copier des fichiers et du contenu avec le module `copy`
- Modifier des lignes précises dans un fichier avec `lineinfile`
- Gérer des blocs de texte avec `blockinfile`
- Générer des fichiers dynamiques à partir de templates Jinja2 avec `template`
- Récupérer des fichiers distants avec `fetch`

## 📋 Prérequis

- Labs 01–07 complétés
- Notions de base sur les permissions Unix (chmod, chown)
- Introduction aux templates Jinja2 (variables, conditions, boucles)

## ⏱️ Durée estimée

60 minutes

## 🏗️ Mise en place

```bash
# Depuis la racine du dépôt
cd labs/lab-08-gestion-fichiers

# Vérifier l'inventaire
cat inventory/hosts.ini

# Tester la connectivité
ansible -i inventory/hosts.ini local -m ping
```

---

## 📚 Concepts expliqués

### `copy` vs `template`

Ces deux modules permettent de déployer des fichiers, mais avec des approches différentes :

| Module | Utilisation | Dynamique ? |
|--------|-------------|-------------|
| `copy` | Copie un fichier statique ou du contenu inline | Non (sauf avec `content:`) |
| `template` | Génère un fichier à partir d'un template Jinja2 | Oui |

```yaml
# copy : fichier statique
- name: Copier un fichier de conf statique
  ansible.builtin.copy:
    src: files/nginx.conf      # fichier source (local)
    dest: /etc/nginx/nginx.conf
    owner: root
    group: root
    mode: '0644'

# copy : contenu inline
- name: Créer un fichier avec contenu
  ansible.builtin.copy:
    content: |
      [section]
      clé=valeur
    dest: /etc/app/config.ini
    mode: '0644'

# template : fichier dynamique avec Jinja2
- name: Générer la configuration depuis un template
  ansible.builtin.template:
    src: templates/nginx.conf.j2   # template source (local)
    dest: /etc/nginx/nginx.conf
    mode: '0644'
```

---

### Le module `file` – Créer, modifier, supprimer

Le module `file` est le couteau suisse de la gestion de fichiers Ansible.

#### États possibles (`state`)

| État | Action |
|------|--------|
| `present` | Assure que le fichier existe (ne le modifie pas) |
| `absent` | Supprime le fichier/répertoire |
| `directory` | Crée le répertoire (et ses parents si `recurse: true`) |
| `touch` | Crée le fichier s'il n'existe pas, met à jour l'horodatage sinon |
| `link` | Crée un lien symbolique |
| `hard` | Crée un lien physique (hard link) |

```yaml
# Créer un répertoire
- name: Créer le répertoire de l'application
  ansible.builtin.file:
    path: /opt/mon-app
    state: directory
    owner: appuser
    group: appuser
    mode: '0755'

# Créer une arborescence complète
- name: Créer l'arborescence
  ansible.builtin.file:
    path: /opt/mon-app/logs/archive
    state: directory
    recurse: true   # crée tous les répertoires parents manquants
    mode: '0755'

# Supprimer un fichier
- name: Supprimer l'ancien fichier de config
  ansible.builtin.file:
    path: /etc/app/old.conf
    state: absent

# Créer un lien symbolique
- name: Créer un lien vers la config active
  ansible.builtin.file:
    src: /etc/app/config-v2.conf
    dest: /etc/app/config.conf
    state: link

# Modifier uniquement les permissions
- name: Sécuriser le fichier de secrets
  ansible.builtin.file:
    path: /etc/app/secrets.conf
    owner: root
    group: app
    mode: '0640'
```

---

### `lineinfile` – Modifier une ligne précise

`lineinfile` garantit qu'une ligne spécifique est présente (ou absente) dans un fichier. Il est **idempotent** : si la ligne est déjà correcte, rien n'est modifié.

```yaml
# S'assurer qu'une ligne existe
- name: Activer le module mod_rewrite dans Apache
  ansible.builtin.lineinfile:
    path: /etc/apache2/apache2.conf
    line: "LoadModule rewrite_module modules/mod_rewrite.so"
    state: present

# Remplacer une ligne correspondant à un motif (regex)
- name: Changer le port d'écoute
  ansible.builtin.lineinfile:
    path: /etc/app/config.ini
    regexp: '^port='
    line: "port=9090"

# Insérer une ligne après une autre
- name: Ajouter la configuration SSL après [server]
  ansible.builtin.lineinfile:
    path: /etc/app/config.ini
    insertafter: '^\[server\]'
    line: "ssl=enabled"

# Supprimer une ligne
- name: Supprimer la ligne de debug
  ansible.builtin.lineinfile:
    path: /etc/app/config.ini
    regexp: '^debug='
    state: absent

# Créer une sauvegarde avant modification
- name: Modifier avec sauvegarde
  ansible.builtin.lineinfile:
    path: /etc/app/config.ini
    regexp: '^log_level='
    line: "log_level=WARNING"
    backup: true   # crée /etc/app/config.ini.12345 (timestamp)
```

---

### `blockinfile` – Gérer un bloc de texte

`blockinfile` insère, remplace ou supprime un **bloc de texte** délimité par des marqueurs. Les marqueurs garantissent l'idempotence.

```yaml
- name: Ajouter la configuration de métriques
  ansible.builtin.blockinfile:
    path: /etc/app/config.ini
    marker: "# {mark} CONFIGURATION MÉTRIQUES ANSIBLE"
    block: |
      [métriques]
      activé=true
      port=9090
      chemin=/metrics
      intervalle=30s

# Le fichier contiendra :
# # BEGIN CONFIGURATION MÉTRIQUES ANSIBLE
# [métriques]
# activé=true
# port=9090
# ...
# # END CONFIGURATION MÉTRIQUES ANSIBLE
```

```yaml
# Supprimer un bloc géré
- name: Supprimer le bloc de métriques
  ansible.builtin.blockinfile:
    path: /etc/app/config.ini
    marker: "# {mark} CONFIGURATION MÉTRIQUES ANSIBLE"
    state: absent
```

---

### Templates Jinja2 avec `template`

Les templates Jinja2 permettent de générer des fichiers de configuration dynamiques en fonction des variables et des facts Ansible.

#### Syntaxe de base

```jinja2
# Variables
{{ variable }}
{{ dict.clé }}
{{ liste[0] }}
{{ variable | default('valeur_par_defaut') }}

# Conditions
{% if condition %}
  contenu si vrai
{% elif autre_condition %}
  contenu alternatif
{% else %}
  contenu par défaut
{% endif %}

# Boucles
{% for element in liste %}
  ligne pour {{ element }}
{% endfor %}

# Commentaires (non inclus dans le fichier généré)
{# Ceci est un commentaire Jinja2 #}
```

#### Exemple de template

```jinja2
# /templates/nginx.conf.j2
# Généré par Ansible - NE PAS MODIFIER MANUELLEMENT
# Date: {{ ansible_date_time.date }}

worker_processes {{ nginx_workers | default(ansible_processor_vcpus) }};

http {
    server {
        listen {{ nginx_port | default(80) }};
        server_name {{ ansible_hostname }};

{% if ssl_enabled | default(false) %}
        ssl on;
        ssl_certificate {{ ssl_cert_path }};
{% endif %}

{% for location in nginx_locations | default(['/']) %}
        location {{ location }} {
            proxy_pass http://localhost:{{ app_port }};
        }
{% endfor %}
    }
}
```

---

### `fetch` – Récupérer des fichiers distants

Le module `fetch` copie des fichiers **depuis** les hôtes gérés **vers** la machine de contrôle Ansible (sens inverse de `copy`) :

```yaml
- name: Récupérer les logs d'application
  ansible.builtin.fetch:
    src: /var/log/mon-app/app.log
    dest: ./logs/              # répertoire local
    flat: false                # crée logs/<hostname>/var/log/.../app.log

- name: Récupérer un fichier à plat
  ansible.builtin.fetch:
    src: /etc/app/config.ini
    dest: ./configs/config_{{ inventory_hostname }}.ini
    flat: true                 # chemin exact (pas de sous-répertoires)
```

---

## 🛠️ Exercices

### Exercice 1 – Opérations sur les fichiers avec `file`

**Objectif** : Maîtriser la création, modification et suppression de fichiers et répertoires.

1. Exécutez le playbook de démonstration :

```bash
ansible-playbook -i inventory/hosts.ini playbooks/fichiers_demo.yml
```

2. Vérifiez la structure créée :

```bash
find /tmp/fichiers_demo -ls
```

3. Vérifiez le lien symbolique :

```bash
ls -la /tmp/fichiers_demo/config/
readlink /tmp/fichiers_demo/config/current.conf
```

**Défi** : Créez un playbook `playbooks/arborescence.yml` qui crée la structure suivante avec les bonnes permissions :

```
/tmp/mon-projet/
├── bin/          (0755)
├── conf/         (0750)
│   └── .gitkeep  (0644)
├── logs/         (0775)
└── data/         (0770)
```

---

### Exercice 2 – Copier des fichiers et du contenu

**Objectif** : Utiliser `copy` pour déployer des fichiers statiques et du contenu inline.

Observez dans `fichiers_demo.yml` comment `copy` est utilisé avec `content:` pour créer un script.

Créez `playbooks/copie_demo.yml` qui déploie plusieurs fichiers :

```yaml
---
- name: Déploiement de fichiers de configuration
  hosts: local
  gather_facts: false
  vars:
    app_dir: /tmp/copie_demo
    app_name: "ma-super-app"
    app_version: "1.5.0"

  tasks:
    - name: Créer le répertoire de l'application
      ansible.builtin.file:
        path: "{{ app_dir }}"
        state: directory
        mode: '0755'

    - name: Créer le fichier de version
      ansible.builtin.copy:
        content: "{{ app_version }}\n"
        dest: "{{ app_dir }}/VERSION"
        mode: '0444'

    - name: Créer le fichier README
      ansible.builtin.copy:
        content: |
          # {{ app_name }}
          Version: {{ app_version }}

          ## Description
          Application de démonstration pour le Lab 08 Ansible.
        dest: "{{ app_dir }}/README.md"
        mode: '0644'

    - name: Vérifier le contenu du répertoire
      ansible.builtin.command: ls -la {{ app_dir }}/
      register: contenu
      changed_when: false

    - name: Afficher le contenu
      ansible.builtin.debug:
        var: contenu.stdout_lines
```

---

### Exercice 3 – Modifier des fichiers avec `lineinfile` et `blockinfile`

**Objectif** : Modifier chirurgicalement des fichiers de configuration existants.

1. Exécutez le playbook de démonstration et observez comment `lineinfile` et `blockinfile` modifient le fichier généré par le template :

```bash
ansible-playbook -i inventory/hosts.ini playbooks/fichiers_demo.yml
cat /tmp/fichiers_demo/config/app.conf
```

2. Créez `playbooks/modifier_config.yml` pour pratiquer :

```yaml
---
- name: Modification de fichiers de configuration
  hosts: local
  gather_facts: false
  vars:
    config_file: /tmp/fichiers_demo/config/app.conf

  tasks:
    - name: Vérifier que le fichier source existe
      ansible.builtin.stat:
        path: "{{ config_file }}"
      register: stat_config

    - name: Arrêter si le fichier n'existe pas
      ansible.builtin.fail:
        msg: "Exécutez d'abord fichiers_demo.yml pour créer {{ config_file }}"
      when: not stat_config.stat.exists

    - name: Changer le niveau de log en WARNING
      ansible.builtin.lineinfile:
        path: "{{ config_file }}"
        regexp: '^niveau='
        line: "niveau=WARNING"
        backup: true

    - name: Ajouter la section sécurité
      ansible.builtin.blockinfile:
        path: "{{ config_file }}"
        marker: "# {mark} SECTION SÉCURITÉ"
        insertafter: EOF
        block: |
          [sécurité]
          https=true
          hsts=true
          max_tentatives_connexion=5
          délai_blocage=300

    - name: Afficher le fichier modifié
      ansible.builtin.command: cat {{ config_file }}
      register: config_final
      changed_when: false

    - name: Montrer le résultat
      ansible.builtin.debug:
        var: config_final.stdout_lines
```

---

### Exercice 4 – Templates Jinja2

**Objectif** : Générer des fichiers de configuration dynamiques avec Jinja2.

1. Examinez le template existant :

```bash
cat templates/app.conf.j2
```

2. Observez la génération dans `fichiers_demo.yml` :

```bash
ansible-playbook -i inventory/hosts.ini playbooks/fichiers_demo.yml
cat /tmp/fichiers_demo/config/app.conf
```

3. Créez votre propre template `templates/nginx_vhost.conf.j2` :

```jinja2
# Virtuel host nginx pour {{ app_name }}
# Généré par Ansible le {{ ansible_date_time.date }}

server {
    listen {{ vhost_port | default(80) }};
    server_name {{ vhost_domain }};

    root {{ vhost_root | default('/var/www/' + app_name) }};
    index index.html index.php;

{% if ssl_enabled | default(false) %}
    # Configuration SSL
    listen {{ ssl_port | default(443) }} ssl;
    ssl_certificate {{ ssl_cert }};
    ssl_certificate_key {{ ssl_key }};
{% endif %}

    access_log /var/log/nginx/{{ app_name }}_access.log;
    error_log  /var/log/nginx/{{ app_name }}_error.log;

    location / {
        try_files $uri $uri/ =404;
    }

{% if php_enabled | default(false) %}
    location ~ \.php$ {
        fastcgi_pass unix:/var/run/php/php-fpm.sock;
        fastcgi_index index.php;
        include fastcgi_params;
    }
{% endif %}
}
```

4. Créez `playbooks/template_nginx.yml` pour l'utiliser :

```yaml
---
- name: Générer la configuration nginx
  hosts: local
  gather_facts: true
  vars:
    app_name: "mon-site-web"
    vhost_domain: "mon-site.exemple.fr"
    vhost_port: 80
    ssl_enabled: false
    php_enabled: true

  tasks:
    - name: Créer le répertoire de sortie
      ansible.builtin.file:
        path: /tmp/nginx_configs
        state: directory
        mode: '0755'

    - name: Générer le virtual host
      ansible.builtin.template:
        src: ../templates/nginx_vhost.conf.j2
        dest: "/tmp/nginx_configs/{{ app_name }}.conf"
        mode: '0644'

    - name: Afficher la configuration générée
      ansible.builtin.command: cat /tmp/nginx_configs/{{ app_name }}.conf
      register: vhost_content
      changed_when: false

    - name: Montrer le résultat
      ansible.builtin.debug:
        var: vhost_content.stdout_lines
```

---

## ✅ Validation

```bash
# 1. Le playbook principal s'exécute sans erreur
ansible-playbook -i inventory/hosts.ini playbooks/fichiers_demo.yml

# 2. Vérifier la structure de répertoires créée
find /tmp/fichiers_demo -ls

# 3. Vérifier le fichier généré par le template
cat /tmp/fichiers_demo/config/app.conf

# 4. Vérifier les modifications de lineinfile
grep 'version=' /tmp/fichiers_demo/config/app.conf

# 5. Vérifier le bloc ajouté par blockinfile
grep -A5 'BEGIN BLOC' /tmp/fichiers_demo/config/app.conf

# 6. Vérifier le lien symbolique
readlink -f /tmp/fichiers_demo/config/current.conf

# 7. Nettoyer
rm -rf /tmp/fichiers_demo /tmp/nginx_configs /tmp/copie_demo
```

**Critères de réussite :**
- [ ] La structure de répertoires est créée avec les bonnes permissions
- [ ] Le template génère un fichier de configuration valide
- [ ] `lineinfile` modifie correctement la ligne ciblée (idempotent)
- [ ] `blockinfile` insère le bloc avec les bons marqueurs
- [ ] Le lien symbolique pointe vers le bon fichier
- [ ] Deuxième exécution du playbook : toutes les tâches sont `ok` (idempotence)

---

## 🔍 Pour aller plus loin

- **`assemble`** : Assembler plusieurs fichiers fragments en un seul fichier
- **`replace`** : Remplacer toutes les occurrences d'un motif dans un fichier
- **`stat`** : Obtenir des informations sur un fichier (existence, taille, permissions, checksum)
- **`find`** : Trouver des fichiers correspondant à des critères
- **`synchronize`** : Synchroniser des répertoires (basé sur rsync)
- **Filtres Jinja2 pour les chemins** : `basename`, `dirname`, `expanduser`, `realpath`

```yaml
# Utiliser stat pour conditionner une tâche
- name: Vérifier si le fichier existe
  ansible.builtin.stat:
    path: /etc/app/config.ini
  register: stat_config

- name: Créer la config seulement si elle n'existe pas
  ansible.builtin.copy:
    content: "[defaults]\nport=8080\n"
    dest: /etc/app/config.ini
  when: not stat_config.stat.exists
```

```yaml
# Utiliser find pour lister des fichiers
- name: Trouver les anciens logs
  ansible.builtin.find:
    paths: /var/log/mon-app
    patterns: "*.log"
    age: "7d"      # plus vieux que 7 jours
    recurse: true
  register: vieux_logs

- name: Supprimer les anciens logs
  ansible.builtin.file:
    path: "{{ item.path }}"
    state: absent
  loop: "{{ vieux_logs.files }}"
  loop_control:
    label: "{{ item.path | basename }}"
```

---

## 💡 Solutions

<details>
<summary>Solution Exercice 1 – Arborescence avec permissions</summary>

```yaml
---
- name: Créer une arborescence de projet
  hosts: local
  gather_facts: false
  vars:
    projet_dir: /tmp/mon-projet

  tasks:
    - name: Créer la structure de répertoires
      ansible.builtin.file:
        path: "{{ item.path }}"
        state: directory
        mode: "{{ item.mode }}"
      loop:
        - { path: "{{ projet_dir }}/bin",  mode: '0755' }
        - { path: "{{ projet_dir }}/conf", mode: '0750' }
        - { path: "{{ projet_dir }}/logs", mode: '0775' }
        - { path: "{{ projet_dir }}/data", mode: '0770' }
      loop_control:
        label: "{{ item.path | basename }}"

    - name: Créer le fichier .gitkeep dans conf/
      ansible.builtin.file:
        path: "{{ projet_dir }}/conf/.gitkeep"
        state: touch
        mode: '0644'

    - name: Vérifier la structure créée
      ansible.builtin.command: find {{ projet_dir }} -ls
      register: structure
      changed_when: false

    - name: Afficher la structure
      ansible.builtin.debug:
        var: structure.stdout_lines
```

</details>

<details>
<summary>Solution Exercice 3 – Modification chirurgicale avec lineinfile et blockinfile</summary>

```yaml
---
- name: Modification complète d'un fichier de configuration
  hosts: local
  gather_facts: false
  vars:
    config_file: /tmp/fichiers_demo/config/app.conf

  tasks:
    - name: Vérifier l'existence du fichier
      ansible.builtin.stat:
        path: "{{ config_file }}"
      register: stat_config

    - name: Arrêter si le fichier n'existe pas
      ansible.builtin.fail:
        msg: "Exécutez d'abord fichiers_demo.yml"
      when: not stat_config.stat.exists

    - name: Passer le niveau de log en WARNING
      ansible.builtin.lineinfile:
        path: "{{ config_file }}"
        regexp: '^niveau='
        line: "niveau=WARNING"

    - name: Activer HTTPS
      ansible.builtin.lineinfile:
        path: "{{ config_file }}"
        regexp: '^ssl='
        line: "ssl=désactivé"
        insertafter: '^port='

    - name: Ajouter la section sécurité
      ansible.builtin.blockinfile:
        path: "{{ config_file }}"
        marker: "# {mark} SECTION SÉCURITÉ"
        insertafter: EOF
        block: |
          [sécurité]
          https=true
          hsts=true
          max_tentatives_connexion=5
          délai_blocage=300
          ip_whitelist=127.0.0.1,10.0.0.0/8

    - name: Afficher le résultat final
      ansible.builtin.command: cat {{ config_file }}
      register: config_final
      changed_when: false

    - name: Montrer le fichier modifié
      ansible.builtin.debug:
        var: config_final.stdout_lines
```

</details>

<details>
<summary>Solution Exercice 4 – Template nginx_vhost.conf.j2 complet</summary>

```jinja2
# Virtual host nginx pour {{ app_name }}
# Généré automatiquement par Ansible
# Date de génération : {{ ansible_date_time.date }} à {{ ansible_date_time.time }}
# NE PAS MODIFIER MANUELLEMENT — toute modification sera écrasée

server {
    listen {{ vhost_port | default(80) }};
    server_name {{ vhost_domain }};

    root {{ vhost_root | default('/var/www/' + app_name) }};
    index index.html index.php;

{% if ssl_enabled | default(false) %}
    # Configuration SSL/TLS
    listen {{ ssl_port | default(443) }} ssl http2;
    ssl_certificate     {{ ssl_cert }};
    ssl_certificate_key {{ ssl_key }};
    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_ciphers         HIGH:!aNULL:!MD5;

    # Redirection HTTP -> HTTPS
    if ($scheme != "https") {
        return 301 https://$host$request_uri;
    }
{% endif %}

    access_log /var/log/nginx/{{ app_name }}_access.log combined;
    error_log  /var/log/nginx/{{ app_name }}_error.log warn;

    location / {
        try_files $uri $uri/ =404;
    }

{% if php_enabled | default(false) %}
    # Support PHP-FPM
    location ~ \.php$ {
        fastcgi_pass   unix:/var/run/php/php-fpm.sock;
        fastcgi_index  index.php;
        fastcgi_param  SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include        fastcgi_params;
    }

    location ~ /\.ht {
        deny all;
    }
{% endif %}
}
```

</details>
