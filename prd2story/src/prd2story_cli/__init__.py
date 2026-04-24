"""prd2story CLI — Bootstrap PRD-to-Story agent workflows into any repo."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from .banner import print_banner
from .integrations import list_integrations
from .scaffold import scaffold
from .version import __version__

app = typer.Typer(
    name="prd2story",
    help="Bootstrap PRD-to-Story agent workflows into any repository.",
    add_completion=False,
    no_args_is_help=True,
)

console = Console()


@app.command()
def init(
    target: str | None = typer.Argument(None, help="Target directory (default: current)"),
    here: bool = typer.Option(False, "--here", help="Initialize in the current directory"),
    integration: str | None = typer.Option(
        None,
        "--integration", "-i",
        help="AI assistant integration (e.g. copilot, windsurf, cursor-agent)",
    ),
    org_name: str | None = typer.Option(
        None,
        "--org",
        help="Organization/team name (replaces template placeholders)",
    ),
    jira_project: str | None = typer.Option(
        None,
        "--jira-project",
        help="Default JIRA project key",
    ),
    tech_stack: str | None = typer.Option(
        None,
        "--tech-stack",
        help="Tech stack context for story generation",
    ),
    team_size: str | None = typer.Option(
        None,
        "--team-size",
        help="Team size context",
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing files"),
    non_interactive: bool = typer.Option(
        False, "--non-interactive", "--yes", "-y",
        help="Skip interactive prompts (use defaults for missing values)",
    ),
) -> None:
    """Initialize prd2story agent workflows in a repository."""
    print_banner(console)

    # Determine target directory
    if here or target is None:
        target_dir = Path.cwd()
    else:
        target_dir = Path(target).resolve()

    # Warn if target is not empty
    if target_dir.exists() and any(target_dir.iterdir()):
        count = sum(1 for _ in target_dir.iterdir())
        console.print(
            f"[yellow]Warning:[/] Current directory is not empty ({count} items)"
        )
        console.print(
            "Template files will be merged with existing content and may overwrite existing files"
        )
        if not non_interactive:
            if not typer.confirm("Do you want to continue?"):
                console.print("[dim]Cancelled.[/]")
                raise typer.Exit(0)

    # Interactive integration selection if not provided
    if integration is None and not non_interactive:
        try:
            from .selector import select_integration

            choices = list_integrations()
            integration = select_integration(choices, console=console)
            if integration is None:
                console.print("[dim]Cancelled.[/]")
                raise typer.Exit(0)
        except (ImportError, Exception):
            # Fallback to simple prompt if readchar not available
            integration = _fallback_integration_prompt()
    elif integration is None:
        integration = "copilot"

    # Interactive prompts for missing values
    if not non_interactive:
        if org_name is None:
            org_name = typer.prompt(
                "Organization/team name",
                default="Your Organization",
            )
        if jira_project is None:
            jira_project = typer.prompt(
                "Default JIRA project key",
                default="PROJ",
            )
        if tech_stack is None:
            tech_stack = typer.prompt(
                "Tech stack (optional, press Enter to skip)",
                default="",
            )
        if team_size is None:
            team_size = typer.prompt(
                "Team size (optional, press Enter to skip)",
                default="",
            )

    # Apply defaults for non-interactive mode
    org_name = org_name or "Your Organization"
    jira_project = jira_project or "PROJ"
    tech_stack = tech_stack or ""
    team_size = team_size or ""

    # Run scaffold
    console.print()
    with console.status("[bold cyan]Scaffolding prd2story...[/]"):
        result = scaffold(
            target_dir,
            integration=integration,
            org_name=org_name,
            jira_project=jira_project,
            tech_stack=tech_stack,
            team_size=team_size,
            force=force,
        )

    # Report results
    console.print()
    console.print("[bold green]prd2story initialized successfully![/]\n")

    table = Table(title="Files Created", show_lines=False)
    table.add_column("File", style="cyan")
    for f in sorted(result["files_created"]):
        table.add_row(f)
    console.print(table)

    console.print(f"\n[bold]Integration:[/] {integration}")
    console.print(f"[bold]Organization:[/] {org_name}")
    console.print(f"[bold]JIRA Project:[/] {jira_project}")

    console.print("\n[dim]Next steps:[/]")
    console.print("  1. Add your PRD to the [cyan]prd/[/] folder")
    console.print("  2. Copy [cyan].env.example[/] to [cyan].env[/] and fill in your values")
    console.print("  3. Open your IDE and type [bold cyan]/prd2story.epic-generator[/] to start")
    console.print()


@app.command()
def version() -> None:
    """Show the prd2story version."""
    console.print(f"prd2story {__version__}")


def _fallback_integration_prompt() -> str:
    """Simple text-based integration prompt when readchar is not available."""
    choices = list_integrations()
    console.print("\n[bold]Choose your AI assistant:[/]\n")
    for i, (key, name) in enumerate(choices, 1):
        console.print(f"  {i}. {key} ({name})")
    console.print()
    while True:
        raw = typer.prompt("Enter number or name", default="1")
        # Try as number
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(choices):
                return choices[idx][0]
        except ValueError:
            pass
        # Try as name
        for key, _ in choices:
            if raw.lower() == key.lower():
                return key
        console.print("[red]Invalid choice. Try again.[/]")


def main() -> None:
    """Entry point for the CLI."""
    app()
