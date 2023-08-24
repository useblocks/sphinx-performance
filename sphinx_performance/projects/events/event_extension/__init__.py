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
        sleep(.1)
        # print("func '{func_name}' invoked for event '{event}'")
        return {ret_val}""",
    )
    return locals().get(func_name)


def setup(app: Sphinx) -> dict[str, Any]:
    """Entry point for Sphinx."""
    # Make connections to events
    events = [
        ["builder-inited"],  # invoked
        ["config-inited"],  # invoked
        ["env-get-outdated", []],  # invoked
        ["env-purge-doc"],  # invoked
        ["env-before-read-docs"],  # invoked
        ["source-read"],  # invoked
        ["object-description-transform"],
        ["doctree-read"],  # invoked
        ["missing-reference"],  # invoked
        ["warn-missing-reference"],  # invoked
        ["doctree-resolved"],  # invoked
        ["env-merge-info"],  # invoked
        ["env-updated"],  # invoked
        ["env-check-consistency"],  # invoked
        ["html-collect-pages", []],  # invoked
        ["html-page-context"],  # invoked
        ["linkcheck-process-uri"],
        ["build-finished"],  # invoked
    ]
    for event in events:
        app.connect(event[0], wait_generic(*event))

    return {
        "version": "0.1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
