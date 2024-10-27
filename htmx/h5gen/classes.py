import functools
import types

from h5gen.constants import HTMX_EXTENSIONS, HTMX_JSDELIVR_SOURCE, ICON_NULL, NO_END_TAG, PICOCSS_SOURCE, TAG_NAMES
from h5gen.tools import render_attrs


def iter_render(elem, level=0, indent="  ", endl="\n"):
    prefix = level * indent
    if isinstance(elem, str):
        yield f"{prefix}{elem}{endl}"
        return
    tag = elem.tag
    etag = "" if tag in NO_END_TAG else f"</{elem.tag}>"
    attrs = render_attrs(elem.attrs)
    children = elem.children
    start = f"{prefix}<{tag} {attrs}>" if attrs else f"{prefix}<{tag}>"

    if not children:
        yield f"{start}{etag}{endl}"
        return

    if len(children) == 1 and isinstance(children[0], str):
        yield f"{start}{children[0]}{etag}{endl}"
        return
    yield f"{start}{endl}"
    for child in children:
        yield from iter_render(child, level + 1, indent, endl)
    yield f"{prefix}{etag}{endl}"


def render(elem, level=0, indent="  ", endl="\n"):
    return f"{elem.prefix}{endl}" + "".join(
        iter_render(elem, level=level, indent=indent, endl=endl)
    )


class Element:
    __slots__ = ["children", "attrs"]

    tag = ""
    prefix = ""

    def __init__(self, *children, **attrs):
        self.children = children
        self.attrs = attrs

    def __str__(self):
        return render(self, 0, "", "")

    def __getitem__(self, key):
        if isinstance(key, tuple):
            return tuple(self[k] for k in key)
        if isinstance(key, (int, slice)):
            return self.children[key]
        return self.attrs[key]


def _fill_tags():
    result = {}
    for name in TAG_NAMES:
        klass = types.new_class(name, (Element,))
        klass.tag = name
        result[name.capitalize()] = klass
    return result


locals().update(_fill_tags())

Html.prefix = "<!doctype html>"

Checkbox = functools.partial(Input, type="checkbox")

def Favicon(href, type="image/x-icon", **kwargs):
    return Link(rel="icon", href=href, type=type, **kwargs)


favicon_null = Favicon("data:;base64,iVBORw0KGgo=")

## Metas

Viewport = functools.partial(Meta, name="viewport")

utf_8 = Meta(charset="utf-8")
viewport = Viewport(content="width=device-width, initial-scale=1")

## Javascript

JS = functools.partial(Script, type="text/javascript")

def HtmxScript(defer=True, **kwargs):
    return Script(src=HTMX_JSDELIVR_SOURCE, defer=defer, **kwargs)


def HtmxExtension(name, defer=True, **kwargs):
    return Script(src=HTMX_EXTENSIONS[name]["url"], defer=defer, **kwargs)


def Htmx(
    body, title="h5gen page", icon=ICON_NULL, extra_headers=(), extensions=(), lang="en"
):
    """Helper that creates an HTML document with prepared HTMX headers

    Args:
        body (Body): an instance of Body
        title (str, optional): Page title. Defaults to "h5gen page".
        icon (_type_, optional): page fav icon. Defaults to null icon.
        extra_headers (tuple, optional): _description_. Defaults to ().
        extensions (tuple, optional): _description_. Defaults to ().

    Returns:
        _type_: _description_
    """
    scripts = [HtmxScript()]
    if extensions:
        hx_exts = {
            name.strip()
            for name in body.attrs.get("hx-ext", "").split(",")
            if name.strip()
        }
        for extension in extensions:
            ext = HTMX_EXTENSIONS[extension]
            hx_exts.add(ext["ext_name"])
            scripts.append(HtmxExtension(extension))
        print(hx_exts)
        body.attrs["hx-ext"] = ",".join(hx_exts)
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


def Css(href, **kwargs):
    return Link(rel="stylesheet", href=href, **kwargs)


# Pico CSS

pico_css = Css(href=PICOCSS_SOURCE)

pico_css_style = Style("""
button {
    --pico-form-element-spacing-horizontal: 0.5rem;
    --pico-form-element-spacing-vertical: 0.2rem;
}
""")