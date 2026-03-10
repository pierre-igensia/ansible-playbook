"""
Plugin de callback personnalisé pour la formation Ansible.
Journalise les événements dans un fichier /tmp/ansible_journal.log.
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import datetime
import os

from ansible.plugins.callback import CallbackBase

DOCUMENTATION = """
    name: journal_formation
    type: notification
    short_description: Journalise les exécutions Ansible dans un fichier
    description:
        - Ce plugin enregistre les événements Ansible dans /tmp/ansible_journal.log
    requirements:
        - Accès en écriture à /tmp/
"""


class CallbackModule(CallbackBase):
    """Plugin de callback pour journaliser les exécutions."""

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = "notification"
    CALLBACK_NAME = "journal_formation"
    CALLBACK_NEEDS_ENABLED = True

    def __init__(self):
        super().__init__()
        self.log_file = os.environ.get(
            "ANSIBLE_JOURNAL_FILE", "/tmp/ansible_journal.log"
        )

    def _log(self, message):
        """Écrit un message horodaté dans le fichier de log."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")

    def v2_playbook_on_start(self, playbook):
        self._log(f"PLAYBOOK START: {playbook._file_name}")

    def v2_playbook_on_play_start(self, play):
        self._log(f"PLAY START: {play.get_name()}")

    def v2_runner_on_ok(self, result):
        host = result._host.get_name()
        task = result._task.get_name()
        changed = "CHANGED" if result._result.get("changed", False) else "OK"
        self._log(f"{changed}: {host} - {task}")

    def v2_runner_on_failed(self, result, ignore_errors=False):
        host = result._host.get_name()
        task = result._task.get_name()
        msg = result._result.get("msg", "")
        self._log(f"FAILED: {host} - {task} | {msg}")

    def v2_runner_on_skipped(self, result):
        host = result._host.get_name()
        task = result._task.get_name()
        self._log(f"SKIPPED: {host} - {task}")

    def v2_runner_on_unreachable(self, result):
        host = result._host.get_name()
        self._log(f"UNREACHABLE: {host}")

    def v2_playbook_on_stats(self, stats):
        self._log("=== RÉCAPITULATIF ===")
        hosts = sorted(stats.processed.keys())
        for host in hosts:
            summary = stats.summarize(host)
            self._log(
                f"STATS: {host} - ok={summary['ok']} "
                f"changed={summary['changed']} "
                f"failures={summary['failures']} "
                f"skipped={summary['skipped']}"
            )
        self._log("=== FIN ===\n")
