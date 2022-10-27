"""
Takes the cli arguments and options, verifies them and creates a Call object,
which contains all needed information.
"""
import itertools
import os
import sys

from sphinx_performance.config import PROJECTS
from sphinx_performance.utils import console


class Call:
    def __init__(self, projects, ctx_args, build_kwargs):
        self.projects = projects
        self.ctx_args = ctx_args
        self.build_kwargs = build_kwargs

        self.project_path = self._get_project_paths(self.projects)
        self.project_kwargs = self._get_project_kwargs(ctx_args)
        self.project_configs = self._create_project_configs(self.project_kwargs)
        self.build_configs = self.create_build_config(self.build_kwargs)

    @property
    def runs(self):
        return len(self.projects) * len(self.build_configs) * len(self.project_configs)

    def _get_project_paths(self, projects):
        """Figures out the correct project path and if it is valid."""
        project_path = {}
        for project in projects:
            if project not in PROJECTS:
                if not os.path.exists(project):
                    console.print(f'Project {project} not found')
                    sys.exit(1)
                project_path[project] = os.path.abspath(project)
            else:
                project_path[project] = PROJECTS[project]
        return project_path

    def _get_project_kwargs(self, ctx_args):
        """Handles the kwargs"""
        project_kwargs = {}
        for i in range(0, len(ctx_args), 2):
            name = ctx_args[i][2:]
            if name not in project_kwargs:
                project_kwargs[name] = []
            value = ctx_args[i + 1]
            try:
                value = int(value)
            except ValueError:
                pass
            project_kwargs[name].append(value)
        return project_kwargs

    def _create_project_configs(self, project_kwargs):
        project_configs = [{}]
        if project_kwargs:
            # Create project config test matrix
            keys, values = zip(*self.project_kwargs.items())
            project_configs = [dict(zip(keys, v)) for v in itertools.product(*values)]
        return project_configs

    def create_build_config(self, build_kwargs):
        # Create build test matrix
        keys, values = zip(*build_kwargs.items())
        build_configs = [dict(zip(keys, v)) for v in itertools.product(*values)]
        return build_configs

