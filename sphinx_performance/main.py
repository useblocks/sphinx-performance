"""
Executes several performance tests.

"""
import itertools
import os.path
import subprocess
import sys
import time

import click
import rich.table

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
@click.option("--keep", is_flag=True, help="Keeps the temporary src and build folders")
@click.option("--browser", is_flag=True, help="Opens the project in your browser")
@click.option("--snakeviz", is_flag=True, help="Opens snakeviz view for measured profiles in browser")
@click.option("--debug", is_flag=True, help="console.prints more information, incl. sphinx build output")
@click.pass_context
def cli(
    ctx,
    project,
    profile,
    parallel,
    keep=False,
    browser=False,
    snakeviz=False,
    debug=False,
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
        keys, values = zip(*project_kwargs.items())
        project_configs = [dict(zip(keys, v)) for v in itertools.product(*values)]
    else:
        project_configs = [{}]

    build_kwargs = {"parallel": list(parallel), "keep": [keep], "browser": [browser], "snakeviz": [snakeviz],
                    "debug": [debug]}

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
            project = ProjectEnv(project_path, build_config, project_config)
            if not project.config_is_valid():
                console.print('Errors in configuration. Skipping this run.')
                continue
            project.prepare_project()
            project.install_dependencies()
            result = project.build()
            project.post_processing()
            config = {**project.project_config, **project.extra_info}
            config['parallel'] = project.build_config['parallel']
            results.append((config, result))
            counter += 1

    console.rule("[bold red]RESULTS")

    # Result table
    table = rich.table.Table()
    table.add_column('#', justify="center")
    table.add_column('runtime\nseconds', justify="center")
    for key in results[0][0].keys():
        table.add_column(key, justify="center")

    run = 1
    for result in results:
        values = [str(run), f"{result[1]:.2f}"] + [str(x) for x in result[0].values()]
        table.add_row(*values)
        run += 1

    console.print(table)

    overall_runtime = sum(x[1] for x in results)
    console.print(f"\nOverall runtime: {overall_runtime:.2f} seconds.")

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
