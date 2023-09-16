"""Overwrite pyinstrument HTMLRenderer so it accepts a JSON object."""

import inspect
from pathlib import Path

from pyinstrument.renderers.html import HTMLRenderer


class HTMLRendererFromJson(HTMLRenderer):
    def render(self, session_json: str):
        path_html_renderer = inspect.getfile(HTMLRenderer)
        resources_dir = Path(path_html_renderer).parent / "html_resources"

        js_file = resources_dir / "app.js"
        css_file = resources_dir / "app.css"

        if not js_file.exists() or not css_file.exists():
            msg = (
                "Could not find app.js / app.css. Perhaps you need to run"
                " bin/build_js_bundle.py?"
            )
            raise RuntimeError(
                msg,
            )

        js = js_file.read_text()
        css = css_file.read_text()

        return f"""<!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
            </head>
            <body>
                <div id="app"></div>

                <script>{js}</script>
                <style>{css}</style>

                <script>
                    const sessionData = {session_json};
                    pyinstrumentHTMLRenderer.render(document.getElementById('app'), sessionData);
                </script>
            </body>
            </html>
        """
