# Lab 28 – Bonnes pratiques à grande échelle

## 🎯 Objectifs

- Configurer les mises à jour progressives (rolling updates) avec `serial`
- Utiliser `max_fail_percentage` pour limiter l'impact des échecs
- Comprendre les stratégies d'exécution (`linear`, `free`, `debug`)
- Organiser l'inventaire pour des infrastructures larges
- Appliquer les bonnes pratiques de structuration de projet Ansible

## 📋 Prérequis

- Labs 01–27 complétés
- Compréhension des rôles, inventaires et playbooks
- Environnement virtuel Python activé

## ⏱️ Durée estimée

90 minutes

## 🏗️ Mise en place

```bash
# Activer l'environnement virtuel
source ~/ansible-venv/bin/activate

# Se placer dans le répertoire du lab
cd labs/lab-28-grande-echelle/
```

## 📚 Concepts expliqués

### Rolling updates avec serial

Déploiement progressif pour éviter les interruptions de service :

```yaml
- hosts: webservers
  serial: 2              # 2 serveurs à la fois
  # ou
  serial: "25%"          # 25% des serveurs à la fois
  # ou
  serial: [1, 5, "100%"] # 1 puis 5 puis tous les restants
  tasks:
    - name: Déployer l'application
      ...
```

### max_fail_percentage

Arrête le déploiement si trop de serveurs échouent :

```yaml
- hosts: webservers
  serial: 5
  max_fail_percentage: 30   # Arrêter si >30% échouent
```

### Stratégies d'exécution

| Stratégie | Comportement |
|-----------|-------------|
| `linear` (défaut) | Chaque tâche est exécutée sur tous les hôtes avant de passer à la suivante |
| `free` | Chaque hôte avance à son propre rythme |
| `debug` | Mode interactif pour le débogage |

```yaml
- hosts: all
  strategy: free    # Les hôtes rapides n'attendent pas les lents
```

### Organisation de l'inventaire à grande échelle

```
inventaire/
├── production/
│   ├── hosts.yml           # Hôtes de production
│   ├── group_vars/
│   │   ├── all.yml         # Variables globales
│   │   ├── webservers.yml  # Variables web
│   │   └── databases.yml   # Variables DB
│   └── host_vars/
│       ├── web01.yml
│       └── db01.yml
├── staging/
│   ├── hosts.yml
│   └── group_vars/
└── development/
    ├── hosts.yml
    └── group_vars/
```

### Structure de projet recommandée

```
projet/
├── ansible.cfg
├── requirements.yml         # Collections et rôles
├── site.yml                 # Point d'entrée
├── playbooks/
│   ├── webservers.yml
│   ├── databases.yml
│   └── monitoring.yml
├── roles/
│   ├── common/
│   ├── webserver/
│   └── database/
├── inventaire/
│   ├── production/
│   └── staging/
├── group_vars/
│   └── all/
│       ├── vars.yml
│       └── vault.yml
└── files/
```

### Throttle : limiter la concurrence par tâche

```yaml
- name: Redémarrer le service (2 à la fois max)
  ansible.builtin.service:
    name: nginx
    state: restarted
  throttle: 2
```

## 🛠️ Exercices

### Exercice 1 – Rolling updates avec serial

**But :** Simuler un déploiement progressif.

**Instructions :**

1. Examiner le playbook :
```bash
cat playbooks/rolling_update.yml
```

2. Exécuter le playbook :
```bash
ansible-playbook -i inventory/mononode.yml playbooks/rolling_update.yml
```

3. Observer l'exécution par lots.

**Résultat attendu :** Les hôtes sont traités par groupes successifs.

---

### Exercice 2 – Stratégies d'exécution

**But :** Comparer les stratégies `linear` et `free`.

**Instructions :**

1. Examiner le playbook :
```bash
cat playbooks/strategies_demo.yml
```

2. Exécuter avec la stratégie linear :
```bash
ansible-playbook -i inventory/mononode.yml playbooks/strategies_demo.yml
```

3. Observer les différences de comportement.

**Résultat attendu :** Compréhension des différences entre stratégies.

---

### Exercice 3 – Organisation de l'inventaire

**But :** Structurer un inventaire pour une large infrastructure.

**Instructions :**

1. Examiner la structure de l'inventaire :
```bash
tree inventory/
cat inventory/mononode.yml
cat inventory/group_vars/all.yml
```

2. Exécuter le playbook d'inventaire :
```bash
ansible-playbook -i inventory/mononode.yml playbooks/inventaire_demo.yml
```

**Résultat attendu :** L'inventaire est structuré et les variables sont correctement héritées.

## ✅ Validation

```bash
# Rolling update
ansible-playbook -i inventory/mononode.yml playbooks/rolling_update.yml

# Stratégies
ansible-playbook -i inventory/mononode.yml playbooks/strategies_demo.yml

# Inventaire
ansible-playbook -i inventory/mononode.yml playbooks/inventaire_demo.yml
```

## 🔍 Pour aller plus loin

- [Documentation Ansible – Stratégies](https://docs.ansible.com/ansible/latest/plugins/strategy.html)
- [Rolling updates](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_delegation.html#rolling-update-batch-size)
- [Best practices](https://docs.ansible.com/ansible/latest/tips_tricks/ansible_tips_tricks.html)
- **Défi 1** : Mettez en place un déploiement blue/green avec `serial` et des health checks entre chaque lot.
- **Défi 2** : Créez une structure de projet multi-environnements (dev, staging, prod) avec des variables spécifiques à chaque environnement.

## 💡 Solutions

<details>
<summary>Solution – Exercice 1 : Rolling update</summary>

```yaml
---
- name: Déploiement progressif
  hosts: local
  serial: 1
  tasks:
    - name: Retirer du load balancer
      ansible.builtin.debug:
        msg: "Retrait de {{ inventory_hostname }} du pool"

    - name: Déployer la mise à jour
      ansible.builtin.debug:
        msg: "Déploiement sur {{ inventory_hostname }}"

    - name: Vérifier la santé
      ansible.builtin.debug:
        msg: "Health check OK pour {{ inventory_hostname }}"

    - name: Réinsérer dans le load balancer
      ansible.builtin.debug:
        msg: "Réinsertion de {{ inventory_hostname }} dans le pool"
```

</details>
