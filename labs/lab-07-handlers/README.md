# Lab 07 – Handlers

## 🎯 Objectifs

À la fin de ce lab, vous serez capable de :

- Comprendre le rôle et le fonctionnement des handlers
- Utiliser la directive `notify` pour déclencher un handler
- Grouper des handlers avec `listen`
- Forcer l'exécution immédiate des handlers avec `meta: flush_handlers`
- Exploiter l'idempotence des handlers

## 📋 Prérequis

- Labs 01–06 complétés
- Compréhension des tâches et des modules Ansible
- Notion de base sur la gestion de services système

## ⏱️ Durée estimée

45 minutes

## 🏗️ Mise en place

```bash
# Depuis la racine du dépôt
cd labs/lab-07-handlers

# Vérifier l'inventaire
cat inventory/hosts.ini

# Tester la connectivité
ansible -i inventory/hosts.ini local -m ping
```

---

## 📚 Concepts expliqués

### Qu'est-ce qu'un handler ?

Un **handler** est une tâche spéciale qui ne s'exécute que si une autre tâche l'a **notifié** (via `notify`) et seulement si cette tâche a provoqué un **changement** (statut `changed`).

Les handlers sont typiquement utilisés pour :
- Redémarrer un service après modification de sa configuration
- Recharger un pare-feu après ajout d'une règle
- Invalider un cache après déploiement

```
Tâche normale        →  changed  →  notify handler  →  handler s'exécute en fin de play
Tâche normale        →  ok       →  (handler ignoré) →  handler NE s'exécute PAS
```

**Caractéristiques clés :**
- Un handler n'est exécuté qu'**une seule fois**, même s'il est notifié plusieurs fois
- Les handlers s'exécutent **à la fin du play**, après toutes les tâches
- L'ordre d'exécution des handlers suit l'ordre de leur **déclaration**, pas l'ordre des notifications

---

### La directive `notify`

`notify` fait référence au nom d'un handler. Elle peut notifier un seul handler ou plusieurs :

```yaml
tasks:
  - name: Modifier la configuration nginx
    ansible.builtin.copy:
      src: nginx.conf
      dest: /etc/nginx/nginx.conf
    notify: Redémarrer nginx          # notifie un seul handler

  - name: Modifier le virtual host
    ansible.builtin.template:
      src: vhost.conf.j2
      dest: /etc/nginx/sites-enabled/mon-site.conf
    notify:                            # notifie plusieurs handlers
      - Redémarrer nginx
      - Notifier l'équipe ops
```

```yaml
handlers:
  - name: Redémarrer nginx
    ansible.builtin.service:
      name: nginx
      state: restarted

  - name: Notifier l'équipe ops
    ansible.builtin.debug:
      msg: "⚠️ Nginx a été redémarré, vérifiez les logs !"
```

---

### `listen` – Grouper des handlers

La directive `listen` permet à un handler de répondre à un **alias de groupe** plutôt qu'à son propre nom. Plusieurs handlers peuvent écouter le même alias :

```yaml
handlers:
  - name: Redémarrer nginx
    ansible.builtin.service:
      name: nginx
      state: restarted
    listen: "redémarrer les services web"    # écoute cet alias

  - name: Redémarrer php-fpm
    ansible.builtin.service:
      name: php-fpm
      state: restarted
    listen: "redémarrer les services web"    # écoute le même alias

tasks:
  - name: Modifier la config
    ansible.builtin.copy:
      src: config.conf
      dest: /etc/app/config.conf
    notify: "redémarrer les services web"    # déclenche les DEUX handlers
```

---

### `meta: flush_handlers` – Exécution immédiate

Par défaut, les handlers s'exécutent **à la fin du play**. Avec `meta: flush_handlers`, vous forcez leur exécution immédiate à ce point précis du playbook :

```yaml
tasks:
  - name: Déployer la configuration
    ansible.builtin.copy:
      src: app.conf
      dest: /etc/app/app.conf
    notify: Redémarrer l'application

  - name: Forcer le redémarrage maintenant
    ansible.builtin.meta: flush_handlers   # les handlers s'exécutent ici

  - name: Vérifier que l'application est opérationnelle
    ansible.builtin.uri:
      url: http://localhost:8080/health
      status_code: 200
    # Cette tâche nécessite que l'app soit déjà redémarrée
```

---

### Ordre d'exécution des handlers

```
PLAY
 ├── TASKS (exécutées dans l'ordre)
 │    ├── tâche 1  → notify: handler B
 │    ├── tâche 2  → (pas de changement, pas de notify)
 │    ├── tâche 3  → notify: handler A, handler B
 │    └── meta: flush_handlers  ← handlers exécutés ici si présent
 │         ├── handler A  (ordre de déclaration dans handlers:)
 │         └── handler B  (exécuté UNE SEULE FOIS malgré 2 notifs)
 └── HANDLERS (s'il reste des handlers non exécutés)
      └── (vide si flush_handlers a tout traité)
```

---

### Idempotence des handlers

Si une tâche ne génère **pas de changement** (statut `ok`), le handler associé **ne sera pas déclenché**. C'est l'un des comportements les plus importants à comprendre :

```yaml
# 1ère exécution : le fichier n'existe pas → changed → handler déclenché ✅
# 2ème exécution : le fichier existe déjà → ok    → handler PAS déclenché ✅
- name: Copier la configuration
  ansible.builtin.copy:
    content: "port=8080"
    dest: /etc/app.conf
  notify: Redémarrer l'application
```

---

## 🛠️ Exercices

### Exercice 1 – Handler de base avec `notify`

**Objectif** : Comprendre le déclenchement conditionnel d'un handler.

1. Exécutez le playbook de démonstration :

```bash
ansible-playbook -i inventory/hosts.ini playbooks/handlers_demo.yml
```

2. Observez l'ordre d'exécution : les handlers s'exécutent **après** les tâches normales.

3. Ré-exécutez le playbook immédiatement :

```bash
ansible-playbook -i inventory/hosts.ini playbooks/handlers_demo.yml
```

**Question** : Pourquoi les handlers ne se déclenchent-ils pas lors de la deuxième exécution ?

---

### Exercice 2 – Plusieurs `notify` vers le même handler

**Objectif** : Confirmer qu'un handler notifié plusieurs fois ne s'exécute qu'une seule fois.

Observez dans `handlers_demo.yml` que le handler « Redémarrer nginx » pourrait être notifié par plusieurs tâches. Ajoutez une deuxième tâche qui le notifie dans un nouveau playbook `playbooks/double_notify.yml` :

```yaml
---
- name: Test double notification
  hosts: local
  gather_facts: false
  vars:
    config_dir: /tmp/handlers_demo

  handlers:
    - name: Redémarrer le service
      ansible.builtin.debug:
        msg: "🔄 Redémarrage du service (exécuté une seule fois)"

  tasks:
    - name: Supprimer les configs de la démo précédente
      ansible.builtin.file:
        path: "{{ config_dir }}"
        state: absent

    - name: Recréer le répertoire
      ansible.builtin.file:
        path: "{{ config_dir }}"
        state: directory
        mode: '0755'

    - name: Première modification de config
      ansible.builtin.copy:
        content: "config_v1=true\n"
        dest: "{{ config_dir }}/config1.conf"
        mode: '0644'
      notify: Redémarrer le service

    - name: Deuxième modification de config
      ansible.builtin.copy:
        content: "config_v2=true\n"
        dest: "{{ config_dir }}/config2.conf"
        mode: '0644'
      notify: Redémarrer le service
```

Vérifiez que le handler ne s'exécute qu'**une seule fois** malgré deux notifications.

---

### Exercice 3 – Grouper des handlers avec `listen`

**Objectif** : Utiliser `listen` pour déclencher plusieurs handlers avec un seul `notify`.

Observez dans `handlers_demo.yml` comment `listen: "restart web services"` permet à plusieurs handlers de répondre à un seul alias.

Créez `playbooks/listen_demo.yml` avec trois handlers qui écoutent le même alias :

```yaml
---
- name: Démonstration de listen
  hosts: local
  gather_facts: false
  vars:
    config_dir: /tmp/handlers_demo

  handlers:
    - name: Vider le cache
      ansible.builtin.debug:
        msg: "🗑️  Cache vidé"
      listen: "redéployer l'application"

    - name: Redémarrer le worker
      ansible.builtin.debug:
        msg: "⚙️  Worker redémarré"
      listen: "redéployer l'application"

    - name: Envoyer une notification
      ansible.builtin.debug:
        msg: "📢 Déploiement notifié à l'équipe"
      listen: "redéployer l'application"

  tasks:
    - name: S'assurer que le répertoire existe
      ansible.builtin.file:
        path: "{{ config_dir }}"
        state: directory
        mode: '0755'

    - name: Déployer la nouvelle version
      ansible.builtin.copy:
        content: "version=3.0\n"
        dest: "{{ config_dir }}/version.conf"
        mode: '0644'
      notify: "redéployer l'application"
```

Vérifiez que les **trois handlers** s'exécutent avec un seul `notify`.

---

### Exercice 4 – `flush_handlers`

**Objectif** : Forcer l'exécution des handlers avant la fin du play.

1. Observez dans `handlers_demo.yml` l'utilisation de `meta: flush_handlers`.

2. Exécutez le playbook avancé pour observer l'idempotence :

```bash
# Première exécution : changed → handlers déclenchés
ansible-playbook -i inventory/hosts.ini playbooks/handlers_advanced.yml

# Deuxième exécution : ok → handlers PAS déclenchés
ansible-playbook -i inventory/hosts.ini playbooks/handlers_advanced.yml
```

3. Créez `playbooks/flush_demo.yml` pour démontrer l'utilité de `flush_handlers` :

```yaml
---
- name: Démonstration de flush_handlers
  hosts: local
  gather_facts: false
  vars:
    config_dir: /tmp/handlers_demo

  handlers:
    - name: Redémarrer le service web
      ansible.builtin.debug:
        msg: "🔄 Service web redémarré"

  tasks:
    - name: Supprimer les fichiers existants
      ansible.builtin.file:
        path: "{{ config_dir }}/web.conf"
        state: absent

    - name: Déployer la configuration web
      ansible.builtin.copy:
        content: "port=80\n"
        dest: "{{ config_dir }}/web.conf"
        mode: '0644'
      notify: Redémarrer le service web

    - name: Forcer le redémarrage maintenant
      ansible.builtin.meta: flush_handlers

    - name: Vérification post-redémarrage (simulée)
      ansible.builtin.debug:
        msg: "✅ Vérification : le service est opérationnel"

    - name: Note finale
      ansible.builtin.debug:
        msg: "Le handler a été exécuté AVANT cette tâche grâce à flush_handlers"
```

---

## ✅ Validation

```bash
# 1. Premier passage : les handlers se déclenchent
ansible-playbook -i inventory/hosts.ini playbooks/handlers_demo.yml

# 2. Deuxième passage : les handlers NE se déclenchent PAS (idempotence)
ansible-playbook -i inventory/hosts.ini playbooks/handlers_demo.yml

# 3. Vérifier l'idempotence du playbook advanced
ansible-playbook -i inventory/hosts.ini playbooks/handlers_advanced.yml
ansible-playbook -i inventory/hosts.ini playbooks/handlers_advanced.yml

# 4. Nettoyer les fichiers de démo
rm -rf /tmp/handlers_demo
```

**Critères de réussite :**
- [ ] Lors du premier passage, les handlers s'exécutent **après** les tâches normales
- [ ] Lors du deuxième passage, les handlers ne s'exécutent **pas** (pas de changement)
- [ ] Un handler notifié plusieurs fois ne s'exécute qu'**une seule fois**
- [ ] `listen` permet à plusieurs handlers de répondre à un même alias
- [ ] `meta: flush_handlers` force l'exécution des handlers à mi-play

---

## 🔍 Pour aller plus loin

- **Handlers dans les rôles** : Les handlers définis dans `roles/<role>/handlers/main.yml` sont disponibles pour toutes les tâches du rôle
- **Handlers avec `block`** : Utiliser `notify` dans des blocs de tâches
- **`force_handlers: true`** : Forcer l'exécution des handlers même si le play échoue
- **Handlers chaînés** : Un handler peut notifier un autre handler (avec précaution)

```yaml
# Forcer les handlers même en cas d'échec
- name: Mon play critique
  hosts: local
  force_handlers: true
  tasks:
    - name: ...
```

```yaml
# Handler qui notifie un autre handler
handlers:
  - name: Redémarrer nginx
    ansible.builtin.service:
      name: nginx
      state: restarted
    notify: Vérifier nginx

  - name: Vérifier nginx
    ansible.builtin.uri:
      url: http://localhost
      status_code: 200
```

---

## 💡 Solutions

<details>
<summary>Solution Exercice 2 – Double notification (handlers_demo.yml complet)</summary>

```yaml
---
- name: Test double notification
  hosts: local
  gather_facts: false
  vars:
    config_dir: /tmp/handlers_demo

  handlers:
    - name: Redémarrer le service
      ansible.builtin.debug:
        msg: "🔄 Redémarrage du service (exécuté une seule fois même avec 2 notifs)"

  tasks:
    - name: Supprimer le répertoire existant
      ansible.builtin.file:
        path: "{{ config_dir }}"
        state: absent

    - name: Créer le répertoire
      ansible.builtin.file:
        path: "{{ config_dir }}"
        state: directory
        mode: '0755'

    - name: Première modification
      ansible.builtin.copy:
        content: "config_v1=true\n"
        dest: "{{ config_dir }}/config1.conf"
        mode: '0644'
      notify: Redémarrer le service   # 1ère notification

    - name: Deuxième modification
      ansible.builtin.copy:
        content: "config_v2=true\n"
        dest: "{{ config_dir }}/config2.conf"
        mode: '0644'
      notify: Redémarrer le service   # 2ème notification (ignorée, déjà en file)

    # Le handler n'apparaît qu'UNE SEULE FOIS dans la sortie
```

</details>

<details>
<summary>Solution Exercice 3 – listen avec trois handlers</summary>

```yaml
---
- name: Démonstration complète de listen
  hosts: local
  gather_facts: false
  vars:
    config_dir: /tmp/handlers_demo
    app_version: "3.0"

  handlers:
    - name: Vider le cache applicatif
      ansible.builtin.debug:
        msg: "🗑️  Cache Redis vidé"
      listen: "redéployer l'application"

    - name: Redémarrer les workers Celery
      ansible.builtin.debug:
        msg: "⚙️  Workers Celery redémarrés (4 workers)"
      listen: "redéployer l'application"

    - name: Notifier Slack
      ansible.builtin.debug:
        msg: "📢 #ops : Déploiement v{{ app_version }} terminé avec succès"
      listen: "redéployer l'application"

  tasks:
    - name: Créer le répertoire
      ansible.builtin.file:
        path: "{{ config_dir }}"
        state: directory
        mode: '0755'

    - name: Supprimer l'ancienne version
      ansible.builtin.file:
        path: "{{ config_dir }}/version.conf"
        state: absent

    - name: Déployer la nouvelle version {{ app_version }}
      ansible.builtin.copy:
        content: "version={{ app_version }}\n"
        dest: "{{ config_dir }}/version.conf"
        mode: '0644'
      notify: "redéployer l'application"   # déclenche les 3 handlers
```

</details>

<details>
<summary>Solution Exercice 4 – flush_handlers complet</summary>

```yaml
---
- name: Démonstration flush_handlers avec vérification
  hosts: local
  gather_facts: false
  vars:
    config_dir: /tmp/handlers_demo
    service_port: 8080

  handlers:
    - name: Redémarrer le service web
      ansible.builtin.debug:
        msg: "🔄 Service web redémarré sur le port {{ service_port }}"

    - name: Recharger le proxy
      ansible.builtin.debug:
        msg: "🔄 Proxy inverse rechargé"

  tasks:
    - name: Préparer le répertoire
      ansible.builtin.file:
        path: "{{ config_dir }}"
        state: directory
        mode: '0755'

    - name: Supprimer les anciennes configs
      ansible.builtin.file:
        path: "{{ item }}"
        state: absent
      loop:
        - "{{ config_dir }}/web.conf"
        - "{{ config_dir }}/proxy.conf"

    - name: Déployer la configuration web
      ansible.builtin.copy:
        content: "port={{ service_port }}\nworkers=4\n"
        dest: "{{ config_dir }}/web.conf"
        mode: '0644'
      notify: Redémarrer le service web

    - name: Déployer la configuration proxy
      ansible.builtin.copy:
        content: "upstream=localhost:{{ service_port }}\n"
        dest: "{{ config_dir }}/proxy.conf"
        mode: '0644'
      notify: Recharger le proxy

    - name: ">>> flush_handlers : redémarrage immédiat <<<"
      ansible.builtin.meta: flush_handlers

    - name: Vérification de santé (après redémarrage)
      ansible.builtin.debug:
        msg: "✅ Le service répond sur le port {{ service_port }}"

    - name: Résumé du déploiement
      ansible.builtin.debug:
        msg: "Déploiement terminé. Handlers exécutés avant les vérifications."
```

</details>
