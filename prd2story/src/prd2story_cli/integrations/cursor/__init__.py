"""Cursor integration for prd2story."""

from .. import register
from ..base import MarkdownIntegration


@register
class CursorIntegration(MarkdownIntegration):
    key = "cursor-agent"
    display_name = "Cursor"
    config = {
        "name": "Cursor",
        "folder": ".cursor",
        "commands_subdir": "rules",
    }
    context_file = ".cursor/rules/prd2story.mdc"

    def command_filename(self, template_name: str) -> str:
        return f"prd2story.{template_name}.mdc"

    def _context_template_name(self) -> str:
        return "cursor-rules.mdc"
