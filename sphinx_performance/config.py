import os

PROJECTS = {
    "basic": os.path.join(os.path.dirname(__file__), "projects", "basic"),
    "needs": os.path.join(os.path.dirname(__file__), "projects", "needs"),
    "theme": os.path.join(os.path.dirname(__file__), "projects", "theme")
}

RUNTIME_PROFILE = 'runtime_all.prof'
MEMORY_PROFILE = 'memray_all.prof'
MEMORY_HTML = 'memray_all.html'

MEMRAY_PORT = 13167