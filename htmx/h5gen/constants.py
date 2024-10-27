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

TAGS = {
    t: (f"<{t}>", f"<{t} {{}}>", "" if t in NO_END_TAG else f"</{t}>")
    for t in TAG_NAMES
}

# Hard code html
TAGS["html"] = ("<!doctype html>\n<html>", "<!doctype html>\n<html {}>", "</html>")

PREFIXES = {"html": "<!doctype html>"}

DEFAULT_ENDL = "\n"

DEFAULT_INDENT = "  "
## HTMX

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
## Favicon

ICON_NULL = "data:;base64,iVBORw0KGgo="
PICOCSS_SOURCE = "https://cdn.jsdelivr.net/npm/@picocss/pico@2.0.6/css/pico.min.css"
