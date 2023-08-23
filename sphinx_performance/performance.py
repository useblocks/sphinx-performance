"""Execute several performance tests."""
import csv
import os.path
import subprocess
import time
from pathlib import Path

import click
import rich.table
from rich import box
from rich.style import Style

from sphinx_performance.call import Call
from sphinx_performance.projectenv import ProjectEnv
from sphinx_performance.utils import console

PROJECTS = {
    "basic": Path(Path(__file__).parent) / "projects" / "basic",
    "needs": Path(Path(__file__).parent) / "projects" / "needs",
    "theme": Path(Path(__file__).parent) / "projects" / "theme",
}


@click.command(
    context_settings={
        "ignore_unknown_options": True,
        "allow_extra_args": True,
        "help_option_names": ["-h", "--help"],
    },
)
@click.option(
    "--project",
    "projects",
    default=["basic"],
    type=str,
    multiple=True,
    help="Defines the project to build",
)
@click.option(
    "--profile",
    default=[],
    type=str,
    multiple=True,
    help="Activates profiling for given area",
)
@click.option(
    "--parallel",
    default=[1],
    type=int,
    multiple=True,
    help="Number of parallel processes to use. Same as -j for sphinx-build",
)
@click.option(
    "--builder",
    default=["html"],
    multiple=True,
    help="Define the builder to use",
)
@click.option(
    "--keep",
    is_flag=True,
    default=False,
    help="Keeps the temporary src and build folders",
)
@click.option(
    "--browser",
    is_flag=True,
    default=False,
    help="Opens the project in your browser",
)
@click.option(
    "--snakeviz",
    is_flag=True,
    default=False,
    help="Opens snakeviz view for measured profiles in browser",
)
@click.option(
    "--debug",
    is_flag=True,
    default=False,
    help="console.prints more information, incl. sphinx build output",
)
@click.option(
    "--temp",
    default=None,
    type=str,
    help="Base folder path to use for temp folders. Must exist.",
)
@click.option(
    "--csv",
    "csv_file",
    default=None,
    type=str,
    help="CSV file path, which shall store the results.",
)
@click.pass_context
def cli_performance(
    ctx,
    projects,
    profile,
    parallel,
    builder,
    keep,
    browser,
    snakeviz,
    debug,
    temp,
    csv_file,
):
    """CLI performance handling."""
    build_kwargs = {
        "builder": builder,
        "parallel": list(parallel),
        "keep": [keep],
        "browser": [browser],
        "snakeviz": [snakeviz],
        "debug": [debug],
    }

    call = Call(projects, ctx.args, build_kwargs)

    profile_str = ",".join(profile)
    os.environ["NEEDS_PROFILING"] = profile_str

    console.print(f"\nRunning {call.runs} test configurations.\n")
    results = []

    console.print(f"\nRunning {call.runs} test configurations.\n")
    results = []

    counter = 1
    for project in projects:
        for build_config in call.build_configs:
            for project_config in call.project_configs:
                console.rule(f"[bold red]Run {counter}/{call.runs}")
                project_obj = ProjectEnv(
                    project,
                    call.project_path[project],
                    build_config,
                    project_config,
                    temp,
                )
                if not project_obj.config_is_valid():
                    console.print("Errors in configuration. Skipping this run.")
                    continue
                project_obj.prepare_project()
                project_obj.install_dependencies()

                result, extra_results = project_obj.build_external()

                project_obj.post_processing()

                config = {**project_obj.project_config}
                config["parallel"] = project_obj.build_config["parallel"]
                config["builder"] = project_obj.build_config["builder"]
                results.append(
                    {
                        "project": project,
                        "result": result,
                        "config": config,
                        "info": project_obj.extra_info,
                        "extra": extra_results,
                    },
                )
                counter += 1

    console.rule("[bold red]RESULTS")

    # Calculate overall config keys, as each project may report different configs.
    # So the final tables need to fill out not used config-keys from different results.
    all_keys = {
        "config": [],
        "info": [],
        "extra": [],
    }
    for key in all_keys:
        found_keys = []
        for result in results:
            found_keys += result[key]
        all_keys[key] = set(found_keys)

    # Result matrix
    matrix = []
    headers = ["#", "runtime", "project"]
    headers.append("")

    for keys in all_keys.values():
        headers += keys
        headers.append("")

    matrix.append(headers)

    run = 1

    for result in results:
        values = [f"Run {run!s}", f"{result['result']:.2f}"]
        values += [result["project"]]
        values += [""]

        for all_type, keys in all_keys.items():
            key_values = []
            for key in keys:
                key_values.append(
                    str(result[all_type].get(key, "-")),
                )  # If no value set for config, set to "-"
            values += key_values
            values += [""]

        matrix.append([*values])
        run += 1

    matrix_transpose = list(map(list, zip(*matrix)))

    topic_style = Style(bold=True)
    runtime_style = Style(color="red", bold=True)
    diff_style = Style(color="gold3", bold=True)

    # Result table
    table = rich.table.Table(box=box.ROUNDED)
    for i, column in enumerate(matrix_transpose[0]):
        style = topic_style if i == 0 else None
        table.add_column(column, justify="center", style=style)

    for i, row in enumerate(matrix_transpose[1:]):
        style = None
        if i == 0:
            style = runtime_style
        elif len(set(row[1:])) != 1:
            style = diff_style
        table.add_row(*row, style=style)

    console.print(table)
    overall_runtime = sum(x["result"] for x in results)
    console.print(f"\nOverall runtime: {overall_runtime:.2f} seconds.")

    if csv_file:
        try:
            with Path.open(csv_file, "w") as f:
                writer = csv.writer(f, delimiter=",", quotechar="|")
                for row in matrix_transpose:
                    writer.writerow(row)
        except csv.Error as e:
            console.print(f"Error during storing csv file: {csv_file}. Reason: {e}")
        else:
            console.print(f"CSV file stored: {csv_file}")

    if snakeviz:
        console.print("\nStarting snakeviz servers\n")
        procs = []
        for p in profile:
            proc = subprocess.Popen(["snakeviz", f"profile/{p}.prof"])
            procs.append(proc)

        console.print(f"\nKilling snakeviz server in {len(procs)*5} secs.")
        time.sleep(len(procs) * 5)
        for proc in procs:
            proc.kill()


if "main" in __name__:
    cli_performance()
