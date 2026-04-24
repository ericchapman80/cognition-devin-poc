"""Tests for the configuration module."""

import json

from prd2story_cli.config import create_config, get_defaults, load_config


class TestGetDefaults:
    def test_returns_expected_keys(self):
        defaults = get_defaults()
        assert "orgName" in defaults
        assert "integration" in defaults
        assert "jiraProject" in defaults

    def test_default_values(self):
        defaults = get_defaults()
        assert defaults["orgName"] == "Your Organization"
        assert defaults["integration"] == "copilot"
        assert defaults["jiraProject"] == "PROJ"


class TestCreateConfig:
    def test_creates_config_file(self, tmp_path):
        create_config(tmp_path, {"orgName": "TestOrg"})
        config_path = tmp_path / ".prd2story" / "init-options.json"
        assert config_path.exists()

    def test_config_content(self, tmp_path):
        create_config(tmp_path, {"orgName": "TestOrg", "integration": "windsurf"})
        config_path = tmp_path / ".prd2story" / "init-options.json"
        data = json.loads(config_path.read_text())
        assert data["orgName"] == "TestOrg"
        assert data["integration"] == "windsurf"

    def test_merges_with_defaults(self, tmp_path):
        create_config(tmp_path, {"orgName": "TestOrg"})
        config_path = tmp_path / ".prd2story" / "init-options.json"
        data = json.loads(config_path.read_text())
        assert data["jiraProject"] == "PROJ"  # default

    def test_strips_internal_keys(self, tmp_path):
        create_config(tmp_path, {"orgName": "TestOrg", "force": True, "here": True})
        config_path = tmp_path / ".prd2story" / "init-options.json"
        data = json.loads(config_path.read_text())
        assert "force" not in data
        assert "here" not in data


class TestLoadConfig:
    def test_load_existing_config(self, tmp_path):
        create_config(tmp_path, {"orgName": "TestOrg"})
        loaded = load_config(tmp_path)
        assert loaded is not None
        assert loaded["orgName"] == "TestOrg"

    def test_load_nonexistent_config(self, tmp_path):
        loaded = load_config(tmp_path)
        assert loaded is None
