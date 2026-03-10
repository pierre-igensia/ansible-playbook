# Commandes Ansible Vault de référence

## Créer un fichier chiffré
```bash
ansible-vault create vars/nouveau_secret.yml
```

## Chiffrer un fichier existant
```bash
ansible-vault encrypt vars/secrets.yml
```

## Modifier un fichier chiffré
```bash
ansible-vault edit vars/secrets.yml
```

## Voir le contenu d'un fichier chiffré
```bash
ansible-vault view vars/secrets.yml
```

## Déchiffrer un fichier (permanent)
```bash
ansible-vault decrypt vars/secrets.yml
```

## Chiffrer une valeur individuelle
```bash
ansible-vault encrypt_string 'MonMotDePasse123' --name 'bdd_mot_de_passe'
```

## Utiliser un fichier de mot de passe
```bash
echo "mon_mot_de_passe_vault" > .vault_pass
chmod 600 .vault_pass
ansible-playbook site.yml --vault-password-file .vault_pass
```

## Utiliser plusieurs vault-id
```bash
ansible-vault create --vault-id dev@prompt vars/dev_secrets.yml
ansible-vault create --vault-id prod@/chemin/vers/fichier_pass vars/prod_secrets.yml
ansible-playbook site.yml --vault-id dev@prompt --vault-id prod@/chemin/fichier_pass
```

## Changer le mot de passe d'un vault
```bash
ansible-vault rekey vars/secrets.yml
```
