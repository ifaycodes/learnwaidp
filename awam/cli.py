"""Command line interface entrypoint for awam."""

import os
import sys
import click
from awam import __version__
from awam import reporter
from awam import engine

@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.argument("files", nargs=-1, required=True, type=click.Path(exists=True, dir_okay=False))
@click.option("--run", is_flag=True, default=False, help="Execute pytest after updating tests.")
@click.option("--audit-only", is_flag=True, default=False, help="Preview edge cases and tests without writing to disk.")
@click.option("--verbose", is_flag=True, default=False, help="Display timing, tokens, and resolved files.")
@click.option("--output", type=click.Path(), default=None, help="Custom test file destination.")
@click.version_option(version=__version__, prog_name="awam")
def main(files, run, audit_only, verbose, output):
    """awam: Proactive edge case detection & unit test generator.

    Target one source file (and optional local dependency files) to inspect
    what could go wrong and generate runnable unit tests in tests/.
    """
    reporter.print_banner()

    primary_file = files[0]
    additional_files = list(files[1:])

    reporter.print_status(f"Analyzing target file: [bold cyan]{primary_file}[/bold cyan]")

    try:
        with open(primary_file, "r", encoding="utf-8") as f:
            source_code = f.read()
    except Exception as e:
        reporter.print_error(f"Failed to read '{primary_file}': {e}")
        sys.exit(1)

    # Read additional dependency files if provided explicitly
    dep_files = {}
    for dep in additional_files:
        try:
            with open(dep, "r", encoding="utf-8") as f:
                dep_files[dep] = f.read()
            reporter.print_status(f"Loaded dependency context: [dim]{dep}[/dim]")
        except Exception as e:
            reporter.print_warning(f"Could not read dependency '{dep}': {e}")

    # Check for existing test file (Slice 2 will handle automatic discovery in tests/)
    existing_tests = ""
    target_test_file = output
    if not target_test_file:
        base_name = os.path.splitext(os.path.basename(primary_file))[0]
        candidate_test = os.path.join("tests", f"test_{base_name}.py")
        if os.path.exists(candidate_test):
            target_test_file = candidate_test
            try:
                with open(candidate_test, "r", encoding="utf-8") as f:
                    existing_tests = f.read()
                reporter.print_status(f"Found existing test file: [dim]{candidate_test}[/dim]")
            except Exception:
                pass

    # Call AI Engine
    try:
        with reporter.console.status("[cyan]Analyzing code and evaluating edge cases...[/cyan]", spinner="dots"):
            analysis, latency, used_model = engine.analyze_code(
                target_filename=primary_file,
                source_code=source_code,
                dependency_files=dep_files,
                existing_tests=existing_tests,
            )
    except engine.GeminiKeyMissingError as e:
        reporter.print_error(str(e))
        sys.exit(1)
    except Exception as e:
        reporter.print_error(f"Analysis failed: {e}")
        sys.exit(1)

    # Display Unified Edge Case Audit
    reporter.print_audit_table(analysis.candidate_cases)

    # Handle --audit-only preview
    if audit_only:
        reporter.print_code_preview(analysis.generated_tests, title="Generated Tests Preview (audit-only)")
        reporter.print_status("[dim]Audit-only mode active: no files were written to disk.[/dim]")
    else:
        # Placeholder for Slice 2 file write
        reporter.print_status("[yellow]File write will be performed in Slice 2.[/yellow]")

    # Diagnostics footer
    if verbose:
        all_files = [primary_file] + list(dep_files.keys())
        reporter.print_diagnostics_footer(
            files_analyzed=all_files,
            target_test_file=target_test_file,
            tests_appended=len([c for c in analysis.candidate_cases if c.status == "missing"]),
            model_name=used_model,
            latency=latency,
        )

if __name__ == "__main__":
    main()
