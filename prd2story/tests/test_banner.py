"""Tests for the ASCII art banner."""

from io import StringIO

from rich.console import Console

from prd2story_cli.banner import BANNER, TAGLINE, print_banner


class TestBanner:
    def test_banner_string_not_empty(self):
        assert len(BANNER.strip()) > 0

    def test_tagline_not_empty(self):
        assert len(TAGLINE) > 0

    def test_print_banner_produces_output(self):
        output = StringIO()
        console = Console(file=output, force_terminal=True)
        print_banner(console)
        result = output.getvalue()
        assert len(result) > 0

    def test_banner_contains_prd2story(self):
        # The ASCII art should contain recognizable text
        assert "PRD" in BANNER.upper() or "prd" in BANNER.lower() or "____" in BANNER
