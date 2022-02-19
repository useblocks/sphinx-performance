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

NEED_CONFIG_DEFAULT = ['pages', 'folders', 'depth']

GLOBAL_PAGE_COUNTER = 0  # Needed for unique IDs in recursive creation functions


class ProjectEnv:
    """
    Handles all configurations for the test projects, creates them and finally calls the build.
    """
    def __init__(self, project_path: str, build_config: str, project_config: str, temp: str = None):
        if temp is not None and not os.path.exists(temp):
            raise ProjectException(f'Given temp folder does not exist: {temp}')

        self.project_path = project_path
        self.build_config = build_config
        self.project_config = project_config
        self.internal_data = {}

        self.source_path = project_path
        self.source_perf_conf_path = os.path.join(self.source_path, "performance.py")

        self.target_path = tempfile.mkdtemp(dir=temp)
        self.target_build_path = os.path.join(self.target_path, "_build")
        self.target_index_path = os.path.join(self.target_build_path, "index.html")
        self.target_req_path = os.path.join(self.target_path, "requirements.txt")

        self.python_path = sys.executable
        self.bin_path = os.path.dirname(self.python_path)
        self.pip_path = os.path.join(self.bin_path, 'pip')
        self.sphinx_path = os.path.join(self.bin_path, 'sphinx-build')

        self.extra_info = {}

    def config_is_valid(self) -> bool:
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

        # From here on several problems can occur, but we want to collect them all and print them all for the user.
        passed = True

        for param, default in conf_params.items():
            if param not in self.project_config:
                if default is not None:
                    self.project_config[param] = default
                else:
                    console.print(f'Missing parameter {{param}} in given config')
                    passed = False

        # Check if the config we need to create files and folders are given.
        for needed_conf in NEED_CONFIG_DEFAULT:
            if needed_conf not in self.project_config:
                console.print(f'Needed parameter "{needed_conf}" not provided by user and test project default')
                passed = False

        # We need some values later, so if they are not defined, lets already return.
        if not passed:
            return passed

        # Calculate some standard extra data, which is hard do get done via jinja2 in performance.py:
        # - amount of page files (depending on folders and depth)
        # - amount of index files (depending on folders and depth)
        page_amount = self.project_config['pages']
        index_amount = 1
        for x in range(1, self.project_config['depth'] + 1):
            page_amount += self.project_config['pages'] * (self.project_config['folders'] ** x)
            index_amount += self.project_config['folders'] ** x

        self.internal_data['page_amount'] = page_amount
        self.internal_data['index_amount'] = index_amount

        return passed

    def _render_file(self, source: str, target: str, has_folders=False, **kwargs) -> None:
        """
        Renders a given template and stores the result in a new file

        :param source: template path
        :param target: target path
        :param kwargs: any kind of keyword arguments, which shall be available in the template
        :return: None

        """
        global GLOBAL_PAGE_COUNTER
        GLOBAL_PAGE_COUNTER += 1

        source_tmp_path = os.path.join(self.target_path, source)
        source_tmp_path_final = os.path.join(self.target_path, target)
        template = Template(Path(source_tmp_path).read_text())
        rendered = template.render(**self.project_config,
                                   **self.build_config,
                                   **self.internal_data,
                                   has_folders=has_folders,
                                   global_page=GLOBAL_PAGE_COUNTER,
                                   **kwargs)
        with open(source_tmp_path_final, "w") as file:
            file.write(rendered)

    def _create_pages(self, folder: str ="", **kwargs):
        for p in range(self.project_config['pages']):
            title = f"Page {p}"
            file_path = os.path.join(folder, f"page_{p}.rst")

            self._render_file("page.template", file_path, title=title, page=p, **kwargs)

    def _create_folders(self, folder_root: str, current_depth: int = 1) -> None:
        """
        Creates folders and needed rst-files in it.
        Depending up on "depth", sub-folders will be created as well.

        :param folder_root: The current folder path to deal with
        :param current_depth: The currently reached depth of the folder structure
        :return: None
        """
        current_folder_path = os.path.join(self.target_path, folder_root)

        for f in range(self.project_config['folders']):
            new_folder_path = os.path.join(current_folder_path, f'folder_{f}')
            os.mkdir(new_folder_path)
            self._create_pages(new_folder_path, current_depth=current_depth)

            index_path = os.path.join(new_folder_path, "index.rst")
            self._render_file("index.template", index_path)

            title = f"Index folder {f} depth {current_depth}"
            if current_depth < self.project_config['depth']:
                self._render_file("index.template", index_path, has_folders=True, title=title)
                self._create_folders(new_folder_path, current_depth + 1)
            else:
                self._render_file("index.template", index_path, has_folders=False, title=title)

    def prepare_project(self):
        """
        Creates the temporary source folder, copies all needed files and calls Jinja2 for some of them.
        """
        # Calculate extra infos
        start_time = time.time()
        for name, result in self.extra_info.items():
            template = Template(result)
            self.extra_info[name] = template.render(**self.project_config,
                                                    **self.build_config,
                                                    **self.internal_data)

        conf_str = ', '.join([f'{key}: {value}' for key, value in self.project_config.items()])
        console.print(f"[bold]Core/s[/bold]:\t\t {self.build_config['parallel']}")
        console.print(f"[bold]Builder[/bold]:\t {self.build_config['builder']}")
        console.print(f"[bold]Config[/bold]:\t\t {conf_str}")
        info_str = ', '.join([f'{key}: {value}' for key, value in self.extra_info.items()])
        console.print(f"[bold]Info[/bold]:\t\t {info_str}")

        console.print(f"\n[bold]Docs path[/bold]:\t {self.target_path}")
        with console.status("Setting up documentation environment"):
            shutil.copytree(self.source_path, self.target_path, dirs_exist_ok=True)

            # Render files
            self._render_file("requirements.template", "requirements.txt")
            self._render_file("conf.template", "conf.py")

            title = "Performance Test main index"
            if self.project_config['folders'] > 0 and self.project_config['depth'] > 0:
                self._render_file("index.template", "index.rst", has_folders=True, title=title)
            else:
                self._render_file("index.template", "index.rst", has_folders=False, title=title)

            # Render and create pages on test project "root"
            self._create_pages(current_depth=0)

            self._create_folders("", 1)
        end_time = time.time()
        result_time = end_time - start_time
        file_data = self._calculate_file_numbers(self.target_path, ['.md', '.rst'])
        size = file_data['size_kb']
        max_size = file_data['max_size_kb']
        data_str = f"{file_data['count']} rst files with {size:.2f} kB"
        console.print(f"[bold]Docs files[/bold]:\t {data_str}")
        console.print(f"[bold]Docs setup[/bold]:\t {result_time:.2f} s\n")

    def _calculate_file_numbers(self, folder, file_types=["rst"]):
        total_size = 0
        total_count = 0
        max_size = 0
        max_file = ''
        min_size = -1
        min_file = ''

        for dirpath, dirnames, filenames in os.walk(folder):
            for f in filenames:
                # Measure file size, if file type matches or if no file types are given
                if not file_types or os.path.splitext(f)[1] in file_types:
                    total_count += 1
                    fp = os.path.join(dirpath, f)
                    size = os.path.getsize(fp)
                    total_size += size
                    if size > max_size:
                        max_size = size
                        max_file = fp
                    if min_size < 0 or min_size > size:
                        min_size = size
                        min_file = fp

        data = {
            "size": total_size,
            "size_kb": total_size/1024,
            "count": total_count,
            "max_size": max_size,
            "max_size_kb": max_size/1024,
            "max_file": max_file,
            "min_size": min_size,
            "min_size_kb": min_size / 1024,
            "min_file": min_file,
        }
        return data

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
        console.print(f"[bold]Deps setup[/bold]:\t {result_time:.2f} s")

    def build(self):
        """
        Build copied Sphnx project
        """
        if self.build_config['browser']:
            self.build_config['keep'] = True

        params = [
            self.sphinx_path,
            "-a",
            "-E",
            "-v",
            "-j",
            str(self.build_config['parallel']),
            "-b",
            str(self.build_config['builder']),
            self.target_path,
            self.target_build_path,
        ]

        if self.build_config['debug']:
            console.print(f'Call:\t\t {" ".join(params)} ')

        start_time = time.time()
        if self.build_config['debug']:
            console.rule('Building documentation START', style="blue")
            subprocess.run(params)
            console.rule('Building documentation FINISHED', style="blue")
        else:
            status_str = "Building documentation"
            status = console.status(status_str)
            with status:
                # process = subprocess.Popen(params, stdout=subprocess.DEVNULL)
                process = subprocess.Popen(params, stdout=subprocess.PIPE)

                reading_start_time = None
                reading_stop_time = None

                writing_start_time = None
                writing_stop_time = None

                while True:

                    # Measure reading and writing time
                    line = process.stdout.readline()
                    line = line.decode('utf8')
                    if 'reading sources' in line:
                        if reading_start_time is None:
                            reading_start_time = time.time()
                        reading_stop_time = time.time()

                    if 'writing output' in line:
                        if writing_start_time is None:
                            writing_start_time = time.time()
                        writing_stop_time = time.time()

                    # Check if project has finished
                    if process.poll() is not None:
                        break

                    # Update build time counter
                    current_time = time.time() - start_time
                    status.update(f'{status_str} {current_time:.2f} s')
                    time.sleep(0.005)

        end_time = time.time()

        file_data = self._calculate_file_numbers(self.target_build_path, [])
        size = file_data['size_kb']
        max_size = file_data['max_size_kb']
        min_size = file_data['min_size_kb']
        data_str = f"{file_data['count']} files with {size:.2f} kB"

        if not self.build_config['debug']:
            # Errors may happen here, if reading/writing could not be detected.
            # Maybe because of different output based of other builders.
            try:
                reading_time = reading_stop_time - reading_start_time
            except TypeError:
                reading_time = 0
            try:
                writing_time = writing_stop_time - writing_start_time
            except TypeError:
                writing_time = 0
        else:
            reading_time = 0
            writing_time = 0

        result_time = end_time - start_time
        console.print(f"\n[bold]Build files[/bold]:\t {data_str}")
        console.print(f"[bold]File max️[/bold]:\t  {max_size:.2f} kB by {file_data['max_file']}")
        console.print(f"[bold]File min[/bold]:\t {min_size:.2f} kB by {file_data['min_file']}")

        if file_data['count']:
            time_per_file = result_time / file_data['count']
            size_per_file = size / file_data['count']
        else:  # if no files got found
            time_per_file = 0
            size_per_file = 0

        console.print(f"[bold]File Ø[/bold]:\t\t {size_per_file:.2f} kB ({time_per_file:.2f} s)")
        console.print(f"[bold]Reading time[/bold]:\t {reading_time:.2f} s")
        console.print(f"[bold]Writing time[/bold]:\t {writing_time:.2f} s")
        console.print(f"[bold red]Build Duration[/bold red]:\t [bold red]{result_time:.2f} s")

        if not self.build_config['keep']:
            if self.build_config['debug']:
                console.print(f"\nDeleting project {self.target_build_path}")
            shutil.rmtree(self.target_build_path)
            shutil.rmtree(self.target_path)

        extra_results = {
            'reading time': f"{reading_time:.2f} s",
            'writing time': f"{writing_time:.2f} s",
            'folder size': f'{size:.2f} kB',
            '# files': f'{file_data["count"]}',
            'avg file time': f'{time_per_file:.2f} s',
            'avg file size': f'{size_per_file:.2f} kB',
            'max file size': f'{max_size:.2f} kB',
            'min file size': f'{min_size:.2f} kB',
        }

        return result_time, extra_results

    def post_processing(self):
        if self.build_config['browser']:
            with suppress(Exception):
                webbrowser.open_new_tab(self.target_index_path)


class ProjectException(BaseException):
    pass