__all__ = [
    "CSS",
    "JS",
    "Checkbox",
    "Favicon",
    "favicon_null",
    "Viewport",
    "viewport",
    "utf_8",
]
import functools

from h5gen.constants import DEFAULT_ENDL, DEFAULT_INDENT, TAGS

ENDL_INDENT = DEFAULT_ENDL + DEFAULT_INDENT


def render_attr(key, value):
    if key == "cls":
        key = "class"
    else:
        key = key.strip("_").replace("_", "-")
    return key if value is True else f'{key}="{value}"'


def render_attrs(options):
    return " ".join(render_attr(k, v) for k, v in options.items())


def iter_render(tag, children, attrs):
    attrs = render_attrs(attrs)
    start, start_with_attrs, end = TAGS[tag]
    start = start_with_attrs.format(attrs) if attrs else start

    if not children:
        yield f"{start}{end}"
        return

    if len(children) == 1 and not children[0].startswith("<"):
        yield f"{start}{children[0]}{end}"
        return

    yield start
    for child in children:
        local_child = child.replace(DEFAULT_ENDL, ENDL_INDENT)
        yield f"{DEFAULT_INDENT}{local_child}"
        if not child.startswith("<"):
            yield ""
    yield end


def _render(tag, children, attrs):
    return DEFAULT_ENDL.join(iter_render(tag, children, attrs))


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
