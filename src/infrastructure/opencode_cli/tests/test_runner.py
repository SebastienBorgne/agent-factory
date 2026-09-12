import subprocess
from datetime import UTC, datetime
from unittest.mock import patch

from django.test import SimpleTestCase

from domain.entities import Project
from domain.value_objects import RunStatus
from infrastructure.opencode_cli.runner import OpenCodeRunner


def _project() -> Project:
    return Project(
        slug="acme",
        name="Acme",
        brief="build a thing",
        output_path="/tmp/acme",
        created_at=datetime.now(UTC),
    )


class OpenCodeRunnerTests(SimpleTestCase):
    @patch("infrastructure.opencode_cli.runner.subprocess.run")
    def test_success_maps_to_succeeded(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="all good", stderr=""
        )

        run_log = OpenCodeRunner().run_project_manager(_project())

        self.assertEqual(run_log.status, RunStatus.SUCCEEDED)
        self.assertIn("all good", run_log.log_tail)
        args, kwargs = mock_run.call_args
        self.assertEqual(args[0], ["opencode", "run", "--agent", "project-manager", "build a thing"])
        self.assertEqual(kwargs["cwd"], "/tmp/acme")

    @patch("infrastructure.opencode_cli.runner.subprocess.run")
    def test_nonzero_exit_maps_to_failed(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=1, stdout="", stderr="boom")

        run_log = OpenCodeRunner().run_project_manager(_project())

        self.assertEqual(run_log.status, RunStatus.FAILED)
        self.assertIn("boom", run_log.log_tail)

    @patch("infrastructure.opencode_cli.runner.subprocess.run")
    def test_timeout_maps_to_failed(self, mock_run):
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="opencode", timeout=1)

        run_log = OpenCodeRunner(timeout_seconds=1).run_project_manager(_project())

        self.assertEqual(run_log.status, RunStatus.FAILED)

    @patch("infrastructure.opencode_cli.runner.subprocess.run")
    def test_missing_binary_maps_to_failed(self, mock_run):
        mock_run.side_effect = FileNotFoundError("opencode not found")

        run_log = OpenCodeRunner().run_project_manager(_project())

        self.assertEqual(run_log.status, RunStatus.FAILED)
        self.assertIn("opencode not found", run_log.log_tail)
