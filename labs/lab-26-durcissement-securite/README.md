# Lab 26 – Durcissement sécurité

## 🎯 Objectifs

- Appliquer le principe du moindre privilège avec Ansible
- Utiliser `no_log` pour protéger les données sensibles
- Configurer les stratégies `become` de manière sécurisée
- Durcir la configuration SSH des serveurs
- Automatiser les audits de sécurité avec Ansible

## 📋 Prérequis

- Labs 01–25 complétés
- Compréhension d'Ansible Vault (Lab 13)
- Notions de sécurité système Linux
- Environnement virtuel Python activé

## ⏱️ Durée estimée

90 minutes

## 🏗️ Mise en place

```bash
# Activer l'environnement virtuel
source ~/ansible-venv/bin/activate

# Se placer dans le répertoire du lab
cd labs/lab-26-durcissement-securite/
```

## 📚 Concepts expliqués

### Principe du moindre privilège

- N'utilisez `become: true` que quand c'est nécessaire (pas au niveau du play entier)
- Limitez les droits sudo des utilisateurs Ansible
- Utilisez `become_user` pour cibler un utilisateur spécifique

```yaml
# ❌ Mauvais : become sur tout le play
- hosts: webservers
  become: true
  tasks:
    - name: Lire un fichier (ne nécessite pas root)
      ansible.builtin.command: cat /etc/hostname

# ✅ Bon : become uniquement là où c'est nécessaire
- hosts: webservers
  tasks:
    - name: Lire un fichier
      ansible.builtin.command: cat /etc/hostname

    - name: Installer un paquet (nécessite root)
      ansible.builtin.apt:
        name: nginx
      become: true
```

### no_log : protéger les données sensibles

```yaml
- name: Configurer le mot de passe de la base de données
  ansible.builtin.template:
    src: db.conf.j2
    dest: /etc/app/db.conf
  no_log: true  # Les variables ne seront pas affichées dans les logs

- name: Créer un utilisateur
  ansible.builtin.user:
    name: deploiement
    password: "{{ mot_de_passe_hash }}"
  no_log: true
```

### Durcissement SSH

```yaml
# Paramètres SSH recommandés
PermitRootLogin: "no"
PasswordAuthentication: "no"
PubkeyAuthentication: "yes"
MaxAuthTries: 3
LoginGraceTime: 30
X11Forwarding: "no"
AllowTcpForwarding: "no"
Protocol: 2
```

### Bonnes pratiques de sécurité Ansible

| Pratique | Description |
|----------|-------------|
| `no_log: true` | Masquer les données sensibles |
| Ansible Vault | Chiffrer les fichiers de secrets |
| `become` ciblé | Élévation de privilèges minimale |
| SSH par clé | Pas de mot de passe SSH |
| Audit trail | Journaliser les exécutions |
| Idempotence | Éviter les états incohérents |

## 🛠️ Exercices

### Exercice 1 – Utiliser no_log et become ciblé

**But :** Appliquer les bonnes pratiques de sécurité dans les playbooks.

**Instructions :**

1. Examiner le playbook de durcissement :
```bash
cat playbooks/bonnes_pratiques.yml
```

2. Exécuter le playbook :
```bash
ansible-playbook playbooks/bonnes_pratiques.yml
```

3. Observer que les tâches `no_log` ne montrent pas les valeurs.

**Résultat attendu :** Les données sensibles sont masquées dans la sortie.

---

### Exercice 2 – Durcir la configuration SSH

**But :** Automatiser le durcissement SSH avec Ansible.

**Instructions :**

1. Examiner le template SSH :
```bash
cat templates/sshd_config.j2
```

2. Examiner le playbook de durcissement SSH :
```bash
cat playbooks/durcissement_ssh.yml
```

3. Observer les paramètres de sécurité appliqués.

**Résultat attendu :** Compréhension de la configuration SSH sécurisée.

---

### Exercice 3 – Audit de sécurité automatisé

**But :** Créer un playbook d'audit de sécurité.

**Instructions :**

1. Examiner le playbook d'audit :
```bash
cat playbooks/audit_securite.yml
```

2. Exécuter l'audit :
```bash
ansible-playbook playbooks/audit_securite.yml
```

3. Consulter le rapport :
```bash
cat /tmp/audit_securite/rapport.txt
```

**Résultat attendu :** Un rapport d'audit liste les vérifications effectuées.

---

### Exercice 4 – Durcissement système

**But :** Appliquer des règles de sécurité système.

**Instructions :**

1. Examiner le playbook de durcissement système :
```bash
cat playbooks/durcissement_systeme.yml
```

2. Observer les vérifications :
   - Permissions de fichiers sensibles
   - Paramètres sysctl
   - Services inutiles désactivés
   - Politique de mots de passe

**Résultat attendu :** Compréhension des points de durcissement système.

## ✅ Validation

```bash
# Exécuter les bonnes pratiques
ansible-playbook playbooks/bonnes_pratiques.yml

# Exécuter l'audit
ansible-playbook playbooks/audit_securite.yml
cat /tmp/audit_securite/rapport.txt
```

## 🔍 Pour aller plus loin

- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks)
- [Ansible Hardening Role](https://github.com/openstack/ansible-hardening)
- [STIG Ansible](https://public.cyber.mil/stigs/)
- **Défi 1** : Créez un rôle de durcissement complet basé sur les CIS Benchmarks pour Ubuntu/Debian.
- **Défi 2** : Intégrez OpenSCAP avec Ansible pour générer des rapports de conformité automatisés.

## 💡 Solutions

<details>
<summary>Solution – Exercice 1 : no_log et become</summary>

```yaml
---
- name: Bonnes pratiques de sécurité
  hosts: local
  gather_facts: true
  tasks:
    - name: Créer un mot de passe (masqué)
      ansible.builtin.set_fact:
        mot_de_passe_app: "SuperSecret123!"
      no_log: true

    - name: Afficher un message (le mot de passe n'apparaît pas)
      ansible.builtin.debug:
        msg: "Configuration terminée"

    # La tâche suivante nécessiterait become sur un vrai serveur
    # - name: Installer un paquet
    #   ansible.builtin.apt:
    #     name: fail2ban
    #   become: true
```

</details>

<details>
<summary>Solution – Exercice 3 : Audit</summary>

```bash
ansible-playbook playbooks/audit_securite.yml
cat /tmp/audit_securite/rapport.txt
# === Rapport d'audit de sécurité ===
# Date : 2024-01-15T14:30:00
# Hôte : localhost
# ✅ Permissions /etc/passwd : 644
# ✅ Permissions /etc/shadow : 640
# ✅ SSH PermitRootLogin vérifié
# ...
```

</details>
