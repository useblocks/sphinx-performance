"""
Configuration to find Sphinx events sent to listeners/extensions.

The goal is to enable extension specific profiling reports.
"""

from __future__ import annotations

from pathlib import Path

from sphinx.events import EventManager as EventManagerOrig

# ruff: noqa: ANN002
#             (missing-type-args - type depends on event, however emit is generic)


class EventManager(EventManagerOrig):
    """
    Overwrite sphinx.events.EventManager.emit() to call an event specific variant.

    This is needed to collect profiling runtime per extension.
    Sphinx communicates with extensions through events.
    pyinstrument does not collect function arguments, so it is unclear which event
    got fired by EventManager.emit. Making the name event specific enables collection
    of runtime per extensions in a post processing step.

    The function is monkeypatched into sphinx.application.EventManager so it is used
    during Sphinx runtime without modifying Sphinx or extensions.
    """

    def emit(self, *args, **kwargs) -> list:
        """Overwritten method in super class."""
        event: str = args[0]
        event_identifier = event.replace("-", "_")
        func_name = f"emit_{event_identifier}"
        if hasattr(self, func_name):
            return getattr(self, func_name)(*args, **kwargs)
        msg = (
            f"The method for event {event} is not yet implemented. Expected"
            f" name: '{func_name}'"
        )
        raise NotImplementedError(msg)

    def emit_config_inited(self, *args, **kwargs):
        return super().emit(*args, **kwargs)

    def emit_builder_inited(self, *args, **kwargs):
        return super().emit(*args, **kwargs)

    def emit_env_get_outdated(self, *args, **kwargs):
        return super().emit(*args, **kwargs)

    def emit_env_before_read_docs(self, *args, **kwargs):
        return super().emit(*args, **kwargs)

    def emit_env_purge_doc(self, *args, **kwargs):
        return super().emit(*args, **kwargs)

    def emit_source_read(self, *args, **kwargs):
        return super().emit(*args, **kwargs)

    def emit_doctree_read(self, *args, **kwargs):
        return super().emit(*args, **kwargs)

    def emit_env_updated(self, *args, **kwargs):
        return super().emit(*args, **kwargs)

    def emit_env_get_updated(self, *args, **kwargs):
        return super().emit(*args, **kwargs)

    def emit_env_check_consistency(self, *args, **kwargs):
        return super().emit(*args, **kwargs)

    def emit_missing_reference(self, *args, **kwargs):
        return super().emit(*args, **kwargs)

    def emit_warn_missing_reference(self, *args, **kwargs):
        return super().emit(*args, **kwargs)

    def emit_doctree_resolved(self, *args, **kwargs):
        return super().emit(*args, **kwargs)

    def emit_html_page_context(self, *args, **kwargs):
        return super().emit(*args, **kwargs)

    def emit_html_collect_pages(self, *args, **kwargs):
        return super().emit(*args, **kwargs)

    def emit_build_finished(self, *args, **kwargs):
        return super().emit(*args, **kwargs)


events = [
    "builder-inited",
    "config-inited",
    "env-get-outdated",
    "env-purge-doc",
    "env-before-read-docs",
    "source-read",
    "object-description-transform",
    "doctree-read",
    "missing-reference",
    "warn-missing-reference",
    "doctree-resolved",
    "env-merge-info",
    "env-updated",
    "env-check-consistency",
    "html-collect-pages",
    "html-page-context",
    "linkcheck-process-uri",
    "build-finished",
]

frame_parents_by_event = {
    "builder-inited": [
        "Sphinx.__init__",
        "Sphinx._init_builder",
    ],
    "config-inited": [
        "Sphinx.__init__",
    ],
    "env-get-outdated": [],
    "env-purge-doc": [],
    "env-before-read-docs": [],
    "source-read": [
        "EventManager.emit_source_read",
    ],
    "object-description-transform": [],
    "doctree-read": [],
    "missing-reference": [],
    "warn-missing-reference": [],
    "doctree-resolved": [],
    "env-merge-info": [],
    "env-updated": [],
    "env-check-consistency": [],
    "html-collect-pages": [],
    "html-page-context": [],
    "linkcheck-process-uri": [],
    "build-finished": [
        "Sphinx.build",
        "",
    ],
}

event_frame = "EventManager.emit"


def aggregate_event_runtime(json_render_data):
    """Filter JSON tree for Sphinx events and add up the consumption time of subpackages."""
    event_functions_frames = {}
    for event in events:
        event_functions_frames[event] = [
            f"EventManager.emit_{event.replace('-', '_')}",
            "EventManager.emit",
        ]
    out_obj = {}
    active_events = {}
    filter_frame_tree(
        json_render_data["root_frame"],
        event_functions_frames,
        active_events,
        out_obj,
    )
    return out_obj


def filter_frame_tree(
    data_obj: dict[str, dict],
    frames_by_event: dict[str, list],
    active_events,
    out_obj,
):
    """
    Recursively walk the JSON tree looking for event related functions.

    All sub-package (extension) invocations are aggregated for the event.
    """
    if "class_name" in data_obj:
        data_obj_qualifier = f"{data_obj['class_name']}.{data_obj['function']}"
    else:
        data_obj_qualifier = data_obj["function"]
    for event, frames in active_events.items():
        if data_obj_qualifier == frames[0]:
            # remove the frame
            active_events[event] = frames[1:]
        else:
            # deactivate the event, not all frames matched
            del active_events[event]

    for event, frames in frames_by_event.items():
        if event not in active_events and data_obj_qualifier == frames[0]:
            active_events[event] = frames[1:]

    collect_events = [
        event for event, frames in active_events.items() if len(frames) == 0
    ]
    for event in collect_events:
        if event not in out_obj:
            out_obj[event] = {}
        for child in data_obj["children"]:
            if "class_name" in child:
                out_qualifier = f"{child['class_name']}.{child['function']}"
            else:
                out_qualifier = child["function"]
            library = Path(child["file_path_short"]).parts[0]
            full_qualifier = f"{library}: {out_qualifier}"
            if full_qualifier not in out_obj[event]:
                out_obj[event][full_qualifier] = 0
            out_obj[event][full_qualifier] += child["time"]
        # event is handled, delete it
        del active_events[event]

    for child in data_obj["children"]:
        filter_frame_tree(child, frames_by_event, active_events, out_obj)
