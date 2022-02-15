"""
Executes several performance tests.

"""
import itertools
import os.path
import shutil
import subprocess
import sys
import tempfile
import time
import webbrowser
from contextlib import suppress
from pathlib import Path

import click
from jinja2 import Template
from tabulate import tabulate

RUNTIMES = {
    "basics": {
        "deps": os.path.join(os.path.dirname(__file__), "runtimes", "basics"),
    }
}

PROJECTS = {
    "needs": os.path.join(os.path.dirname(__file__), "projects", "needs")
}

class RuntimeEnv:
    def __init__(self, runtime_conf_path):

        self.runtime_conf_path = runtime_conf_path
        self.runtime_requirements = os.path.join(self.runtime_conf_path, 'requirements.txt')
        self.python_path = sys.executable

        self.bin_path = os.path.dirname(self.python_path)

        self.pip_path = os.path.join(self.bin_path, 'pip')
        self.sphinx_path = os.path.join(self.bin_path, 'sphinx-build')

    def install_python_env(self):
        """
        NOT READY TO USE
        """
        if self.already_installed:
            raise Exception("already_installed is set for runtime. Can't install python")

        os.chdir(self.runtime_path)
        subprocess.call(['which', 'python'])
        venv_command = ["python", "-m", "venv", '.venv']
        subprocess.call(venv_command)
        print("python venv installed")

    def install_dependencies(self):
        #shutil.copytree(self.runtime_conf_path, self.runtime_path, dirs_exist_ok=True)

        dep_command = [self.pip_path, "install", "-r", self.runtime_requirements]
        subprocess.call(dep_command)
        print("python dependencies installed")


class ProjectEnv:
    def __init__(self, runtime, project_path, build_config, project_config):
        self.project_path = project_path
        self.build_config = build_config
        self.project_config = project_config

        self.source_path = project_path
        self.source_tmp_path = tempfile.mkdtemp()
        self.build_path = tempfile.mkdtemp()

        self.sphinx_path = runtime.sphinx_path
        self.index_path = os.path.join(self.build_path, "index.html")

    def prepare_project(self):
        shutil.copytree(self.source_path, self.source_tmp_path, dirs_exist_ok=True)

        # Render conf.py
        source_tmp_path_conf = os.path.join(self.source_tmp_path, "conf.template")
        source_tmp_path_conf_final = os.path.join(self.source_tmp_path, "conf.py")
        template = Template(Path(source_tmp_path_conf).read_text())
        rendered = template.render(**self.project_config, **self.build_config)
        with open(source_tmp_path_conf_final, "w") as file:
            file.write(rendered)

        # Render index files
        source_tmp_path_index = os.path.join(self.source_tmp_path, "index.template")
        source_tmp_path_index_final = os.path.join(self.source_tmp_path, "index.rst")
        template = Template(Path(source_tmp_path_index).read_text())
        title = "Index"
        rendered = template.render(**self.project_config, **self.build_config, title=title)

        with open(source_tmp_path_index_final, "w") as file:
            file.write(rendered)

        # Render pages
        for p in range(self.project_config['pages']):
            source_tmp_path_page = os.path.join(self.source_tmp_path, "page.template")
            source_tmp_path_page_final = os.path.join(self.source_tmp_path, f"page_{p}.rst")
            template = Template(Path(source_tmp_path_page).read_text())
            title = f"Page {p}"
            rendered = template.render(
                page=p,
                title=title,
                **self.project_config,
                **self.build_config
            )
            with open(source_tmp_path_page_final, "w") as file:
                file.write(rendered)

    def build(self):
        """
        Build copied Sphnx project
        """
        if self.build_config['browser']:
            self.build_config['keep'] = True

        conf_str = ', '.join([f'{key}: {value}' for key, value in self.project_config.items()])
        print(
            f"* Using {self.build_config['parallel']} cores: {conf_str}"
        )
        start_time = time.time()
        params = [
            self.sphinx_path,
            "-a",
            "-E",
            "-j",
            str(self.build_config['parallel']),
            "-b",
            "html",
            self.source_tmp_path,
            self.build_path,
        ]

        if self.build_config['keep'] and self.build_config['debug']:
            print(f"  Project = {self.source_tmp_path}")
            print(f"  Build   = {self.index_path}")
        if self.build_config['debug']:
            print(f'  Call: {" ".join(params)} ')

        if self.build_config['debug']:
            subprocess.run(params)
        else:
            subprocess.run(params, stdout=subprocess.DEVNULL)

        end_time = time.time()

        if self.build_config['keep']:
            print(f"  Project = {self.source_tmp_path}")
            print(f"  Build   = {self.index_path}")
        else:
            if self.build_config['debug']:
                print(f"  Deleting project: {self.build_path}")
            shutil.rmtree(self.build_path)
            shutil.rmtree(self.source_tmp_path)

        result_time = end_time - start_time
        print(f"  Duration: {result_time:.2f} seconds")
        return result_time

    def post_processing(self):
        if self.build_config['browser']:
            with suppress(Exception):
                webbrowser.open_new_tab(self.index_path)


@click.command(context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True,
))
@click.option("--runtime", type=str, default='basics', help="Defines the runtime to use")
@click.option("--project", type=str, help="Defines the project to build")
@click.option("--profile", default=[], type=str, multiple=True, help="Activates profiling for given area")
@click.option(
    "--parallel",
    default=[1, 4],
    type=int,
    multiple=True,
    help="Number of parallel processes to use. Same as -j for sphinx-build",
)
@click.option("--keep", is_flag=True, help="Keeps the temporary src and build folders")
@click.option("--browser", is_flag=True, help="Opens the project in your browser")
@click.option("--snakeviz", is_flag=True, help="Opens snakeviz view for measured profiles in browser")
@click.option("--debug", is_flag=True, help="Prints more information, incl. sphinx build output")
@click.option("--basic", is_flag=True, help="Use only default config of Sphinx-Needs (e.g. no extra options)")
@click.pass_context
def cli(
    ctx,
    runtime,
    project,
    profile,
    parallel,
    keep=False,
    browser=False,
    snakeviz=False,
    debug=False,
    basic=False,
):
    """
    CLI handling
    """

    if runtime not in RUNTIMES:
        if not os.path.exists(runtime):
            print(f'Runtime {runtime} not found')
            sys.exit(1)
        runtime_deps = os.path.abspath(runtime)
    else:
        runtime_deps = RUNTIMES[runtime]['deps']

    if project not in PROJECTS:
        if not os.path.exists(project):
            print(f'Project {project} not found')
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
        except TypeError:
            pass
        project_kwargs[name].append(value)

    project_configs = {}
    if project_kwargs:
        keys, values = zip(*project_kwargs.items())
        project_configs = [dict(zip(keys, v)) for v in itertools.product(*values)]

    build_kwargs = {"parallel": list(parallel), "keep": [keep], "browser": [browser], "snakeviz": [snakeviz],
                    "debug": [debug], "basic": [basic]}

    keys, values = zip(*build_kwargs.items())
    build_configs = [dict(zip(keys, v)) for v in itertools.product(*values)]

    profile_str = ",".join(profile)
    os.environ["NEEDS_PROFILING"] = profile_str

    print(f"Running {len(project_configs)} test configurations.")
    results = []

    runtime_obj = RuntimeEnv(runtime_deps)
    runtime_obj.install_dependencies()

    for build_config in build_configs:
        for project_config in project_configs:
            project = ProjectEnv(runtime_obj, project_path, build_config, project_config)
            project.prepare_project()
            result = project.build()
            config = {**project_config}
            config['parallel'] = build_config['parallel']
            results.append((config, result))

    print("\nRESULTS:\n")
    result_table = []
    for result in results:
        result_table.append([f"{result[1]:.2f}"] + list(result[0].values()))
    headers = ["runtime\nseconds"] + [x for x in list(result[0].keys())]
    print(tabulate(result_table, headers=headers))

    overall_runtime = sum(x[1] for x in results)
    print(f"\nOverall runtime: {overall_runtime:.2f} seconds.")

    if snakeviz:
        print("\nStarting snakeviz servers\n")
        procs = []
        for p in profile:
            proc = subprocess.Popen(["snakeviz", f"profile/{p}.prof"])
            procs.append(proc)

        print(f"\nKilling snakeviz server in {len(procs)*5} secs.")
        time.sleep(len(procs) * 5)
        for proc in procs:
            proc.kill()


if "main" in __name__:
    cli()
