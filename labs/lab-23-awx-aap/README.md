# Lab 23 – AWX / Ansible Automation Platform

## 🎯 Objectifs

- Comprendre l'architecture d'AWX et d'Ansible Automation Platform (AAP)
- Installer AWX avec Docker Compose
- Créer des projets, inventaires et credentials dans AWX
- Configurer et lancer des job templates
- Utiliser les surveys pour paramétrer les exécutions
- Découvrir les workflow templates

## 📋 Prérequis

- Labs 01–22 complétés
- Docker et Docker Compose installés
- 4 Go de RAM minimum disponibles
- Environnement virtuel Python activé

## ⏱️ Durée estimée

120 minutes

## 🏗️ Mise en place

```bash
# Se placer dans le répertoire du lab
cd labs/lab-23-awx-aap/

# Vérifier Docker
docker --version
docker compose version

# Note : L'installation d'AWX est détaillée dans l'exercice 1
```

## 📚 Concepts expliqués

### AWX vs Ansible Automation Platform

| Aspect | AWX | AAP (Red Hat) |
|--------|-----|---------------|
| Licence | Open Source | Commercial |
| Support | Communauté | Red Hat |
| Mises à jour | Fréquentes | Stables |
| Interface | Web UI | Web UI + Hub |
| Utilisation | Dev/Lab | Production |

### Architecture AWX

```
┌─────────────────────────────────────────┐
│              AWX Web UI                  │
│          (Interface web)                 │
├──────────┬──────────┬───────────────────┤
│   API    │  RBAC    │   Notifications   │
│  REST    │ Contrôle │   (Slack, email)  │
├──────────┴──────────┴───────────────────┤
│           Task Engine                    │
│    (Exécution des playbooks)            │
├─────────────────────────────────────────┤
│     PostgreSQL    │    Redis            │
│   (Base de données) │  (Message broker) │
└─────────────────────────────────────────┘
```

### Concepts clés AWX

| Concept | Description |
|---------|-------------|
| **Organisation** | Regroupement logique d'équipes et de projets |
| **Projet** | Lien vers un dépôt Git contenant des playbooks |
| **Inventaire** | Liste des hôtes gérés |
| **Credential** | Identifiants (SSH, cloud, vault, etc.) |
| **Job Template** | Combinaison projet + inventaire + playbook + credential |
| **Survey** | Formulaire de saisie avant l'exécution |
| **Workflow** | Enchaînement conditionnel de job templates |

### API REST AWX

```bash
# Lister les job templates
curl -u admin:password https://awx.local/api/v2/job_templates/

# Lancer un job
curl -X POST -u admin:password \
  https://awx.local/api/v2/job_templates/1/launch/ \
  -H "Content-Type: application/json" \
  -d '{"extra_vars": {"env": "staging"}}'
```

## 🛠️ Exercices

### Exercice 1 – Installer AWX avec Docker

**But :** Déployer AWX localement pour le lab.

**Instructions :**

1. Examiner la documentation d'installation :
```bash
cat playbooks/install_awx.yml
```

2. L'installation d'AWX se fait via l'opérateur AWX Operator (Kubernetes) ou Docker :
```bash
# Cloner le repo AWX
git clone -b 24.0.0 https://github.com/ansible/awx.git /tmp/awx-install

# Avec Docker Compose (méthode simplifiée pour le lab)
# Voir la documentation : https://github.com/ansible/awx/blob/devel/tools/docker-compose/README.md
```

3. Accéder à l'interface web :
```
URL : http://localhost:8043
Utilisateur : admin
Mot de passe : password
```

**Résultat attendu :** AWX est accessible via le navigateur.

---

### Exercice 2 – Configurer un projet et un inventaire

**But :** Créer les ressources de base dans AWX.

**Instructions :**

1. Créer une **Organisation** :
   - Nom : `Formation`
   - Description : `Organisation de formation Ansible`

2. Créer un **Projet** :
   - Nom : `Labs Ansible`
   - Organisation : `Formation`
   - Type SCM : `Git`
   - URL SCM : URL de votre dépôt Git

3. Créer un **Inventaire** :
   - Nom : `Serveurs Lab`
   - Organisation : `Formation`
   - Ajouter un hôte : `localhost` avec `ansible_connection: local`

4. Créer un **Credential** de type `Machine` :
   - Nom : `SSH Lab`
   - Type : `Machine`

**Résultat attendu :** Les ressources sont créées dans AWX.

---

### Exercice 3 – Créer et lancer un Job Template

**But :** Exécuter un playbook depuis AWX.

**Instructions :**

1. Créer un **Job Template** :
   - Nom : `Déploiement Lab`
   - Projet : `Labs Ansible`
   - Playbook : sélectionner un playbook
   - Inventaire : `Serveurs Lab`
   - Credential : `SSH Lab`

2. Lancer le job depuis l'interface web.

3. Observer la sortie en temps réel dans la console AWX.

**Résultat attendu :** Le playbook s'exécute avec succès dans AWX.

---

### Exercice 4 – Surveys et Workflow Templates

**But :** Ajouter un formulaire de saisie et créer un workflow.

**Instructions :**

1. Ajouter un **Survey** au job template :
   - Question : "Environnement cible"
   - Type : Multiple choice
   - Options : dev, staging, production
   - Variable : `environnement`

2. Créer un **Workflow Template** :
   - Étape 1 : Vérification (succès → étape 2)
   - Étape 2 : Déploiement (succès → étape 3, échec → notification)
   - Étape 3 : Tests post-déploiement

3. Exécuter le workflow.

**Résultat attendu :** Le workflow s'exécute en enchaînant les étapes.

---

### Exercice 5 – API REST AWX

**But :** Interagir avec AWX via l'API.

**Instructions :**

1. Examiner le playbook d'API :
```bash
cat playbooks/awx_api_demo.yml
```

2. Exécuter le playbook :
```bash
ansible-playbook -i inventory/mononode.yml playbooks/awx_api_demo.yml
```

**Résultat attendu :** Les concepts d'API AWX sont compris.

## ✅ Validation

```bash
# Vérifier AWX (si installé)
curl -s http://localhost:8043/api/v2/ping/

# Sinon, exécuter la simulation
ansible-playbook -i inventory/mononode.yml playbooks/awx_api_demo.yml
```

## 🔍 Pour aller plus loin

- [Documentation AWX](https://ansible.readthedocs.io/projects/awx/en/latest/)
- [AWX Operator](https://github.com/ansible/awx-operator)
- [API AWX](https://ansible.readthedocs.io/projects/awx/en/latest/rest_api/)
- **Défi 1** : Configurez des notifications Slack/email dans AWX pour être alerté des résultats de jobs.
- **Défi 2** : Créez un workflow complet de déploiement blue/green avec validation manuelle.

## 💡 Solutions

<details>
<summary>Solution – Exercice 2 : Configuration via API</summary>

```bash
# Créer une organisation
curl -X POST -u admin:password \
  http://localhost:8043/api/v2/organizations/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Formation", "description": "Organisation de formation"}'

# Créer un projet
curl -X POST -u admin:password \
  http://localhost:8043/api/v2/projects/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Labs Ansible",
    "organization": 1,
    "scm_type": "git",
    "scm_url": "https://github.com/votre-repo/ansible-labs.git"
  }'

# Créer un inventaire
curl -X POST -u admin:password \
  http://localhost:8043/api/v2/inventories/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Serveurs Lab", "organization": 1}'
```

</details>

<details>
<summary>Solution – Exercice 5 : API REST</summary>

```bash
# Lister les job templates
curl -s -u admin:password http://localhost:8043/api/v2/job_templates/ | python3 -m json.tool

# Lancer un job avec des variables
curl -X POST -u admin:password \
  http://localhost:8043/api/v2/job_templates/1/launch/ \
  -H "Content-Type: application/json" \
  -d '{"extra_vars": {"environnement": "staging"}}'

# Vérifier le statut d'un job
curl -s -u admin:password http://localhost:8043/api/v2/jobs/1/ | python3 -m json.tool | grep status
```

</details>
