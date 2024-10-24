import types
from collections.abc import Iterable


def render_attr(key: str, value):
    if value is True:
        return key
    elif value is False:
        return ""
    return f'{key}="{value}"'


def render_attrs(options):
    return " ".join(render_attr(k, v) for k, v in options.items())


def render_simple(tag: str, children: Iterable[str], attrs) -> str:
    children = "".join(children)
    attrs = render_attrs(attrs)
    if children:
        start = f"<{tag} {attrs}>" if attrs else f"<{tag}>"
        return f"{start}{children}</{tag}>"
    return f"<{tag} {attrs}/>"


class Tag:
    def __init__(self, name):
        self.name = name
    
    def render(self, *children, **options):
        return render_simple(self.name, children, options)

    __call__ = render


def pretty_render(elem, level=0, indent="  ", endl="\n"):
    prefix = level * indent
    if isinstance(elem, str):
        return f"{prefix}{elem}"
    tag = elem.tag
    attrs = render_attrs(elem.attrs)
    children = elem.children
    if children:
        start = f"{prefix}<{tag} {attrs}>" if attrs else f"{prefix}<{tag}>"
        if len(children) == 1 and isinstance(children[0], str):
            return f"{start}{children[0]}</{tag}>"
        children = endl.join(pretty_render(child, level+1, indent, endl) for child in children)
        return f"{start}{endl}{children}{endl}{prefix}</{tag}>"
    return f"{prefix}<{tag} {attrs}/>"


class Element:
    tag = "None"
    __slots__ = ["children", "attrs"]

    def __init__(self, *children, **attrs):
        self.children = children
        self.attrs = attrs

    def __str__(self):
        return render_simple(self.tag, (str(child) for child in self.children), self.attrs)


TAG_NAMES = [
    "a", "abbr", "address", "area", "article", "aside", "audio", "b", "base", "bdi", "bdo",
    "blockquote", "body", "br", "button", "canvas", "caption", "cite", "code", "col", "colgroup",
    "data", "datalist", "dd", "del", "details", "dfn", "dialog", "div", "dl", "dt", "em", "embed",
    "fieldset", "figcaption", "figure", "footer", "form", "h1", "h2", "h3", "h4", "h5", "h6",
    "head", "header", "hr", "html", "i", "iframe", "img", "input", "ins", "kbd", "label", "legend",
    "li", "link", "main", "map", "mark", "meta", "meter", "nav", "noscript", "object", "ol", "optgroup",
    "option", "output", "p", "param", "picture", "pre", "progress", "q", "rp", "rt", "ruby", "s", "samp",
    "script", "section", "select", "small", "source", "span", "strong", "style", "sub", "summary", "sup",
    "svg", "table", "tbody", "td", "template", "textarea", "tfoot", "th", "thead", "time", "title", "tr",
    "track", "u", "ul", "var", "video", "wbr"
]

def _fill_tags(d):
    for name in TAG_NAMES:
        klass = types.new_class(name, (Element,))
        klass.tag = name.upper()
        d[name] = klass
        name = name.upper()
        d[name] = Tag(name)


_fill_tags(locals())


def main():
    html = HTML(
        HEAD(
            TITLE("Hello!"),
            SCRIPT(src="/bla"),
            LINK(href="", rel="", defer=True)
        )
    )
    print(html)


def sample():
    return html(
        head(
            title('Sample Page'),
            link(rel='stylesheet', href='style.css'),
            script(src="https://unpkg.com/htmx.org@2.0.3", defer=True)
        ),
        body(
            h1('Welcome to My Website'),
            p('This is a paragraph.'),
            div(
                p('Another paragraph inside a div.'),
                id='content',
            )
        )
    )

def main2(level=0, indent="  ", end="\n"):
    print(80*"=")
    doc = sample()
    print(doc)
    print(80*"=")
    print(pretty_render(doc, level, indent, end))
    print(80*"=")


if __name__ == "__main__":
    main2()