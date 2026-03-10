#!/usr/bin/env python3
"""
Inventaire dynamique Ansible - Script de démonstration
Ce script simule un inventaire dynamique qui pourrait interroger
une CMDB, une API cloud, ou toute autre source de données.

Utilisation :
    ./inventaire_dynamique.py --list         # Lister tous les hôtes
    ./inventaire_dynamique.py --host <nom>   # Variables d'un hôte spécifique
"""

import json
import sys
import argparse


def obtenir_inventaire():
    """Retourne l'inventaire complet au format Ansible."""

    # Simulation d'une requête vers une CMDB ou une API
    # Dans un cas réel : requests.get('https://ma-cmdb.exemple.com/api/hosts')

    return {
        "serveurs_web": {
            "hosts": ["web01.exemple.com", "web02.exemple.com"],
            "vars": {
                "http_port": 80,
                "https_port": 443,
                "serveur_logiciel": "nginx"
            }
        },
        "serveurs_bdd": {
            "hosts": ["db01.exemple.com", "db02.exemple.com"],
            "vars": {
                "bdd_port": 5432,
                "bdd_moteur": "postgresql"
            }
        },
        "equilibreurs_charge": {
            "hosts": ["lb01.exemple.com"],
            "vars": {
                "ha_active": True,
                "algorithme": "round_robin"
            }
        },
        "production": {
            "children": ["serveurs_web", "serveurs_bdd", "equilibreurs_charge"]
        },
        "local": {
            "hosts": ["localhost"],
            "vars": {
                "ansible_connection": "local"
            }
        },
        "_meta": {
            "hostvars": {
                "web01.exemple.com": {
                    "ansible_host": "192.168.1.10",
                    "ansible_user": "ubuntu",
                    "role": "frontend",
                    "zone": "eu-west-1a",
                    "etiquettes": {"Env": "production", "Equipe": "web"}
                },
                "web02.exemple.com": {
                    "ansible_host": "192.168.1.11",
                    "ansible_user": "ubuntu",
                    "role": "frontend",
                    "zone": "eu-west-1b",
                    "etiquettes": {"Env": "production", "Equipe": "web"}
                },
                "db01.exemple.com": {
                    "ansible_host": "192.168.1.20",
                    "ansible_user": "ubuntu",
                    "role": "principal",
                    "replication": "maitre",
                    "etiquettes": {"Env": "production", "Equipe": "bdd"}
                },
                "db02.exemple.com": {
                    "ansible_host": "192.168.1.21",
                    "ansible_user": "ubuntu",
                    "role": "replique",
                    "replication": "esclave",
                    "etiquettes": {"Env": "production", "Equipe": "bdd"}
                },
                "lb01.exemple.com": {
                    "ansible_host": "192.168.1.30",
                    "ansible_user": "ubuntu",
                    "role": "equilibreur",
                    "etiquettes": {"Env": "production", "Equipe": "infra"}
                },
                "localhost": {
                    "ansible_connection": "local"
                }
            }
        }
    }


def obtenir_variables_hote(nom_hote):
    """Retourne les variables d'un hôte spécifique."""
    inventaire = obtenir_inventaire()
    return inventaire.get("_meta", {}).get("hostvars", {}).get(nom_hote, {})


def main():
    parser = argparse.ArgumentParser(
        description="Inventaire dynamique Ansible - Démonstration"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Retourner l'inventaire complet"
    )
    parser.add_argument(
        "--host",
        metavar="NOM_HOTE",
        help="Retourner les variables d'un hôte spécifique"
    )

    args = parser.parse_args()

    if args.list:
        resultat = obtenir_inventaire()
        print(json.dumps(resultat, indent=2, ensure_ascii=False))
    elif args.host:
        resultat = obtenir_variables_hote(args.host)
        print(json.dumps(resultat, indent=2, ensure_ascii=False))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
