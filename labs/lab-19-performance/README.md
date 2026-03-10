# Lab 19 – Performance et optimisation

## 🎯 Objectifs

- Configurer les `forks` pour paralléliser l'exécution
- Activer le `pipelining` pour réduire les connexions SSH
- Utiliser `async` et `poll` pour les tâches longues
- Mettre en place le cache de faits (JSON et Redis)
- Profiler l'exécution avec les plugins de callback

## 📋 Prérequis

- Labs 01–18 complétés
- Compréhension de `ansible.cfg` et des connexions SSH
- Environnement virtuel Python activé

## ⏱️ Durée estimée

75 minutes

## 🏗️ Mise en place

```bash
# Activer l'environnement virtuel
source ~/ansible-venv/bin/activate

# Se placer dans le répertoire du lab
cd labs/lab-19-performance/

# Vérifier la configuration actuelle
ansible-config dump --changed
```

## 📚 Concepts expliqués

### Forks : parallélisation

Par défaut, Ansible exécute les tâches sur **5 hôtes simultanément**. On peut augmenter cette valeur :

```ini
# ansible.cfg
[defaults]
forks = 20
```

```bash
# Ou en ligne de commande
ansible-playbook site.yml -f 20
```

> **Règle pratique** : `forks` = nombre de cœurs CPU × 2 à 4, selon la RAM disponible.

### Pipelining

Le pipelining réduit le nombre de connexions SSH en envoyant le module et son exécution dans la même session :

```ini
[ssh_connection]
pipelining = True
```

> **Prérequis** : `requiretty` doit être désactivé dans `/etc/sudoers` sur les hôtes distants.

### Async et Poll

Pour les tâches longues, `async` lance la tâche en arrière-plan :

```yaml
- name: Mise à jour longue
  ansible.builtin.apt:
    upgrade: dist
  async: 3600        # Timeout max en secondes
  poll: 0            # 0 = fire-and-forget (ne pas attendre)
  register: mise_a_jour

- name: Vérifier l'état de la mise à jour
  ansible.builtin.async_status:
    jid: "{{ mise_a_jour.ansible_job_id }}"
  register: resultat
  until: resultat.finished
  retries: 60
  delay: 10
```

| `poll` | Comportement |
|--------|-------------|
| `> 0` | Ansible vérifie toutes les N secondes |
| `= 0` | Fire-and-forget, il faut vérifier manuellement |

### Cache de faits

Évite de recolleceer les faits à chaque exécution :

```ini
# Cache JSON (fichier)
[defaults]
gathering = smart
fact_caching = jsonfile
fact_caching_connection = /tmp/ansible_facts_cache
fact_caching_timeout = 86400

# Cache Redis
[defaults]
gathering = smart
fact_caching = redis
fact_caching_connection = localhost:6379:0
fact_caching_timeout = 86400
```

### Stratégies d'exécution

```ini
[defaults]
strategy = linear     # Par défaut : toutes les tâches sur tous les hôtes en ordre
# strategy = free     # Chaque hôte avance à son propre rythme
```

### Profiling avec callback

```ini
[defaults]
callbacks_enabled = ansible.posix.profile_tasks, ansible.posix.timer
```

## 🛠️ Exercices

### Exercice 1 – Mesurer l'impact des forks

**But :** Comparer les temps d'exécution avec différentes valeurs de forks.

**Instructions :**

1. Examiner le playbook de benchmark :
```bash
cat playbooks/benchmark_forks.yml
```

2. Exécuter avec les forks par défaut (5) :
```bash
time ansible-playbook -i inventory/mononode.yml playbooks/benchmark_forks.yml -f 5
```

3. Augmenter les forks :
```bash
time ansible-playbook -i inventory/mononode.yml playbooks/benchmark_forks.yml -f 20
```

4. Comparer les temps d'exécution.

**Résultat attendu :** Avec plus de forks, l'exécution est plus rapide sur de multiples hôtes.

---

### Exercice 2 – Tâches asynchrones

**But :** Lancer des tâches longues de manière asynchrone.

**Instructions :**

1. Examiner le playbook asynchrone :
```bash
cat playbooks/async_demo.yml
```

2. Exécuter le playbook :
```bash
ansible-playbook -i inventory/mononode.yml playbooks/async_demo.yml
```

3. Observer le comportement :
   - Les tâches longues sont lancées en parallèle
   - Le playbook vérifie leur état périodiquement

**Résultat attendu :** Les tâches asynchrones se terminent avec succès après vérification.

---

### Exercice 3 – Activer le cache de faits

**But :** Configurer et utiliser le cache de faits JSON.

**Instructions :**

1. Créer le répertoire de cache :
```bash
mkdir -p /tmp/ansible_facts_cache
```

2. Examiner la configuration :
```bash
cat playbooks/cache_demo.yml
```

3. Première exécution (collecte les faits) :
```bash
time ansible-playbook -i inventory/mononode.yml playbooks/cache_demo.yml
```

4. Vérifier le cache :
```bash
ls /tmp/ansible_facts_cache/
cat /tmp/ansible_facts_cache/localhost | python3 -m json.tool | head -20
```

5. Deuxième exécution (utilise le cache, plus rapide) :
```bash
time ansible-playbook -i inventory/mononode.yml playbooks/cache_demo.yml
```

**Résultat attendu :** La deuxième exécution est plus rapide car les faits sont lus depuis le cache.

---

### Exercice 4 – Profiler avec profile_tasks

**But :** Identifier les tâches les plus lentes.

**Instructions :**

1. Activer le plugin de profiling dans `ansible.cfg` :
```ini
[defaults]
callbacks_enabled = ansible.posix.profile_tasks
```

2. Exécuter un playbook :
```bash
ANSIBLE_CALLBACKS_ENABLED=ansible.posix.profile_tasks \
ansible-playbook -i inventory/mononode.yml playbooks/benchmark_forks.yml
```

3. Observer le temps de chaque tâche dans la sortie.

**Résultat attendu :** Chaque tâche affiche son temps d'exécution ; les plus lentes sont identifiées.

## ✅ Validation

```bash
# Tester les forks
ansible-playbook -i inventory/mononode.yml playbooks/benchmark_forks.yml -f 10

# Tester async
ansible-playbook -i inventory/mononode.yml playbooks/async_demo.yml

# Tester le cache
mkdir -p /tmp/ansible_facts_cache
ansible-playbook -i inventory/mononode.yml playbooks/cache_demo.yml
ls /tmp/ansible_facts_cache/
```

## 🔍 Pour aller plus loin

- [Documentation Ansible – Performance](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_async.html)
- [Fact caching](https://docs.ansible.com/ansible/latest/plugins/cache.html)
- [Stratégies d'exécution](https://docs.ansible.com/ansible/latest/plugins/strategy.html)
- **Défi 1** : Configurez un cache Redis pour les faits et comparez les performances avec le cache JSON.
- **Défi 2** : Utilisez la stratégie `free` et observez la différence d'exécution par rapport à `linear`.

## 💡 Solutions

<details>
<summary>Solution – Exercice 2 : Tâches asynchrones</summary>

```yaml
---
- name: Démonstration async/poll
  hosts: local
  gather_facts: false
  tasks:
    - name: Simuler une tâche longue (async)
      ansible.builtin.command: sleep 5
      async: 30
      poll: 0
      register: tache_longue

    - name: Faire autre chose pendant ce temps
      ansible.builtin.debug:
        msg: "Je travaille pendant que la tâche longue s'exécute..."

    - name: Vérifier l'état de la tâche longue
      ansible.builtin.async_status:
        jid: "{{ tache_longue.ansible_job_id }}"
      register: resultat
      until: resultat.finished
      retries: 10
      delay: 2
```

</details>

<details>
<summary>Solution – Exercice 3 : Cache de faits</summary>

Ajouter dans `ansible.cfg` ou utiliser les variables d'environnement :
```bash
export ANSIBLE_GATHERING=smart
export ANSIBLE_CACHE_PLUGIN=jsonfile
export ANSIBLE_CACHE_PLUGIN_CONNECTION=/tmp/ansible_facts_cache
export ANSIBLE_CACHE_PLUGIN_TIMEOUT=86400
```

```bash
# Première exécution : collecte les faits
time ansible-playbook -i inventory/mononode.yml playbooks/cache_demo.yml

# Vérifier le cache
ls /tmp/ansible_facts_cache/

# Deuxième exécution : utilise le cache
time ansible-playbook -i inventory/mononode.yml playbooks/cache_demo.yml
```

</details>
