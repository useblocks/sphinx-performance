"""
Extension that connects to all Sphinx events and sleeps in those.

Can be used to test the debuggers.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sphinx.application import Sphinx


def wait_generic(event, ret_val=None):
    """Wait for a short time so debuggers see the event fired."""
    # generate event specific wait function name
    event_identifier = event.replace("-", "_")
    func_name = f"wait_{event_identifier}"
    exec(
        f"""def {func_name}(*args, **kwargs):
        from time import sleep
        sleep(.5)
        return {ret_val}""",
    )
    return locals().get(func_name)


def setup(app: Sphinx) -> dict[str, Any]:
    """Entry point for Sphinx."""
    # Make connections to events
    events = [
        ["builder-inited"],
        ["config-inited"],
        ["env-get-outdated", []], # *
        ["env-purge-doc"], # *
        ["env-before-read-docs"], # *
        ["source-read"],  # *
        ["object-description-transform"],
        ["doctree-read"],  # *
        ["missing-reference"], # *
        ["warn-missing-reference"], # *
        ["doctree-resolved"], # *
        ["env-merge-info"],
        ["env-updated"], # *
        ["env-check-consistency"], # *
        ["html-collect-pages", []], # *
        ["html-page-context"], # *
        ["linkcheck-process-uri"],
    ]
    for event in events:
        app.connect(event[0], wait_generic(*event))
