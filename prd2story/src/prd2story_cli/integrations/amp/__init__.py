"""Amp integration for prd2story."""

from .. import register
from ..base import MarkdownIntegration


@register
class AmpIntegration(MarkdownIntegration):
    key = "amp"
    display_name = "Amp"
    config = {
        "name": "Amp",
        "folder": ".amp",
        "commands_subdir": "commands",
    }
    context_file = ".amp/instructions.md"

    def command_filename(self, template_name: str) -> str:
        return f"prd2story-{template_name}.md"

    def _context_template_name(self) -> str:
        return "generic-instructions.md"
