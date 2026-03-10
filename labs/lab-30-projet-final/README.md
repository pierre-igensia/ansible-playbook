# Lab 30 – Projet final : Application multi-tiers

## 🎯 Objectifs

- Concevoir et déployer une application multi-tiers complète avec Ansible
- Combiner tous les concepts appris (rôles, templates, vault, handlers, tags, etc.)
- Organiser un projet Ansible professionnel
- Mettre en place le monitoring et la validation post-déploiement
- Documenter et rendre le projet maintenable

## 📋 Prérequis

- **Tous les labs précédents (01–29) complétés**
- Maîtrise des rôles, templates Jinja2, handlers, tags
- Connaissance d'Ansible Vault (Lab 13)
- Environnement virtuel Python activé

## ⏱️ Durée estimée

180 minutes

## 🏗️ Mise en place

```bash
# Activer l'environnement virtuel
source ~/ansible-venv/bin/activate

# Se placer dans le répertoire du lab
cd labs/lab-30-projet-final/

# Explorer la structure du projet
tree -L 3
```

## 📚 Architecture de l'application

### Vue d'ensemble

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   NGINX     │    │   APP       │    │   BASE DE   │
│   Load      │───→│   Python    │───→│   DONNÉES   │
│   Balancer  │    │   (Flask)   │    │  (PostgreSQL)│
│   :80/:443  │    │   :8080     │    │   :5432     │
└─────────────┘    └─────────────┘    └─────────────┘
       │                  │                  │
       └──────────────────┼──────────────────┘
                          │
                 ┌─────────────┐
                 │  MONITORING │
                 │  (métriques │
                 │   & logs)   │
                 └─────────────┘
```

### Les 4 rôles

| Rôle | Description | Port |
|------|-------------|------|
| `load-balancer` | Reverse proxy NGINX | 80/443 |
| `serveur-web` | Application Flask | 8080 |
| `base-de-donnees` | PostgreSQL | 5432 |
| `monitoring` | Collecte de métriques | - |

### Structure du projet

```
lab-30-projet-final/
├── inventory/
│   ├── mononode.yml
│   ├── group_vars/
│   │   └── all.yml
│   └── host_vars/
├── playbooks/
│   ├── site.yml           ← Point d'entrée principal
│   ├── deploiement.yml    ← Déploiement complet
│   └── verification.yml   ← Tests post-déploiement
└── roles/
    ├── load-balancer/
    ├── serveur-web/
    ├── base-de-donnees/
    └── monitoring/
```

## 🛠️ Exercices

### Exercice 1 – Explorer la structure du projet

**But :** Comprendre l'organisation d'un projet Ansible professionnel.

**Instructions :**

1. Explorer la structure :
```bash
tree -L 3
```

2. Examiner l'inventaire :
```bash
cat inventory/mononode.yml
cat inventory/group_vars/all.yml
```

3. Examiner le playbook principal :
```bash
cat playbooks/site.yml
```

4. Explorer chaque rôle :
```bash
for role in roles/*/; do
  echo "=== $role ==="
  cat "${role}tasks/main.yml"
  echo ""
done
```

**Résultat attendu :** Compréhension complète de la structure et de l'organisation.

---

### Exercice 2 – Déployer l'application complète

**But :** Exécuter le déploiement multi-tiers.

**Instructions :**

1. Vérifier la syntaxe :
```bash
ansible-playbook -i inventory/mononode.yml playbooks/site.yml --syntax-check
```

2. Mode check (dry-run) :
```bash
ansible-playbook -i inventory/mononode.yml playbooks/site.yml --check
```

3. Déploiement complet :
```bash
ansible-playbook -i inventory/mononode.yml playbooks/site.yml
```

4. Vérifier les fichiers créés :
```bash
tree /tmp/projet-final/
```

**Résultat attendu :** Toute l'application est déployée avec succès.

---

### Exercice 3 – Utiliser les tags pour un déploiement partiel

**But :** Déployer uniquement certains composants.

**Instructions :**

1. Lister les tags disponibles :
```bash
ansible-playbook -i inventory/mononode.yml playbooks/site.yml --list-tags
```

2. Déployer uniquement la base de données :
```bash
ansible-playbook -i inventory/mononode.yml playbooks/site.yml --tags "database"
```

3. Déployer tout sauf le monitoring :
```bash
ansible-playbook -i inventory/mononode.yml playbooks/site.yml --skip-tags "monitoring"
```

**Résultat attendu :** Seuls les composants sélectionnés sont déployés.

---

### Exercice 4 – Exécuter la vérification post-déploiement

**But :** Valider que le déploiement est fonctionnel.

**Instructions :**

1. Examiner le playbook de vérification :
```bash
cat playbooks/verification.yml
```

2. Exécuter la vérification :
```bash
ansible-playbook -i inventory/mononode.yml playbooks/verification.yml
```

3. Consulter le rapport :
```bash
cat /tmp/projet-final/verification/rapport.txt
```

**Résultat attendu :** Toutes les vérifications passent au vert.

---

### Exercice 5 – Améliorer le projet

**But :** Ajouter des fonctionnalités au projet.

**Instructions :**

1. Ajoutez un rôle `sauvegarde` qui :
   - Crée un script de sauvegarde de la base de données
   - Configure une tâche cron pour les sauvegardes automatiques
   - Gère la rétention (suppression des anciennes sauvegardes)

2. Ajoutez un playbook `rollback.yml` qui :
   - Restaure la version précédente de l'application
   - Vérifie le bon fonctionnement après le rollback

3. Ajoutez des variables Vault pour les secrets :
   - Mot de passe de la base de données
   - Clé secrète de l'application

**Résultat attendu :** Le projet est enrichi avec des fonctionnalités professionnelles.

## ✅ Validation

```bash
# Vérifier la syntaxe
ansible-playbook -i inventory/mononode.yml playbooks/site.yml --syntax-check

# Déploiement complet
ansible-playbook -i inventory/mononode.yml playbooks/site.yml

# Vérification post-déploiement
ansible-playbook -i inventory/mononode.yml playbooks/verification.yml

# Vérifier l'idempotence
ansible-playbook -i inventory/mononode.yml playbooks/site.yml
# Aucune tâche ne doit être "changed" à la 2ème exécution

# Consulter le rapport
cat /tmp/projet-final/verification/rapport.txt
```

## 🔍 Pour aller plus loin

- [Bonnes pratiques Ansible](https://docs.ansible.com/ansible/latest/tips_tricks/ansible_tips_tricks.html)
- [Sample Ansible setup](https://docs.ansible.com/ansible/latest/tips_tricks/sample_setup.html)
- **Défi 1** : Conteneurisez l'application et déployez-la avec Docker via Ansible (utiliser la collection `community.docker`).
- **Défi 2** : Ajoutez un déploiement blue/green avec rollback automatique en cas d'échec du health check.
- **Défi 3** : Intégrez le projet dans un pipeline CI/CD complet (Lab 25) avec des tests Molecule (Lab 17).

## 💡 Solutions

<details>
<summary>Solution – Exercice 2 : Déploiement complet</summary>

```bash
# Déploiement
ansible-playbook -i inventory/mononode.yml playbooks/site.yml

# Vérification
tree /tmp/projet-final/
# /tmp/projet-final/
# ├── app/
# │   ├── app.py
# │   └── config.py
# ├── database/
# │   ├── data/
# │   └── postgresql.conf
# ├── nginx/
# │   └── nginx.conf
# └── monitoring/
#     └── collecteur.sh
```

</details>

<details>
<summary>Solution – Exercice 5 : Rôle de sauvegarde</summary>

```yaml
# roles/sauvegarde/tasks/main.yml
---
- name: Créer le répertoire de sauvegardes
  ansible.builtin.file:
    path: "{{ sauvegarde_dir }}/backups"
    state: directory
    mode: '0750'

- name: Déployer le script de sauvegarde
  ansible.builtin.template:
    src: backup.sh.j2
    dest: "{{ sauvegarde_dir }}/backup.sh"
    mode: '0750'

- name: Planifier la sauvegarde quotidienne
  ansible.builtin.cron:
    name: "Sauvegarde base de données"
    minute: "0"
    hour: "2"
    job: "{{ sauvegarde_dir }}/backup.sh >> {{ sauvegarde_dir }}/backup.log 2>&1"
```

</details>

---

**Félicitations !** Vous avez terminé les 30 labs de la formation Ansible. Vous maîtrisez maintenant Ansible du niveau débutant au niveau professionnel.
