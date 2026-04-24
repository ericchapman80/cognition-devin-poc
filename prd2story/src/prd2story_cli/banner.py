"""ASCII art banner for prd2story CLI."""

from rich.console import Console
from rich.text import Text

BANNER = r"""
 ____  ____  ____  ____  ____  _____  ___  ____  _  _
(  _ \(  _ \(  _ \(_  _)(  _ \(  _  )/ __)(_  _)( \/ )
 )___/ )   / )(_) )  )(  _)(_  )(_)(  \__ \  )(  )  (
(__)  (_)\_)(____/ (__) (____)(_____)( ___/ (__) (_/\_)
"""

TAGLINE = "PRD to Story — Bootstrap Agile agent workflows into any repo"


def print_banner(console: Console | None = None) -> None:
    """Print the prd2story ASCII banner with colors."""
    if console is None:
        console = Console()

    banner_text = Text(BANNER, style="bold cyan")
    console.print(banner_text)
    console.print(f"  [italic bright_yellow]{TAGLINE}[/]\n")
