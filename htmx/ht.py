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

def render(tag: str, children: Iterable[str], attrs) -> str:
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
        return render(self.name, children, options)

    __call__ = render


class Element:
    def __init__(self, *children, **attrs):
        self.children = children
        self.attrs = attrs
    
    @staticmethod
    def render_child(c):
        return c if isinstance(c, str) else c.render()

    def render(self):
        children = (self.render_child(child) for child in self.children)
        tag = type(self).__name__
        return render(tag, children, self.attrs)


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
        d[name] = types.new_class(name, (Element,))

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


def main2():
    doc = html(
        head(
            title("Hello!"),
            script(src="/bla"),
            link(href="", rel="", defer=True)
        )
    )
    print(doc.render())


if __name__ == "__main__":
    main()