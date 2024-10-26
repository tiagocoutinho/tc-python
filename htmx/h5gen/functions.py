
__all__ = []

from h5gen.constants import DEFAULT_ENDL, DEFAULT_INDENT, NO_END_TAG, TAG_NAMES, PREFIXES
from h5gen.tools import render_attrs

ENDL_INDENT = DEFAULT_ENDL + DEFAULT_INDENT


def _iter_render(tag, children, attrs):
    if prefix := PREFIXES.get(tag):
        yield prefix
    attrs = render_attrs(attrs)
    start = f"<{tag} {attrs}>" if attrs else f"<{tag}>"
    end = "" if tag in NO_END_TAG else f"</{tag}>"

    n = len(children)
    if not n:
        yield f"{start}{end}"
        return
    
    if n == 1 and not children[0].startswith("<"):
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
    def f(*children, **attrs):
        return _render(tag_name, children, attrs)
    f.__name__ = tag_name
    __all__.append(tag_name)
    return f


def _create_elements(tag_names):
    return {tag_name: _create_element(tag_name) for tag_name in tag_names}


locals().update(_create_elements(TAG_NAMES))
