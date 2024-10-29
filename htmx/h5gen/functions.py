__all__ = [
    "CSS",
    "JS",
    "Checkbox",
    "Favicon",
    "favicon_null",
    "Viewport",
    "viewport",
    "utf_8",
    "HtmxScript",
    "HtmxExt",
    "Htmx",
]
import functools

from h5gen.constants import (
    DEFAULT_ENDL,
    DEFAULT_INDENT,
    HTMX_EXTENSIONS,
    HTMX_JSDELIVR_SOURCE,
    ICON_NULL,
    PICOCSS_SOURCE,
    TAGS,
)
from h5gen.tools import render_attrs

ENDL_INDENT = DEFAULT_ENDL + DEFAULT_INDENT


def _iter_render(tag, children, attrs):
    attrs = render_attrs(attrs)
    start, start_with_attrs, end = TAGS[tag]
    start = start_with_attrs.format(attrs) if attrs else start

    if not children:
        yield f"{start}{end}"
        return

    if len(children) == 1 and not children[0].startswith("<"):
        yield f"{start}{children[0]}{end}"
        return

    yield f"{start}"
    for child in children:
        yield child.replace(DEFAULT_ENDL, ENDL_INDENT)
        if not child.startswith("<"):
            yield ""
    yield end


def _render(tag, children, attrs):
    return DEFAULT_ENDL.join(_iter_render(tag, children, attrs))


def _create_element(tag_name):
    fname = tag_name.capitalize()

    def f(*children, **attrs):
        return _render(tag_name, children, attrs)

    f.__name__ = fname
    __all__.append(fname)
    return f


def _create_elements():
    return {tag_name.capitalize(): _create_element(tag_name) for tag_name in TAGS}


locals().update(_create_elements())


# Some helpers


def CSS(*children, **attrs):
    if not children and "href" in attrs:
        attrs.setdefault("rel", "stylesheet")
        return Link(**attrs)
    return Style(*children, **attrs)


JS = functools.partial(Script, type="text/javascript")
Checkbox = functools.partial(Input, type="checkbox")
HiddenInput = functools.partial(Input, type="hidden")

def Favicon(href, type="image/x-icon", **kwargs):
    return Link(rel="icon", href=href, type=type, **kwargs)


favicon_null = Favicon("data:;base64,iVBORw0KGgo=")

## Metas

utf_8 = Meta(charset="utf-8")

Viewport = functools.partial(Meta, name="viewport")
viewport = Viewport(content="width=device-width, initial-scale=1")

# HTMX


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


# Pico CSS

pico_css = CSS(href=PICOCSS_SOURCE)

pico_css_style = Style("""
button {
    --pico-form-element-spacing-horizontal: 0.5rem;
    --pico-form-element-spacing-vertical: 0.2rem;
}
""")
