"""
Configuration to find Sphinx events sent to listeners/extensions.

The goal is to enable extension specific profiling reports.
"""
# ruff: noqa: ANN002
#             (missing-type-args - type depends on event, however emit is generic)
from sphinx.events import EventManager as EventManagerOrig


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
    "source-read": [],
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


def patch_json_renderer(json_render_data):
    pass
