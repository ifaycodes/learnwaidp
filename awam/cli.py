"""Command line interface entrypoint for awam."""

import os
import sys
import click
from awam import __version__
from awam import reporter
from awam import engine
from awam import test_manager
from awam import analyzer
from awam import resolver
from awam import runner

@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.argument("files", nargs=-1, required=True, type=click.Path(exists=True, dir_okay=False))
@click.option("--run", is_flag=True, default=False, help="Execute pytest after updating tests.")
@click.option("--generate", "-g", is_flag=True, default=False, help="Generate and append missing tests into tests/ directory.")
@click.option("--audit-only", is_flag=True, default=False, help="Preview edge case audit and generated tests without writing to disk.")
@click.option("--verbose", is_flag=True, default=False, help="Display timing, tokens, and resolved files.")
@click.option("--output", type=click.Path(), default=None, help="Custom test file destination.")
@click.option("--mock", "--demo", is_flag=True, default=False, help="Run in offline simulation mode without API key.")
@click.version_option(version=__version__, prog_name="awam")
def main(files, run, generate, audit_only, verbose, output, mock):
    """awam: Proactive edge case detection & unit test generator.

    Target one source file (and optional local dependency files) to inspect
    what could go wrong and generate runnable unit tests in tests/.
    """
    if mock:
        os.environ["AWAM_MOCK"] = "1"

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

    # 1. Pre-flight lint & syntax sanity check
    preflight = analyzer.run_preflight(source_code, primary_file)
    if not preflight.is_valid:
        for err in preflight.errors:
            reporter.print_error(f"Pre-flight check failed in '{primary_file}':\n{err}")
        sys.exit(1)

    reporter.print_status("Pre-flight syntax check passed.")
    for warn in preflight.warnings:
        reporter.print_warning(f"Pre-flight warning: {warn}")

    # 2. Local module dependency traversal (up to 2 helper files, max 3 files total)
    dep_files = resolver.resolve_dependencies(primary_file, max_helper_files=2)
    for dep_path in dep_files:
        reporter.print_status(f"Resolved local dependency: [dim]{dep_path}[/dim]")

    # Also include any explicitly supplied files up to limit
    for dep in additional_files:
        if len(dep_files) >= 2:
            break
        if dep not in dep_files and os.path.isfile(dep):
            try:
                with open(dep, "r", encoding="utf-8") as f:
                    dep_files[dep] = f.read()
                reporter.print_status(f"Loaded explicit dependency: [dim]{dep}[/dim]")
            except Exception as e:
                reporter.print_warning(f"Could not read dependency '{dep}': {e}")

    # Resolve and discover target test file
    target_test_file = test_manager.resolve_test_file(primary_file, output)
    existing_tests = test_manager.read_existing_tests(target_test_file)
    if existing_tests:
        reporter.print_status(f"Found existing test file: [dim]{target_test_file}[/dim]")

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

    # Handle --generate or default inquiry mode
    tests_written = 0
    if generate:
        tests_written, was_created = test_manager.write_or_append_tests(
            test_file_path=target_test_file,
            generated_tests=analysis.generated_tests,
            source_file=primary_file,
        )
        if was_created:
            reporter.print_success(f"Created new test file: [bold green]{target_test_file}[/bold green] ({tests_written} tests)")
        elif tests_written > 0:
            reporter.print_success(f"Appended [bold green]+{tests_written} tests[/bold green] to {target_test_file}")
        else:
            reporter.print_status(f"Test suite in {target_test_file} already covers candidate edge cases.")
    elif audit_only:
        reporter.print_code_preview(analysis.generated_tests, title="Generated Tests Preview (audit-only)")
        reporter.print_status("[dim]Audit-only preview: no files were written to disk.[/dim]")
    else:
        reporter.print_status("[cyan]Inquiry mode active: no files modified on disk.[/cyan]")
        reporter.console.print("  [dim]• Use the questions above to write tests in your test suite.[/dim]")
        reporter.console.print("  [dim]• Run with [bold cyan]--generate[/bold cyan] to have awam draft tests for you in tests/.[/dim]")
        reporter.console.print("  [dim]• Run with [bold cyan]--run[/bold cyan] to execute pytest and check your error guards.[/dim]\n")

    # 4. Optional test runner execution and fix advisor (--run)
    if run:
        if not os.path.exists(target_test_file):
            reporter.print_warning(f"No test file found at '{target_test_file}'. Write tests or run with '--generate' first.")
        else:
            reporter.print_status(f"Executing test runner against [bold cyan]{target_test_file}[/bold cyan]...")
            exit_code, test_output = runner.execute_pytest(target_test_file)
            reporter.print_test_results(exit_code, test_output)
            if exit_code != 0:
                with reporter.console.status("[cyan]Formulating developer fix suggestion...[/cyan]", spinner="dots"):
                    suggestion = runner.suggest_fix(test_output, primary_file, model_name=used_model)
                reporter.print_fix_suggestion(suggestion)

    # Diagnostics footer
    if verbose:
        all_files = [primary_file] + list(dep_files.keys())
        reporter.print_diagnostics_footer(
            files_analyzed=all_files,
            target_test_file=target_test_file,
            tests_appended=tests_written,
            model_name=used_model,
            latency=latency,
        )

if __name__ == "__main__":
    main()
