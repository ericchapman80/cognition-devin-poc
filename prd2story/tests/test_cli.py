"""Tests for the CLI entry point."""

from typer.testing import CliRunner

from prd2story_cli import app

runner = CliRunner()


class TestCLIVersion:
    def test_version_command(self):
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "prd2story" in result.output


class TestCLIInit:
    def test_init_non_interactive(self, tmp_path):
        result = runner.invoke(app, [
            "init",
            str(tmp_path),
            "--integration", "copilot",
            "--org", "TestOrg",
            "--jira-project", "TEST",
            "--non-interactive",
        ])
        assert result.exit_code == 0
        assert "prd2story initialized successfully" in result.output

    def test_init_creates_files(self, tmp_path):
        runner.invoke(app, [
            "init",
            str(tmp_path),
            "--integration", "copilot",
            "--org", "TestOrg",
            "--non-interactive",
        ])
        assert (tmp_path / "AGENTS.md").exists()
        assert (tmp_path / ".env.example").exists()
        assert (tmp_path / "prd" / "example-prd.md").exists()

    def test_init_with_windsurf(self, tmp_path):
        result = runner.invoke(app, [
            "init",
            str(tmp_path),
            "--integration", "windsurf",
            "--org", "TestOrg",
            "--non-interactive",
        ])
        assert result.exit_code == 0
        assert (tmp_path / ".windsurf" / "workflows").is_dir()

    def test_init_with_cursor(self, tmp_path):
        result = runner.invoke(app, [
            "init",
            str(tmp_path),
            "--integration", "cursor-agent",
            "--org", "TestOrg",
            "--non-interactive",
        ])
        assert result.exit_code == 0
        assert (tmp_path / ".cursor" / "rules").is_dir()

    def test_init_with_claude(self, tmp_path):
        result = runner.invoke(app, [
            "init",
            str(tmp_path),
            "--integration", "claude",
            "--org", "TestOrg",
            "--non-interactive",
        ])
        assert result.exit_code == 0
        assert (tmp_path / ".claude" / "commands").is_dir()

    def test_init_invalid_integration(self, tmp_path):
        result = runner.invoke(app, [
            "init",
            str(tmp_path),
            "--integration", "nonexistent",
            "--org", "TestOrg",
            "--non-interactive",
        ])
        assert result.exit_code != 0
