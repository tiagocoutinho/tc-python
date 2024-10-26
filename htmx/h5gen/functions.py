import textwrap

from h5gen.constants import NO_END_TAG, TAG_NAMES, PREFIXES
from h5gen.tools import render_attrs


def render_simple(tag, children, attrs) -> str:
    children = "".join(children)
    attrs = render_attrs(attrs)
    start = f"<{tag} {attrs}>" if attrs else f"<{tag}>"
    end = "" if tag in NO_END_TAG else f"</{tag}>"
    return f"{start}{children}{end}"


def iter_render(tag, children, attrs, indent="  ", endl="\n"):
    prefix = PREFIXES.get(tag)
    prefix = f"{prefix}{endl}" if prefix else ""
    etag = "" if tag in NO_END_TAG else f"</{tag}>"
    attrs = render_attrs(attrs)
    start = f"{prefix}<{tag} {attrs}>" if attrs else f"{prefix}<{tag}>"

    if not children:
        yield f"{start}{etag}{endl}"
        return

    yield f"{start}{endl}"
    for child in children:
        yield textwrap.indent(child, indent)
        if not child.startswith("<"):
            yield endl

    yield f"{etag}{endl}"


def render(tag, children, attrs, indent="  ", endl="\n"):
    return "".join(iter_render(tag, children, attrs, indent=indent, endl=endl))


def create_element(tag_name):
    def f(*children, **attrs):
        return render(tag_name, children, attrs)
    f.__name__ = tag_name
    return f


def create_elements(tag_names):
    return {tag_name: create_element(tag_name) for tag_name in tag_names}


locals().update(create_elements(TAG_NAMES))