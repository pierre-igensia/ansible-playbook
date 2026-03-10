# Lab 21 – Gestion Windows avec Ansible

## 🎯 Objectifs

- Configurer WinRM pour la communication Ansible ↔ Windows
- Utiliser les modules `win_*` pour gérer des machines Windows
- Installer des logiciels avec Chocolatey via Ansible
- Gérer les services, fonctionnalités et registre Windows
- Comprendre l'authentification Kerberos et NTLM

## 📋 Prérequis

- Labs 01–20 complétés
- Une machine Windows Server (ou Windows 10/11) accessible
- Python `pywinrm` installé (`uv pip install pywinrm`)
- WinRM activé sur la machine Windows cible

## ⏱️ Durée estimée

90 minutes

## 🏗️ Mise en place

```bash
# Activer l'environnement virtuel
source ~/ansible-venv/bin/activate

# Installer pywinrm
uv pip install pywinrm requests-credssp

# Se placer dans le répertoire du lab
cd labs/lab-21-gestion-windows/

# Sur la machine Windows cible (PowerShell en admin) :
# winrm quickconfig -force
# Enable-PSRemoting -Force
# Set-Item WSMan:\localhost\Service\AllowUnencrypted -Value $true
# Set-Item WSMan:\localhost\Service\Auth\Basic -Value $true
```

## 📚 Concepts expliqués

### Connexion Ansible → Windows

Ansible utilise **WinRM** (Windows Remote Management) au lieu de SSH pour communiquer avec Windows :

```
┌─────────────┐    WinRM (HTTP/HTTPS)    ┌─────────────┐
│  Contrôleur │ ──────────────────────── │   Windows   │
│   Ansible   │    Port 5985/5986        │   Server    │
│   (Linux)   │                          │             │
└─────────────┘                          └─────────────┘
```

### Variables de connexion Windows

```yaml
# group_vars/windows.yml
ansible_connection: winrm
ansible_winrm_transport: basic    # ou ntlm, kerberos, credssp
ansible_winrm_port: 5985          # HTTP (5986 pour HTTPS)
ansible_winrm_scheme: http
ansible_user: Administrateur
ansible_password: "{{ vault_windows_password }}"
```

### Modules Windows principaux

| Module | Description |
|--------|-------------|
| `ansible.windows.win_copy` | Copier des fichiers |
| `ansible.windows.win_file` | Gérer fichiers/répertoires |
| `ansible.windows.win_package` | Installer des packages MSI/EXE |
| `ansible.windows.win_feature` | Gérer les fonctionnalités Windows |
| `ansible.windows.win_service` | Gérer les services |
| `ansible.windows.win_user` | Gérer les utilisateurs locaux |
| `ansible.windows.win_regedit` | Modifier le registre |
| `ansible.windows.win_shell` | Exécuter des commandes PowerShell |
| `chocolatey.chocolatey.win_chocolatey` | Installer via Chocolatey |

### Inventaire Windows

```ini
[windows]
win-srv01 ansible_host=192.168.1.100
win-srv02 ansible_host=192.168.1.101

[windows:vars]
ansible_connection=winrm
ansible_winrm_transport=basic
ansible_winrm_port=5985
ansible_user=Administrateur
ansible_password=MonMotDePasse
```

## 🛠️ Exercices

### Exercice 1 – Configurer la connexion WinRM

**But :** Établir la connexion Ansible vers une machine Windows.

**Instructions :**

1. Examiner l'inventaire Windows :
```bash
cat inventory/mononode.yml
```

2. Tester la connexion (si machine Windows disponible) :
```bash
ansible windows -m ansible.windows.win_ping
```

3. Si pas de machine Windows, simuler avec le playbook local :
```bash
ansible-playbook playbooks/windows_simulation.yml
```

**Résultat attendu :** Le ping Windows répond avec `pong` ou la simulation affiche les concepts clés.

---

### Exercice 2 – Gestion de fichiers et services

**But :** Utiliser les modules `win_*` pour gérer des fichiers et services.

**Instructions :**

1. Examiner le playbook :
```bash
cat playbooks/gestion_windows.yml
```

2. Observer les modules utilisés :
   - `win_file` pour créer des répertoires
   - `win_copy` pour copier des fichiers
   - `win_service` pour gérer les services
   - `win_feature` pour installer des fonctionnalités

**Résultat attendu :** Compréhension des modules Windows et de leur syntaxe.

---

### Exercice 3 – Installation de logiciels avec Chocolatey

**But :** Utiliser Chocolatey pour installer des logiciels.

**Instructions :**

1. Examiner le playbook Chocolatey :
```bash
cat playbooks/chocolatey_demo.yml
```

2. Observer comment installer Chocolatey puis des packages :
```yaml
- name: Installer Chocolatey
  chocolatey.chocolatey.win_chocolatey:
    name: chocolatey
    state: present

- name: Installer des logiciels
  chocolatey.chocolatey.win_chocolatey:
    name: "{{ item }}"
    state: present
  loop:
    - git
    - notepadplusplus
    - 7zip
```

**Résultat attendu :** Compréhension du workflow d'installation via Chocolatey.

---

### Exercice 4 – Registre et configuration système

**But :** Modifier le registre Windows et configurer le système.

**Instructions :**

1. Examiner le playbook de configuration :
```bash
cat playbooks/registre_config.yml
```

2. Observer les modifications du registre :
```yaml
- name: Désactiver Windows Update automatique
  ansible.windows.win_regedit:
    path: HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU
    name: NoAutoUpdate
    data: 1
    type: dword
```

**Résultat attendu :** Compréhension de la gestion du registre Windows via Ansible.

## ✅ Validation

```bash
# Simuler les concepts Windows
ansible-playbook playbooks/windows_simulation.yml

# Avec une vraie machine Windows :
# ansible windows -m ansible.windows.win_ping
# ansible-playbook playbooks/gestion_windows.yml
```

## 🔍 Pour aller plus loin

- [Documentation Ansible – Windows](https://docs.ansible.com/ansible/latest/os_guide/windows_usage.html)
- [Collection ansible.windows](https://docs.ansible.com/ansible/latest/collections/ansible/windows/index.html)
- [WinRM Setup](https://docs.ansible.com/ansible/latest/os_guide/windows_winrm.html)
- **Défi 1** : Créez un rôle complet pour configurer un serveur IIS (install, site web, certificat SSL).
- **Défi 2** : Mettez en place l'authentification Kerberos entre Ansible et un domaine Active Directory.

## 💡 Solutions

<details>
<summary>Solution – Exercice 1 : Connexion WinRM</summary>

```bash
# Sur la machine Windows (PowerShell admin)
winrm quickconfig -force
Enable-PSRemoting -Force
Set-Item WSMan:\localhost\Service\AllowUnencrypted -Value $true
Set-Item WSMan:\localhost\Service\Auth\Basic -Value $true

# Vérifier
winrm get winrm/config/service

# Depuis Ansible
ansible windows -m ansible.windows.win_ping
# win-srv01 | SUCCESS => { "changed": false, "ping": "pong" }
```

</details>

<details>
<summary>Solution – Exercice 3 : Chocolatey</summary>

```yaml
---
- name: Installation via Chocolatey
  hosts: windows
  tasks:
    - name: S'assurer que Chocolatey est installé
      chocolatey.chocolatey.win_chocolatey:
        name: chocolatey
        state: present

    - name: Installer les outils de développement
      chocolatey.chocolatey.win_chocolatey:
        name: "{{ item }}"
        state: present
      loop:
        - git
        - notepadplusplus
        - 7zip
        - vscode
        - python3

    - name: Vérifier les packages installés
      ansible.windows.win_shell: choco list --local-only
      register: choco_list

    - name: Afficher les packages
      ansible.builtin.debug:
        var: choco_list.stdout_lines
```

</details>
