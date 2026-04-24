"""GitHub Copilot integration for prd2story."""

from .. import register
from ..base import MarkdownIntegration


@register
class CopilotIntegration(MarkdownIntegration):
    key = "copilot"
    display_name = "GitHub Copilot"
    config = {
        "name": "GitHub Copilot",
        "folder": ".github",
        "commands_subdir": "agents",
    }
    context_file = ".github/copilot-instructions.md"

    def _context_template_name(self) -> str:
        return "copilot-instructions.md"
