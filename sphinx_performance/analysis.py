"""
Executes several performance tests.

"""
import os.path
import subprocess
import sys
import time
import click
import webbrowser
from contextlib import suppress

from sphinx_performance.call import Call
from sphinx_performance.projectenv import ProjectEnv
from sphinx_performance.utils import console

from sphinx_performance.config import RUNTIME_PROFILE, MEMORY_PROFILE, MEMORY_HTML


@click.command(context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True,
))
@click.option("--project", 'projects', default=["basic"], type=str, multiple=True, help="Defines the project to build")
@click.option("--profile", default=[], type=str, multiple=True, help="Activates profiling for given area")
@click.option(
    "--parallel",
    default=[1],
    type=int,
    multiple=True,
    help="Number of parallel processes to use. Same as -j for sphinx-build",
)
@click.option("--builder", default=['html'], multiple=True, help="Define the builder to use")
@click.option("--keep", is_flag=True, help="Keeps the temporary src and build folders")
@click.option("--browser", is_flag=True, help="Opens the project in your browser")
@click.option("--flamegraph", is_flag=True, help="Opens a flamegraph view if 'runtime' or 'memray' is used.")
@click.option("--debug", is_flag=True, help="console.prints more information, incl. sphinx build output")
@click.option("--temp", default=None, type=str, help="Base folder path to use for temp folders. Must exist.")
@click.option("--silent", is_flag=True, help="Do not wait for user input. Always answer [y]es.")
@click.option("--stats", is_flag=True, help="Prints out the cProfile stats.")
@click.option("--runtime", is_flag=True, help="Activates runtime profiling for the complete build. ")
@click.option("--memray", is_flag=True, help="Activates memory profiling for the complete build.")
@click.option("--memray-live", is_flag=True, help="Activates memory live profiling for the complete build.")
@click.option("--summary", is_flag=True, help="Prints a summary, if 'memray' is used.")
@click.pass_context
def cli_analysis(
    ctx,
    projects,
    profile,
    parallel,
    builder,
    keep=False,
    browser=False,
    flamegraph=False,
    debug=False,
    temp=None,
    silent=False,
    stats=False,
    runtime=False,
    memray=False,
    memray_live=False,
    summary=False
):
    """
    CLI analysis handling
    """
    if sum([runtime, memray, memray_live]) >= 2:
        console.print('[bold red]runtime, memray and memray_live can not be profiled together, because '
                      'they influence each other to much. Please use only one per call.')
        sys.exit(1)

    build_kwargs = {"builder": builder, "parallel": list(parallel), "keep": [keep], "browser": [browser],
                    "flamegraph": [flamegraph], "debug": [debug]}

    call = Call(projects, ctx.args, build_kwargs)

    profile_str = ",".join(profile)
    os.environ["NEEDS_PROFILING"] = profile_str

    console.print(f"\nRunning {call.runs} test configurations.\n")

    if call.runs > 1 and not silent:
        console.print(f'[bold red]There should not be more than 1 run for performance analysing. Given are {call.runs}.')
        answer = ''
        while answer not in ['y', 'n']:
            answer = console.input('Really continue? \[y/N]  ')
            if answer == 'n' or answer == '':
                console.log('Exit now.')
                sys.exit(0)

    results = []
    counter = 1
    for project in projects:
        for build_config in call.build_configs:
            for project_config in call.project_configs:
                console.rule(f"[bold red]Run {counter}/{call.runs}")
                project_obj = ProjectEnv(project, call.project_path[project], build_config, project_config, temp)
                if not project_obj.config_is_valid():
                    console.print('Errors in configuration. Skipping this run.')
                    continue
                project_obj.prepare_project()
                project_obj.install_dependencies()

                app_code, build_time, all_profile = project_obj.build_internal(use_runtime=runtime,
                                                                               use_memray=memray,
                                                                               use_memray_live=memray_live)

                console.print(f'Build done in {build_time:.3f}s with status code {app_code}')
                project_obj.post_processing()

                if runtime:
                    all_profile.dump_stats(RUNTIME_PROFILE)
                    if stats:
                        all_profile.print_stats()

                if memray:
                    if stats:
                        args = ['memray', 'stats', '-n', '10', MEMORY_PROFILE]
                        subprocess.run(args)
                    if summary:
                        args = ['memray', 'summary', MEMORY_PROFILE]
                        subprocess.run(args)

    if flamegraph:
        if runtime:
            console.print("\nStarting snakeviz servers\n")
            procs = []
            for p in profile:
                proc = subprocess.Popen(["snakeviz", f"profile/{p}.prof"])
                procs.append(proc)

            if runtime:
                proc = subprocess.Popen(["snakeviz", RUNTIME_PROFILE])
                procs.append(proc)

            console.print(f"\nKilling snakeviz server in {len(procs)*5} secs.")
            time.sleep(len(procs) * 5)
            for proc in procs:
                proc.kill()
        if memray:
            args = ['memray', 'flamegraph', '-f', '-o', MEMORY_HTML, MEMORY_PROFILE]
            subprocess.run(args)
            with suppress(Exception):
                webbrowser.open_new_tab(MEMORY_HTML)



if "main" in __name__:
    cli_analysis()
