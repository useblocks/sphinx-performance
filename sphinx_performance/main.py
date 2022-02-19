"""
Executes several performance tests.

"""
import csv
import itertools
import os.path
import subprocess
import sys
import time

import click
import rich.table
from rich.style import Style
from rich import box

from sphinx_performance.projectenv import ProjectEnv
from sphinx_performance.utils import console

PROJECTS = {
    "basic": os.path.join(os.path.dirname(__file__), "projects", "basic"),
    "needs": os.path.join(os.path.dirname(__file__), "projects", "needs")
}


@click.command(context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True,
))
@click.option("--project", default="basic", type=str, help="Defines the project to build")
@click.option("--profile", default=[], type=str, multiple=True, help="Activates profiling for given area")
@click.option(
    "--parallel",
    default=[1],
    type=int,
    multiple=True,
    help="Number of parallel processes to use. Same as -j for sphinx-build",
)
@click.option("--builder", default=['html'], multiple=True, help="Keeps the temporary src and build folders")
@click.option("--keep", is_flag=True, help="Keeps the temporary src and build folders")
@click.option("--browser", is_flag=True, help="Opens the project in your browser")
@click.option("--snakeviz", is_flag=True, help="Opens snakeviz view for measured profiles in browser")
@click.option("--debug", is_flag=True, help="console.prints more information, incl. sphinx build output")
@click.option("--temp", default=None, type=str, help="Base folder path to use for temp folders. Must exist.")
@click.option("--csv", 'csv_file', default=None, type=str, help="CSV file path, which shall store the results.")
@click.pass_context
def cli(
    ctx,
    project,
    profile,
    parallel,
    builder,
    keep=False,
    browser=False,
    snakeviz=False,
    debug=False,
    temp=None,
    csv_file=None
):
    """
    CLI handling
    """

    if project not in PROJECTS:
        if not os.path.exists(project):
            console.print(f'Project {project} not found')
            sys.exit(1)
        project_path = os.path.abspath(project)
    else:
        project_path = PROJECTS[project]

    project_kwargs = {}
    for i in range(0, len(ctx.args), 2):
        name = ctx.args[i][2:]
        if name not in project_kwargs:
            project_kwargs[name] = []
        value = ctx.args[i + 1]
        try:
            value = int(value)
        except ValueError:
            pass
        project_kwargs[name].append(value)

    if project_kwargs:
        # Create project config test matrix
        keys, values = zip(*project_kwargs.items())
        project_configs = [dict(zip(keys, v)) for v in itertools.product(*values)]
    else:
        project_configs = [{}]

    build_kwargs = {"builder": builder, "parallel": list(parallel), "keep": [keep], "browser": [browser],
                    "snakeviz": [snakeviz], "debug": [debug]}

    # Create build test matrix
    keys, values = zip(*build_kwargs.items())
    build_configs = [dict(zip(keys, v)) for v in itertools.product(*values)]

    profile_str = ",".join(profile)
    os.environ["NEEDS_PROFILING"] = profile_str

    console.print(f"\nRunning {len(project_configs) * len(build_configs)} test configurations.\n")
    results = []

    counter = 1
    for build_config in build_configs:
        for project_config in project_configs:
            console.rule(f"[bold red]Run {counter}")
            project = ProjectEnv(project_path, build_config, project_config, temp)
            if not project.config_is_valid():
                console.print('Errors in configuration. Skipping this run.')
                continue
            project.prepare_project()
            project.install_dependencies()

            result, extra_results = project.build()

            project.post_processing()

            config = {**project.project_config}
            config['parallel'] = project.build_config['parallel']
            config['builder'] = project.build_config['builder']
            # config += {** project.extra_info}
            results.append({
                "result": result,
                "config": config,
                "info": project.extra_info,
                "extra": extra_results})
            counter += 1

    console.rule("[bold red]RESULTS")

    # Result matrix
    matrix = []
    headers = ['#', 'runtime']
    headers.append("")
    for key in results[0]['config'].keys():
        headers.append(key)

    headers.append("")
    for key in results[0]['info'].keys():
        headers.append(key)

    headers.append("")
    for key in results[0]['extra'].keys():
        headers.append(key)

    matrix.append(headers)

    run = 1
    for result in results:
        values = [f'Run {str(run)}', f"{result['result']:.2f}"]
        values += [""]
        values += [str(x) for x in result['config'].values()]
        values += [""]
        values += [str(x) for x in result['info'].values()]
        values += [""]
        values += [str(x) for x in result['extra'].values()]
        matrix.append([*values])
        run += 1

    matrix_transpose = list(map(list, zip(*matrix)))

    topic_style = Style(bold=True)
    runtime_style = Style(color='red', bold=True)
    diff_style = Style(color="gold3", bold=True)

    # Result table
    table = rich.table.Table(box=box.ROUNDED)
    for i, column in enumerate(matrix_transpose[0]):
        if i == 0:
            style = topic_style
        else:
            style = None
        table.add_column(column, justify="center", style=style)

    for i, row in enumerate(matrix_transpose[1:]):
        style = None
        if i == 0:
            style = runtime_style
        elif len(set(row[1:])) != 1:
            style = diff_style
        table.add_row(*row, style=style)

    console.print(table)
    overall_runtime = sum(x['result'] for x in results)
    console.print(f"\nOverall runtime: {overall_runtime:.2f} seconds.")

    if csv_file:
        try:
            with open(csv_file, 'w') as f:
                writer = csv.writer(f, delimiter=",", quotechar="|")
                for row in matrix_transpose:
                    writer.writerow(row)
        except csv.Error as e:
            console.print(f'Error during storing csv file: {csv_file}. Reason: {e}')
        else:
            console.print(f'CSV file stored: {csv_file}')

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
    cli()
