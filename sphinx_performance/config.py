"""Internal configuration."""
from pathlib import Path

PROJECTS = {
    "basic": Path(Path(__file__).parent) / "projects" / "basic",
    "events": Path(Path(__file__).parent) / "projects" / "events",
    "needs": Path(Path(__file__).parent) / "projects" / "needs",
    "theme": Path(Path(__file__).parent) / "projects" / "theme",
}

RUNTIME_PROFILE = "runtime_all.prof"
MEMORY_PROFILE = "memray_all.prof"
MEMORY_HTML = "memray_all.html"

MEMRAY_PORT = 13167
