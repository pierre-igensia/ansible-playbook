# Lab 12 – Gestion des Erreurs

## 🎯 Objectifs
- Utiliser `ignore_errors` pour continuer malgré une erreur
- Définir des conditions d'échec personnalisées avec `failed_when`
- Structurer le code avec `block`, `rescue` et `always`
- Comprendre `any_errors_fatal` et `max_fail_percentage`

## 📋 Prérequis
- Labs 01–11 complétés

## ⏱️ Durée estimée
60 minutes

## 🏗️ Mise en place
1. Activer l'environnement virtuel : `source .venv/bin/activate`
2. Se placer dans `labs/lab-12-gestion-erreurs/`

## 📚 Concepts expliqués

### ignore_errors
```yaml
- name: Commande qui peut échouer
  ansible.builtin.command: /usr/bin/peut-echouer
  ignore_errors: true
```
⚠️ À utiliser avec précaution — masque les erreurs réelles.

### failed_when
```yaml
- name: Échec personnalisé
  ansible.builtin.command: vérifier_statut
  register: résultat
  failed_when: "'ERREUR' in résultat.stdout or résultat.rc > 1"
```

### changed_when
```yaml
- name: Commande idempotente
  ansible.builtin.command: echo "ok"
  changed_when: false  # Ne jamais marquer comme changed
```

### block / rescue / always
```yaml
- block:
    - name: Tâche qui peut échouer
      # ...
  rescue:
    - name: Gestion de l'erreur
      # ...
  always:
    - name: Toujours exécutée (comme finally en Python)
      # ...
```

### any_errors_fatal
```yaml
- hosts: all
  any_errors_fatal: true  # Arrête tout si un hôte échoue
```

## 🛠️ Exercices

### Exercice 1 – ignore_errors et failed_when
**But :** Maîtriser les conditions d'échec personnalisées.

### Exercice 2 – block / rescue / always
**But :** Implémenter une gestion d'erreur robuste.

### Exercice 3 – Rollback automatique
**But :** Créer un mécanisme de rollback en cas d'erreur de déploiement.

### Exercice 4 – changed_when pour l'idempotence
**But :** Corriger des faux "changed" avec changed_when.

## ✅ Validation
```bash
ansible-playbook playbooks/gestion_erreurs.yml
ansible-playbook playbooks/block_rescue.yml
ansible-playbook playbooks/déploiement_sécurisé.yml
```

## 🔍 Pour aller plus loin
- [Documentation sur la gestion des erreurs](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_error_handling.html)
- **Défi 1** : Créer un playbook de déploiement avec rollback automatique sur 3 serveurs
- **Défi 2** : Implémenter un système d'alerte par email en cas d'échec (module `mail`)

## 💡 Solutions
<details>
<summary>Solution</summary>

### Solution Exercice 1
```yaml
- name: Vérifier le statut d'un service
  ansible.builtin.command: systemctl is-active nginx
  register: statut_nginx
  failed_when: statut_nginx.rc not in [0, 3]
  changed_when: false
```

### Solution Exercice 2
```yaml
- block:
    - name: Déployer la nouvelle version
      ansible.builtin.copy:
        src: app_v2.tar.gz
        dest: /tmp/
  rescue:
    - name: Restaurer l'ancienne version
      ansible.builtin.debug:
        msg: "Restauration de l'ancienne version..."
  always:
    - name: Envoyer le rapport
      ansible.builtin.debug:
        msg: "Déploiement terminé (succès ou échec)"
```
</details>
