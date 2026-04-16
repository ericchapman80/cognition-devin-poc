"""CLI entry point for the college guide multi-agent workflow."""

import json
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from college_guide.config import AppConfig
from college_guide.models import StudentProfile
from college_guide.orchestrator import OrchestratorAgent
from trading_agents.llm.provider import LLMProvider

console = Console()


def load_student_profile(profile_path: str) -> StudentProfile:
    """Load a student profile from a JSON file."""
    path = Path(profile_path)
    if not path.exists():
        console.print(f"[red]Error: Profile file not found: {profile_path}[/red]")
        sys.exit(1)

    with open(path) as f:
        data = json.load(f)

    return StudentProfile.model_validate(data)


@click.command()
@click.option(
    "--profile",
    "-p",
    required=True,
    help="Path to student profile JSON file",
)
@click.option(
    "--output",
    "-o",
    default=None,
    help="Output file path for the report (default: output/<name>-College-Guide.md)",
)
@click.option(
    "--max-reviews",
    default=3,
    help="Maximum review iterations (default: 3)",
)
def main(profile: str, output: str | None, max_reviews: int) -> None:
    """Generate a comprehensive college planning report using multi-agent AI analysis."""
    console.print(
        Panel.fit(
            "[bold blue]College Guide Multi-Agent Workflow[/bold blue]\n"
            "Generating comprehensive college planning report...",
            border_style="blue",
        )
    )

    # Load config and student profile
    config = AppConfig.from_env()
    student = load_student_profile(profile)

    console.print(f"\n[bold]Student:[/bold] {student.name}")
    console.print(f"[bold]Grade:[/bold] {student.current_grade}")
    console.print(f"[bold]State:[/bold] {student.state}")
    console.print(f"[bold]Visa:[/bold] {student.visa_info.student_visa}")
    console.print(f"[bold]Intended Majors:[/bold] {', '.join(student.intended_majors)}")
    console.print()

    # Initialize LLM provider (reuse from trading_agents)
    from trading_agents.config import LLMConfig

    llm_config = LLMConfig(
        provider=config.llm_provider,
        model=config.llm_model,
        ollama_base_url=config.ollama_base_url,
        openai_api_key=config.openai_api_key,
        temperature=config.temperature,
    )
    llm = LLMProvider(llm_config)

    # Progress tracking
    agent_status: dict[str, str] = {}

    def on_step(step: dict) -> None:
        agent = step["agent"]
        status = step["status"]
        agent_status[agent] = status

    # Run the orchestrator
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Running multi-agent analysis...", total=None)

        def progress_step(step: dict) -> None:
            agent = step["agent"]
            status = step["status"]
            iteration = step.get("iteration", "")
            iter_str = f" (iteration {iteration})" if iteration else ""
            agent_display = agent.replace("_", " ").title()
            if status == "running":
                progress.update(task, description=f"[yellow]{agent_display}{iter_str}...[/yellow]")
            elif status == "completed":
                review_status = step.get("status_detail", "")
                status_str = f" - {review_status}" if review_status else ""
                console.print(f"  [green]✓[/green] {agent_display}{iter_str}{status_str}")

        orchestrator = OrchestratorAgent(
            llm=llm,
            max_review_iterations=max_reviews,
            on_step=progress_step,
        )
        report = orchestrator.run(student)

    # Display results
    console.print()
    if report.is_finalized:
        console.print(
            Panel.fit(
                f"[bold green]Report APPROVED[/bold green] "
                f"after {report.review_iterations} review iteration(s)",
                border_style="green",
            )
        )
    else:
        console.print(
            Panel.fit(
                f"[bold yellow]Report finalized[/bold yellow] "
                f"after {report.review_iterations} review iteration(s) "
                f"(max iterations reached)",
                border_style="yellow",
            )
        )

    # Save report
    if output is None:
        output_dir = Path(config.college_guide.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        safe_name = student.name.replace(" ", "-")
        output = str(output_dir / f"{safe_name}-College-Guide.md")

    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report.markdown_content)
    console.print(f"\n[bold]Report saved to:[/bold] {output_path}")
    console.print(f"[bold]Report length:[/bold] {len(report.markdown_content):,} characters")


if __name__ == "__main__":
    main()
