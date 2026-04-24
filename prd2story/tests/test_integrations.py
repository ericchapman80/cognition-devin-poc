"""Tests for the integration registry and individual integrations."""

import pytest

from prd2story_cli.integrations import (
    get_integration,
    list_integrations,
)
from prd2story_cli.integrations.base import IntegrationBase


class TestIntegrationRegistry:
    """Tests for the integration registry."""

    def test_list_integrations_returns_all_nine(self):
        """All 9 supported integrations should be registered."""
        integrations = list_integrations()
        keys = [k for k, _ in integrations]
        assert len(keys) == 9
        expected = {
            "amp", "claude", "codex", "copilot", "cursor-agent",
            "gemini", "kilocode", "opencode", "windsurf",
        }
        assert set(keys) == expected

    def test_list_integrations_returns_tuples(self):
        """Each entry should be a (key, display_name) tuple."""
        integrations = list_integrations()
        for key, display_name in integrations:
            assert isinstance(key, str)
            assert isinstance(display_name, str)
            assert len(key) > 0
            assert len(display_name) > 0

    def test_get_integration_valid(self):
        """get_integration should return the correct class for a valid key."""
        cls = get_integration("copilot")
        assert cls.key == "copilot"
        assert cls.display_name == "GitHub Copilot"

    def test_get_integration_invalid(self):
        """get_integration should raise KeyError for unknown keys."""
        with pytest.raises(KeyError, match="Unknown integration"):
            get_integration("nonexistent-ide")

    def test_all_integrations_inherit_from_base(self):
        """Every registered integration should be a subclass of IntegrationBase."""
        for key, _ in list_integrations():
            cls = get_integration(key)
            assert issubclass(cls, IntegrationBase)

    def test_all_integrations_have_config(self):
        """Every integration should have name, folder, commands_subdir in config."""
        for key, _ in list_integrations():
            cls = get_integration(key)
            assert "name" in cls.config
            assert "folder" in cls.config
            assert "commands_subdir" in cls.config


class TestCopilotIntegration:
    """Tests specific to GitHub Copilot integration."""

    def test_copilot_config(self):
        cls = get_integration("copilot")
        assert cls.config["folder"] == ".github"
        assert cls.config["commands_subdir"] == "agents"
        assert cls.context_file == ".github/copilot-instructions.md"

    def test_copilot_command_filename(self):
        instance = get_integration("copilot")()
        assert instance.command_filename("epic-generator") == "prd2story.epic-generator.md"


class TestWindsurfIntegration:
    """Tests specific to Windsurf integration."""

    def test_windsurf_config(self):
        cls = get_integration("windsurf")
        assert cls.config["folder"] == ".windsurf"
        assert cls.config["commands_subdir"] == "workflows"
        assert cls.context_file == ".windsurf/rules/prd2story.md"


class TestCursorIntegration:
    """Tests specific to Cursor integration."""

    def test_cursor_config(self):
        cls = get_integration("cursor-agent")
        assert cls.config["folder"] == ".cursor"
        assert cls.config["commands_subdir"] == "rules"

    def test_cursor_command_filename(self):
        instance = get_integration("cursor-agent")()
        assert instance.command_filename("epic-generator") == "prd2story.epic-generator.mdc"


class TestClaudeIntegration:
    """Tests specific to Claude Code integration."""

    def test_claude_config(self):
        cls = get_integration("claude")
        assert cls.config["folder"] == "."
        assert cls.config["commands_subdir"] == ".claude/commands"
        assert cls.context_file == "CLAUDE.md"

    def test_claude_command_filename(self):
        instance = get_integration("claude")()
        assert instance.command_filename("epic-generator") == "prd2story-epic-generator.md"


class TestGeminiIntegration:
    """Tests specific to Gemini CLI integration."""

    def test_gemini_config(self):
        cls = get_integration("gemini")
        assert cls.config["folder"] == ".gemini"
        assert cls.config["commands_subdir"] == "commands"
        assert cls.context_file == ".gemini/GEMINI.md"


class TestOpencodeIntegration:
    """Tests specific to opencode integration."""

    def test_opencode_config(self):
        cls = get_integration("opencode")
        assert cls.config["folder"] == ".opencode"
        assert cls.config["commands_subdir"] == "commands"


class TestCodexIntegration:
    """Tests specific to Codex CLI integration."""

    def test_codex_config(self):
        cls = get_integration("codex")
        assert cls.config["folder"] == ".codex"
        assert cls.config["commands_subdir"] == "commands"


class TestKilocodeIntegration:
    """Tests specific to Kilo Code integration."""

    def test_kilocode_config(self):
        cls = get_integration("kilocode")
        assert cls.config["folder"] == ".kilocode"
        assert cls.config["commands_subdir"] == "commands"


class TestAmpIntegration:
    """Tests specific to Amp integration."""

    def test_amp_config(self):
        cls = get_integration("amp")
        assert cls.config["folder"] == ".amp"
        assert cls.config["commands_subdir"] == "commands"
