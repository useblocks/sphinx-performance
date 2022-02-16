import importlib
import os.path
import shutil
import subprocess
import sys
import tempfile
import time
import webbrowser
from contextlib import suppress
from pathlib import Path

from jinja2 import Template

from sphinx_performance.utils import console

class ProjectEnv:
    def __init__(self, project_path, build_config, project_config):
        self.project_path = project_path
        self.build_config = build_config
        self.project_config = project_config

        self.source_path = project_path
        self.source_perf_conf_path = os.path.join(self.source_path, "performance.py")

        self.target_path = tempfile.mkdtemp()
        self.target_build_path = os.path.join(self.target_path, "_build")
        self.target_index_path = os.path.join(self.target_build_path, "index.html")
        self.target_req_path = os.path.join(self.target_path, "requirements.txt")

        self.python_path = sys.executable
        self.bin_path = os.path.dirname(self.python_path)
        self.pip_path = os.path.join(self.bin_path, 'pip')
        self.sphinx_path = os.path.join(self.bin_path, 'sphinx-build')

        self.extra_info = {}

    def config_is_valid(self):
        if not os.path.exists(self.source_perf_conf_path):
            console.print("performance.py file not found")
            return False

        try:
            spec = importlib.util.spec_from_file_location("module.name", self.source_perf_conf_path)
            per_conf = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(per_conf)
        except ImportError as e:
            console.print(f'performance.py file could not be imported: {{e}}')
            return False

        conf_params = per_conf.parameters
        self.extra_info = per_conf.info

        for param, default in conf_params.items():
            if param not in self.project_config:
                if default is not None:
                    self.project_config[param] = default
                else:
                    console.print(f'Missing parameter {{param}} in given config')
                    return False

        return True

    def _render_file(self, source, target, **kwargs):
        source_tmp_path = os.path.join(self.target_path, source)
        source_tmp_path_final = os.path.join(self.target_path, target)
        template = Template(Path(source_tmp_path).read_text())
        rendered = template.render(**self.project_config, **self.build_config, **kwargs)
        with open(source_tmp_path_final, "w") as file:
            file.write(rendered)

    def prepare_project(self):
        shutil.copytree(self.source_path, self.target_path, dirs_exist_ok=True)

        # Render files
        self._render_file("requirements.template", "requirements.txt")
        self._render_file("conf.template", "conf.py")
        self._render_file("index.template", "index.rst")

        # Calculate extra infos
        for name, result in self.extra_info.items():
            template = Template(result)
            self.extra_info[name] = template.render(**self.project_config, **self.build_config)

        # Render pages
        for p in range(self.project_config['pages']):
            title = f"Page {p}"
            self._render_file("page.template", f"page_{p}.rst", title=title, page=p)

    def install_dependencies(self):
        dep_command = [self.pip_path, "install", "-r", self.target_req_path]
        start_time = time.time()

        if self.build_config['debug']:
            console.rule('Installing dependencies START', style="blue")
            subprocess.call(dep_command)
            console.rule('Installing dependencies FINISHED', style="blue")
        else:
            with console.status("Installing dependencies"):
                subprocess.call(dep_command, stdout=subprocess.DEVNULL)
        end_time = time.time()
        result_time = end_time - start_time

    def build(self):
        """
        Build copied Sphnx project
        """
        if self.build_config['browser']:
            self.build_config['keep'] = True

        conf_str = ', '.join([f'{key}: {value}' for key, value in self.project_config.items()])
        console.print(f"[bold]Core/s[/bold]:\t\t {self.build_config['parallel']}")
        console.print(f"[bold]Config[/bold]:\t\t {conf_str}")
        info_str = ', '.join([f'{key}: {value}' for key, value in self.extra_info.items()])
        console.print(f"[bold]Info[/bold]:\t\t {info_str}")
        start_time = time.time()
        params = [
            self.sphinx_path,
            "-a",
            "-E",
            "-j",
            str(self.build_config['parallel']),
            "-b",
            "html",
            self.target_path,
            self.target_build_path,
        ]

        if self.build_config['debug']:
            console.print(f'Call:\t\t {" ".join(params)} ')

        if self.build_config['debug']:
            console.rule('Building documentation START', style="blue")
            subprocess.run(params)
            console.rule('Building documentation FINISHED', style="blue")
        else:
            with console.status("Building documentation"):
                subprocess.run(params, stdout=subprocess.DEVNULL)

        end_time = time.time()

        if self.build_config['keep']:
            console.print(f"\nProject:\t {self.target_path}")
            console.print(f"Build:\t\t {self.target_index_path}")
        else:
            if self.build_config['debug']:
                console.print(f"\nDeleting project {self.target_build_path}")
            shutil.rmtree(self.target_build_path)
            shutil.rmtree(self.target_path)

        result_time = end_time - start_time
        console.print(f"\n[bold red]Duration[/bold red]:\t {result_time:.2f} seconds")
        return result_time

    def post_processing(self):
        if self.build_config['browser']:
            with suppress(Exception):
                webbrowser.open_new_tab(self.target_index_path)

