"""Tests for the scaffold/init module."""

import json

from prd2story_cli.scaffold import SCAFFOLD_DIRS, scaffold


class TestScaffoldDirectories:
    """Tests for directory creation."""

    def test_creates_all_scaffold_dirs(self, tmp_path):
        scaffold(tmp_path, integration="copilot", org_name="TestOrg")
        for d in SCAFFOLD_DIRS:
            assert (tmp_path / d).is_dir(), f"Directory {d} was not created"

    def test_creates_gitkeep_in_empty_dirs(self, tmp_path):
        scaffold(tmp_path, integration="copilot", org_name="TestOrg")
        for d in SCAFFOLD_DIRS:
            dir_path = tmp_path / d
            if dir_path.is_dir():
                files = list(dir_path.iterdir())
                # Should have at least .gitkeep or content
                assert len(files) > 0


class TestScaffoldFiles:
    """Tests for file creation."""

    def test_creates_agents_md(self, tmp_path):
        scaffold(tmp_path, integration="copilot", org_name="TestOrg")
        assert (tmp_path / "AGENTS.md").exists()

    def test_agents_md_has_org_name(self, tmp_path):
        scaffold(tmp_path, integration="copilot", org_name="Acme Corp")
        content = (tmp_path / "AGENTS.md").read_text()
        assert "Acme Corp" in content
        assert "{{ORG_NAME}}" not in content

    def test_creates_env_example(self, tmp_path):
        scaffold(tmp_path, integration="copilot", org_name="TestOrg", jira_project="TEST")
        assert (tmp_path / ".env.example").exists()

    def test_env_example_has_jira_project(self, tmp_path):
        scaffold(tmp_path, integration="copilot", org_name="TestOrg", jira_project="MYPROJ")
        content = (tmp_path / ".env.example").read_text()
        assert "MYPROJ" in content
        assert "{{JIRA_PROJECT}}" not in content

    def test_creates_example_prd(self, tmp_path):
        scaffold(tmp_path, integration="copilot", org_name="TestOrg")
        assert (tmp_path / "prd" / "example-prd.md").exists()

    def test_creates_config(self, tmp_path):
        scaffold(tmp_path, integration="copilot", org_name="TestOrg")
        config_path = tmp_path / ".prd2story" / "init-options.json"
        assert config_path.exists()
        data = json.loads(config_path.read_text())
        assert data["orgName"] == "TestOrg"
        assert data["integration"] == "copilot"


class TestScaffoldIntegrations:
    """Tests for integration-specific file creation."""

    def test_copilot_creates_agents_dir(self, tmp_path):
        scaffold(tmp_path, integration="copilot", org_name="TestOrg")
        agents_dir = tmp_path / ".github" / "agents"
        assert agents_dir.is_dir()

    def test_copilot_creates_command_files(self, tmp_path):
        scaffold(tmp_path, integration="copilot", org_name="TestOrg")
        agents_dir = tmp_path / ".github" / "agents"
        expected_files = [
            "prd2story.epic-generator.md",
            "prd2story.story-generator.md",
            "prd2story.story-reviewer.md",
            "prd2story.jira-creator.md",
        ]
        for fname in expected_files:
            assert (agents_dir / fname).exists(), f"Missing {fname}"

    def test_copilot_creates_instructions(self, tmp_path):
        scaffold(tmp_path, integration="copilot", org_name="TestOrg")
        assert (tmp_path / ".github" / "copilot-instructions.md").exists()

    def test_windsurf_creates_workflows_dir(self, tmp_path):
        scaffold(tmp_path, integration="windsurf", org_name="TestOrg")
        workflows_dir = tmp_path / ".windsurf" / "workflows"
        assert workflows_dir.is_dir()

    def test_windsurf_creates_rules(self, tmp_path):
        scaffold(tmp_path, integration="windsurf", org_name="TestOrg")
        assert (tmp_path / ".windsurf" / "rules" / "prd2story.md").exists()

    def test_cursor_creates_rules_dir(self, tmp_path):
        scaffold(tmp_path, integration="cursor-agent", org_name="TestOrg")
        rules_dir = tmp_path / ".cursor" / "rules"
        assert rules_dir.is_dir()

    def test_cursor_uses_mdc_extension(self, tmp_path):
        scaffold(tmp_path, integration="cursor-agent", org_name="TestOrg")
        rules_dir = tmp_path / ".cursor" / "rules"
        mdc_files = list(rules_dir.glob("*.mdc"))
        assert len(mdc_files) > 0

    def test_claude_creates_commands_dir(self, tmp_path):
        scaffold(tmp_path, integration="claude", org_name="TestOrg")
        commands_dir = tmp_path / ".claude" / "commands"
        assert commands_dir.is_dir()

    def test_claude_creates_context_file(self, tmp_path):
        scaffold(tmp_path, integration="claude", org_name="TestOrg")
        assert (tmp_path / "CLAUDE.md").exists()

    def test_gemini_creates_commands_dir(self, tmp_path):
        scaffold(tmp_path, integration="gemini", org_name="TestOrg")
        commands_dir = tmp_path / ".gemini" / "commands"
        assert commands_dir.is_dir()


class TestTemplateSubstitution:
    """Tests for template variable replacement."""

    def test_org_name_replaced_in_commands(self, tmp_path):
        scaffold(tmp_path, integration="copilot", org_name="Acme Corp")
        agents_dir = tmp_path / ".github" / "agents"
        for f in agents_dir.glob("*.md"):
            content = f.read_text()
            assert "{{ORG_NAME}}" not in content

    def test_org_name_replaced_in_instructions(self, tmp_path):
        scaffold(tmp_path, integration="copilot", org_name="Acme Corp")
        content = (tmp_path / ".github" / "copilot-instructions.md").read_text()
        assert "Acme Corp" in content
        assert "{{ORG_NAME}}" not in content


class TestGitignore:
    """Tests for .gitignore handling."""

    def test_creates_gitignore(self, tmp_path):
        scaffold(tmp_path, integration="copilot", org_name="TestOrg")
        assert (tmp_path / ".gitignore").exists()

    def test_gitignore_has_env_entry(self, tmp_path):
        scaffold(tmp_path, integration="copilot", org_name="TestOrg")
        content = (tmp_path / ".gitignore").read_text()
        assert ".env" in content

    def test_gitignore_no_duplicates(self, tmp_path):
        # Run scaffold twice
        scaffold(tmp_path, integration="copilot", org_name="TestOrg")
        scaffold(tmp_path, integration="copilot", org_name="TestOrg", force=True)
        content = (tmp_path / ".gitignore").read_text()
        # Count occurrences of .env (exact line match)
        lines = [line.strip() for line in content.splitlines()]
        assert lines.count(".env") == 1

    def test_gitignore_appends_to_existing(self, tmp_path):
        existing = "node_modules/\n.DS_Store\n"
        (tmp_path / ".gitignore").write_text(existing)
        scaffold(tmp_path, integration="copilot", org_name="TestOrg")
        content = (tmp_path / ".gitignore").read_text()
        assert "node_modules/" in content
        assert ".env" in content


class TestIdempotency:
    """Tests for safe re-running of scaffold."""

    def test_scaffold_twice_does_not_error(self, tmp_path):
        scaffold(tmp_path, integration="copilot", org_name="TestOrg")
        scaffold(tmp_path, integration="copilot", org_name="TestOrg", force=True)

    def test_scaffold_preserves_existing_files_without_force(self, tmp_path):
        scaffold(tmp_path, integration="copilot", org_name="TestOrg")
        # Modify AGENTS.md
        agents_path = tmp_path / "AGENTS.md"
        agents_path.write_text("custom content")
        # Re-scaffold without force
        scaffold(tmp_path, integration="copilot", org_name="TestOrg")
        assert agents_path.read_text() == "custom content"

    def test_scaffold_overwrites_with_force(self, tmp_path):
        scaffold(tmp_path, integration="copilot", org_name="TestOrg")
        agents_path = tmp_path / "AGENTS.md"
        agents_path.write_text("custom content")
        scaffold(tmp_path, integration="copilot", org_name="TestOrg", force=True)
        assert agents_path.read_text() != "custom content"


class TestReturnValue:
    """Tests for the return dict from scaffold."""

    def test_returns_dirs_created(self, tmp_path):
        result = scaffold(tmp_path, integration="copilot", org_name="TestOrg")
        assert "dirs_created" in result
        assert len(result["dirs_created"]) > 0

    def test_returns_files_created(self, tmp_path):
        result = scaffold(tmp_path, integration="copilot", org_name="TestOrg")
        assert "files_created" in result
        assert len(result["files_created"]) > 0

    def test_returns_integration(self, tmp_path):
        result = scaffold(tmp_path, integration="windsurf", org_name="TestOrg")
        assert result["integration"] == "windsurf"
