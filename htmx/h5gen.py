import functools
import types

TAG_NAMES = [
    "a",
    "abbr",
    "address",
    "area",
    "article",
    "aside",
    "audio",
    "b",
    "base",
    "bdi",
    "bdo",
    "blockquote",
    "body",
    "br",
    "button",
    "canvas",
    "caption",
    "cite",
    "code",
    "col",
    "colgroup",
    "data",
    "datalist",
    "dd",
    "del",
    "details",
    "dfn",
    "dialog",
    "div",
    "dl",
    "dt",
    "em",
    "embed",
    "fieldset",
    "figcaption",
    "figure",
    "footer",
    "form",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "head",
    "header",
    "hr",
    "html",
    "i",
    "iframe",
    "img",
    "input",
    "ins",
    "kbd",
    "label",
    "legend",
    "li",
    "link",
    "main",
    "map",
    "mark",
    "meta",
    "meter",
    "nav",
    "noscript",
    "object",
    "ol",
    "optgroup",
    "option",
    "output",
    "p",
    "param",
    "picture",
    "pre",
    "progress",
    "q",
    "rp",
    "rt",
    "ruby",
    "s",
    "samp",
    "script",
    "section",
    "select",
    "small",
    "source",
    "span",
    "strong",
    "style",
    "sub",
    "summary",
    "sup",
    "svg",
    "table",
    "tbody",
    "td",
    "template",
    "textarea",
    "tfoot",
    "th",
    "thead",
    "time",
    "title",
    "tr",
    "track",
    "u",
    "ul",
    "var",
    "video",
    "wbr",
]

NO_END_TAG = {"link", "meta"}


def render_attr(key, value):
    return key if value is True else f'{key}="{value}"'


def render_attrs(options):
    return " ".join(render_attr(k, v) for k, v in options.items() if v is not False)


def render_simple(tag, children, attrs) -> str:
    children = "".join(children)
    attrs = render_attrs(attrs)
    start = f"<{tag} {attrs}>" if attrs else f"<{tag}>"
    end = "" if tag in NO_END_TAG else f"</{tag}>"
    return f"{start}{children}{end}"


def iter_render_pretty(elem, level=0, indent="  ", endl="\n"):
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
        yield from iter_render_pretty(child, level + 1, indent, endl)
    yield f"{prefix}{etag}{endl}"


def render_pretty(elem, level=0, indent="  ", endl="\n"):
    return f"{elem.prefix}{endl}" + "".join(
        iter_render_pretty(elem, level=level, indent=indent, endl=endl)
    )


def py_dict_to_attrs(attrs: dict[str, str]) -> dict[str, str]:
    return {name.strip("_").replace("_", "-"): value for name, value in attrs.items()}


class Element:
    __slots__ = ["children", "attrs"]

    tag = ""
    prefix = ""

    def __init__(self, *children, **attrs):
        self.children = children
        self.attrs = py_dict_to_attrs(attrs)

    def __str__(self):
        return self.prefix + render_simple(
            self.tag, (str(child) for child in self.children), self.attrs
        )

    def __getitem__(self, key):
        if isinstance(key, tuple):
            return tuple(self[k] for k in key)
        if isinstance(key, (int, slice)):
            return self.children[key]
        return self.attrs[key]


def _fill_tags(d):
    for name in TAG_NAMES:
        klass = types.new_class(name, (Element,))
        klass.tag = name
        d[name.capitalize()] = klass


_fill_tags(locals())

Html.prefix = "<!doctype html>"


## H