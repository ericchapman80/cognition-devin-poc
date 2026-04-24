"""Scaffold/init logic for prd2story.

Creates the directory structure, copies templates, and sets up
the selected integration in the target project.
"""

from __future__ import annotations

from pathlib import Path

from .config import create_config
from .integrations import get_integration
from .integrations.base import IntegrationBase

# Directories that are always created
SCAFFOLD_DIRS = [
    ".prd2story/prd",
    ".prd2story/stories/drafts",
    ".prd2story/stories/approved",
    ".prd2story/stories/created-in-jira",
    ".prd2story/stories/checklists",
    ".prd2story/stories/status",
]

# Files to copy from shared templates (relative to templates dir)
SCAFFOLD_FILES = {
    "example-prd.md": ".prd2story/prd/example-prd.md",
    "story-review-checklist.md": ".prd2story/stories/checklists/story-review-checklist.md",
    "status-readme.md": ".prd2story/stories/status/README.md",
}

GITIGNORE_ENTRIES = [
    "# prd2story",
    ".env",
    ".env.local",
    ".env.*.local",
    "*.token",
    "credentials.json",
    "secrets.json",
    ".prd2story/",
]


def scaffold(
    target_dir: Path,
    *,
    integration: str = "copilot",
    org_name: str = "Your Organization",
    jira_project: str = "PROJ",
    tech_stack: str = "",
    team_size: str = "",
    force: bool = False,
) -> dict:
    """Scaffold prd2story into the target directory.

    Returns a dict with keys: "dirs_created", "files_created", "integration".
    """
    target_dir = Path(target_dir).resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    dirs_created: list[str] = []
    files_created: list[str] = []

    # 1. Create scaffold directories
    for d in SCAFFOLD_DIRS:
        dir_path = target_dir / d
        dir_path.mkdir(parents=True, exist_ok=True)
        dirs_created.append(d)

        # Add .gitkeep to empty dirs
        gitkeep = dir_path / ".gitkeep"
        if not any(f for f in dir_path.iterdir() if f.name != ".gitkeep"):
            gitkeep.touch()
            files_created.append(f"{d}/.gitkeep")

    # 2. Copy shared template files
    templates_dir = IntegrationBase.shared_templates_dir()
    if templates_dir:
        for template_name, dest_rel in SCAFFOLD_FILES.items():
            src = templates_dir / template_name
            if src.exists():
                dst = target_dir / dest_rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                if not dst.exists() or force:
                    content = src.read_text(encoding="utf-8")
                    content = content.replace("{{ORG_NAME}}", org_name)
                    content = content.replace("{{JIRA_PROJECT}}", jira_project)
                    content = content.replace("{{TECH_STACK}}", tech_stack)
                    content = content.replace("{{TEAM_SIZE}}", team_size)
                    dst.write_text(content, encoding="utf-8")
                    files_created.append(dest_rel)

    # 3. Copy AGENTS.md into .prd2story/ (avoid conflicting with repo's own AGENTS.md)
    if templates_dir:
        agents_src = templates_dir / "agents-md-template.md"
        if agents_src.exists():
            agents_dst = target_dir / ".prd2story" / "AGENTS.md"
            agents_dst.parent.mkdir(parents=True, exist_ok=True)
            if not agents_dst.exists() or force:
                content = agents_src.read_text(encoding="utf-8")
                content = content.replace("{{ORG_NAME}}", org_name)
                content = content.replace("{{JIRA_PROJECT}}", jira_project)
                agents_dst.write_text(content, encoding="utf-8")
                files_created.append(".prd2story/AGENTS.md")

    # 4. Copy .env.example
    if templates_dir:
        env_src = templates_dir / "env-example-template.md"
        if env_src.exists():
            env_dst = target_dir / ".env.example"
            if not env_dst.exists() or force:
                content = env_src.read_text(encoding="utf-8")
                content = content.replace("{{ORG_NAME}}", org_name)
                content = content.replace("{{JIRA_PROJECT}}", jira_project)
                env_dst.write_text(content, encoding="utf-8")
                files_created.append(".env.example")

    # 5. Set up the selected integration
    integration_cls = get_integration(integration)
    integration_instance = integration_cls()
    integration_files = integration_instance.setup(target_dir, org_name=org_name)
    for f in integration_files:
        try:
            rel = f.relative_to(target_dir)
            files_created.append(str(rel))
        except ValueError:
            files_created.append(str(f))

    # 6. Update .gitignore
    _update_gitignore(target_dir)
    files_created.append(".gitignore")

    # 7. Save config
    create_config(target_dir, {
        "orgName": org_name,
        "integration": integration,
        "jiraProject": jira_project,
        "techStack": tech_stack,
        "teamSize": team_size,
    })
    files_created.append(".prd2story/init-options.json")

    return {
        "dirs_created": dirs_created,
        "files_created": files_created,
        "integration": integration,
    }


def _update_gitignore(target_dir: Path) -> None:
    """Append prd2story entries to .gitignore without duplicating."""
    gitignore_path = target_dir / ".gitignore"
    existing_lines: set[str] = set()

    if gitignore_path.exists():
        existing_content = gitignore_path.read_text(encoding="utf-8")
        existing_lines = {line.strip() for line in existing_content.splitlines()}
    else:
        existing_content = ""

    new_entries = []
    for entry in GITIGNORE_ENTRIES:
        if entry.strip() not in existing_lines:
            new_entries.append(entry)

    if new_entries:
        with open(gitignore_path, "a", encoding="utf-8") as f:
            if existing_content and not existing_content.endswith("\n"):
                f.write("\n")
            f.write("\n".join(new_entries) + "\n")
