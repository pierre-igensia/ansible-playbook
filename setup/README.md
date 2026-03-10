# Guide d'installation et de configuration

Ce guide vous accompagne pas à pas pour préparer votre environnement de développement avant de commencer les labs Ansible.

---

## 1. Prérequis

| Outil | Version minimale | Vérification |
|-------|-----------------|--------------|
| Python | **3.11+** | `python3 --version` |
| `uv` | dernière version | `uv --version` |
| Git | 2.x | `git --version` |
| Docker *(labs 17+)* | 20.10+ | `docker --version` |

### Installer `uv`

`uv` est un gestionnaire de paquets Python ultra-rapide (remplaçant de `pip` + `venv`). Installez-le avec la commande suivante :

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Rechargez ensuite votre shell pour que la commande `uv` soit disponible :

```bash
source ~/.bashrc   # ou ~/.zshrc selon votre shell
```

---

## 2. Créer et activer un environnement virtuel

Depuis la racine du dépôt, créez un environnement virtuel isolé :

```bash
uv venv .venv
```

Activez l'environnement :

```bash
# Linux / macOS
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\activate
```

> ✅ Votre invite de commande doit afficher `(.venv)` pour confirmer que l'environnement est bien actif.

---

## 3. Installer Ansible et les outils complémentaires

Installez Ansible ainsi que tous les outils nécessaires aux labs en une seule commande :

```bash
uv pip install ansible ansible-lint molecule molecule-plugins[docker] pytest-testinfra
```

| Paquet | Rôle |
|--------|------|
| `ansible` | Moteur principal d'automatisation |
| `ansible-lint` | Analyse statique des playbooks YAML |
| `molecule` | Framework de test pour les rôles Ansible |
| `molecule-plugins[docker]` | Pilote Docker pour Molecule |
| `pytest-testinfra` | Tests d'infrastructure avec pytest |

---

## 4. Vérifier l'installation

Contrôlez que tout est correctement installé :

```bash
ansible --version
```

Vous devriez obtenir une sortie similaire à :

```
ansible [core 2.1x.x]  # version stable la plus récente
  config file = /chemin/vers/le/depot/ansible.cfg
  configured module search path = [...]
  ansible python module location = ...
  ansible collection location = ...
  executable location = .venv/bin/ansible
  python version = 3.11.x
  jinja version = 3.x.x
  libyaml = True
```

Vérifiez également les autres outils :

```bash
ansible-lint --version
molecule --version
```

---

## 5. Configurer `ansible.cfg`

Un fichier `ansible.cfg` est fourni à la racine du dépôt avec des paramètres optimisés pour les labs. Ansible le détecte automatiquement lorsque vous lancez des commandes depuis ce répertoire.

```ini
[defaults]
inventory         = ./inventory
roles_path        = ./roles
stdout_callback   = yaml
interpreter_python = auto_silent
host_key_checking = False
retry_files_enabled = False

[ssh_connection]
pipelining = True
```

> ⚠️ Ne versionnez jamais de mots de passe ou de clés privées dans ce fichier. Utilisez **Ansible Vault** (lab-13) ou un gestionnaire de secrets (lab-27) pour sécuriser vos informations sensibles.

---

## 6. Conseils : épingler les dépendances avec `uv pip compile`

Pour garantir des environnements reproductibles (indispensable en CI/CD), épinglez les versions exactes de vos dépendances :

```bash
# Générer un fichier requirements.in avec vos dépendances de haut niveau
cat > requirements.in << EOF
ansible
ansible-lint
molecule
molecule-plugins[docker]
pytest-testinfra
EOF

# Compiler les dépendances avec leurs versions exactes
uv pip compile requirements.in -o requirements.txt

# Installer depuis le fichier verrouillé
uv pip install -r requirements.txt
```

> 💡 Commitez `requirements.in` **et** `requirements.txt` dans le dépôt afin que tous les contributeurs utilisent exactement les mêmes versions.

---

## 🎯 Prochaine étape

Une fois votre environnement prêt, commencez par le premier lab :

👉 **[Lab 01 – Premiers pas avec Ansible](../labs/lab-01-premiers-pas/)**
