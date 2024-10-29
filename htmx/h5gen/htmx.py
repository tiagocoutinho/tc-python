from h5gen.constants import ICON_NULL
from h5gen.functions import (
    Script,
    Html,
    Head,
    Title,
    Body,
    JS,
    Favicon,
    utf_8,
    viewport,
)


HTMX_UNPKG_SOURCE = "https://unpkg.com/htmx.org@2.0.3/dist/htmx.min.js"
HTMX_UNPKG_EXT_TEMPLATE = "https://unpkg.com/htmx-ext-{name}@{version}/{name}.js".format
HTMX_JSDELIVR_SOURCE = "https://cdn.jsdelivr.net/npm/htmx.org@2.0.3/dist/htmx.min.js"
HTMX_JSDELIVR_EXT_TEMPLATE = (
    "https://cdn.jsdelivr.net/npm/htmx-ext-{name}@{version}/{name}.js".format
)
HTMX_EXTENSIONS = {
    "preload": {
        "url": HTMX_JSDELIVR_EXT_TEMPLATE(name="preload", version="2.0.1"),
        "ext_name": "preload",
    },
}


def HtmxScript(defer=True, **kwargs):
    return Script(src=HTMX_JSDELIVR_SOURCE, defer=defer, **kwargs)


def HtmxExt(name, defer=True, **kwargs):
    return Script(src=HTMX_EXTENSIONS[name]["url"], defer=defer, **kwargs)


def Htmx(
    *payload,
    title="h5gen page",
    icon=ICON_NULL,
    extra_headers=(),
    extensions=(),
    lang="en",
    body_attrs=None,
    debug=False,
):
    """Helper that creates an HTML document with prepared HTMX headers

    Args:
        payload (str): body content
        title (str, optional): Page title. Defaults to "h5gen page".
        icon (_type_, optional): page fav icon. Defaults to null icon.
        extra_headers (tuple, optional): _description_. Defaults to ().
        extensions (tuple, optional): _description_. Defaults to ().
        body_attrs (dict, optional): extra body attrs (ex: `{"class": "body"}`)
    Returns:
        _type_: _description_
    """
    scripts = [HtmxScript()]
    if body_attrs is None:
        body_attrs = {}
    if extensions:
        hx_exts = set()
        for extension in extensions:
            ext = HTMX_EXTENSIONS[extension]
            hx_exts.add(ext["ext_name"])
            scripts.append(HtmxExt(extension))
        body_attrs["hx-ext"] = ",".join(hx_exts)
    if debug:
        debug = JS(
            "document.body.addEventListener('htmx:load', function(evt) {htmx.logAll();});"
        )
        payload = (*payload, debug)
    body = Body(*payload, **body_attrs)
    return Html(
        Head(
            Title(title),
            Favicon(icon),
            utf_8,
            viewport,
            *scripts,
            *extra_headers,
        ),
        body,
        lang=lang,
    )
