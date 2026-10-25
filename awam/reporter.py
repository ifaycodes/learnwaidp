"""Terminal UI and reporting utilities for awam using rich."""

import sys
import os
from typing import List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.text import Text

# Ensure clean UTF-8 encoding on Windows command prompt / powershell
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

console = Console(force_terminal=True)

def print_banner(tool_name: str = "awam") -> None:
    """Print clean header banner."""
    header = Text()
    header.append("⚡ ", style="bold yellow")
    header.append(tool_name, style="bold cyan")
    header.append(" — Proactive Edge Case & Unit Test Hub", style="dim")
    console.print(header)

def print_status(message: str) -> None:
    """Print cyan informational status message."""
    console.print(f"[cyan][awam][/cyan] {message}")

def print_warning(message: str) -> None:
    """Print yellow warning message."""
    console.print(f"[yellow][awam:warning][/yellow] {message}")

def print_error(message: str) -> None:
    """Print red error message or panel."""
    console.print(Panel(f"[bold red]Error:[/bold red] {message}", border_style="red", expand=False))

def print_success(message: str) -> None:
    """Print green success message."""
    console.print(f"[green][awam][/green] {message}")

def print_audit_table(candidate_cases: List[object]) -> None:
    """Display the unified edge case audit table.
    
    Highlights what the developer already covered in green ([✓])
    and missing edge cases in yellow ([+]).
    """
    table = Table(
        title="Unified Edge Case Audit",
        title_style="bold cyan",
        header_style="bold magenta",
        show_lines=True,
        expand=False,
    )
    table.add_column("Status", justify="center", style="bold", width=22)
    table.add_column("Scenario", style="white", min_width=28)
    table.add_column("Assessment / Reason", style="dim", min_width=32)

    covered_count = 0
    missing_count = 0

    for item in candidate_cases:
        if isinstance(item, dict):
            scenario = item.get("scenario", "")
            status = item.get("status", "missing")
            matched_test = item.get("matched_test")
            inquiry = item.get("inquiry", "")
            reason = item.get("reason", "")
        else:
            scenario = getattr(item, "scenario", "")
            status = getattr(item, "status", "missing")
            matched_test = getattr(item, "matched_test", None)
            inquiry = getattr(item, "inquiry", "")
            reason = getattr(item, "reason", "")

        if status == "covered":
            covered_count += 1
            status_text = Text("[✓] Already covered", style="bold green")
            scenario_cell = scenario
            assessment = f"Handled in `{matched_test}`" if matched_test else reason
        else:
            missing_count += 1
            status_text = Text("[+] Missing gap", style="bold yellow")
            if inquiry:
                scenario_cell = f"{scenario}\n[cyan]❓ Inquiry:[/cyan] [italic white]{inquiry}[/italic white]"
            else:
                scenario_cell = scenario
            assessment = reason or "No matching assertion found in test suite"

        table.add_row(status_text, scenario_cell, assessment)

    console.print()
    console.print(table)
    console.print()

    # Reinforcement summary line
    summary = Text()
    if covered_count > 0:
        summary.append(f"✓ {covered_count} covered ", style="bold green")
        summary.append("• ", style="dim")
    summary.append(f"{missing_count} missing edge case inquiries identified", style="bold yellow")
    console.print(summary)
    console.print()

def print_code_preview(code: str, title: str = "Generated Tests Preview", language: str = "python") -> None:
    """Print syntax-highlighted code block."""
    if not code.strip():
        console.print("[dim]No new tests generated (all candidate edge cases are already covered).[/dim]")
        return
    syntax = Syntax(code, language, theme="monokai", line_numbers=True)
    panel = Panel(syntax, title=f"[cyan]{title}[/cyan]", border_style="cyan", expand=False)
    console.print(panel)

def print_test_results(exit_code: int, output: str) -> None:
    """Display test runner execution results."""
    console.print()
    if exit_code == 0:
        console.print(Panel(
            "[bold green]✔ All tests passed![/bold green]\n" + output.strip(),
            title="[bold green]Test Runner: PASSED[/bold green]",
            border_style="green",
            expand=False,
        ))
    else:
        console.print(Panel(
            "[bold red]✘ Test failures detected[/bold red]\n" + output.strip(),
            title="[bold red]Test Runner: FAILED[/bold red]",
            border_style="red",
            expand=False,
        ))

def print_fix_suggestion(suggestion: object) -> None:
    """Display developer-led fix advice without touching source code."""
    summary = getattr(suggestion, "error_summary", "")
    guard = getattr(suggestion, "suggested_guard", "")
    target = getattr(suggestion, "target_file", "")

    content = f"[bold yellow]Exposed Gap:[/bold yellow] {summary}\n\n"
    content += f"[bold cyan]Suggested Guard for {target}:[/bold cyan]\n"
    content += f"  {guard}\n\n"
    content += "[dim](awam never modifies your source files; you decide how to implement the fix.)[/dim]"

    console.print()
    console.print(Panel(
        content,
        title="[bold yellow]💡 Developer Fix Suggestion[/bold yellow]",
        border_style="yellow",
        expand=False,
    ))

def print_diagnostics_footer(
    files_analyzed: List[str],
    target_test_file: Optional[str] = None,
    tests_appended: int = 0,
    model_name: str = "gemini-3.1-flash-lite",
    latency: Optional[float] = None,
    tokens_in: Optional[int] = None,
    tokens_out: Optional[int] = None,
) -> None:
    """Print the verbose diagnostics footer."""
    console.print()
    console.rule("[dim]Diagnostics[/dim]", style="dim")
    console.print(f"[dim]• Files analyzed:[/dim] {', '.join(files_analyzed)}")
    if target_test_file:
        console.print(f"[dim]• Target test file:[/dim] {target_test_file} ([green]+{tests_appended} tests[/green])")
    
    perf_parts = [f"Model: {model_name}"]
    if latency is not None:
        perf_parts.append(f"Latency: {latency:.2f}s")
    if tokens_in is not None and tokens_out is not None:
        perf_parts.append(f"Tokens: {tokens_in} in / {tokens_out} out")
    console.print(f"[dim]• {' | '.join(perf_parts)}[/dim]")
    console.rule(style="dim")
