import math
from h5gen.constants import ICON_NULL
from h5gen.functions import (
    Script,
    Html,
    Head,
    Title,
    Body,
    Caption,
    Table,
    Tr,
    Td,
    Th,
    Tbody,
    Thead,
    Tfoot,
    Button,
    Div,
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


def calculate_window(center, window_size, min_value, max_value):
    # Ensure window size is odd to keep the center in the middle
    if window_size % 2 == 0:
        raise ValueError("Window size must be an odd number.")

    half_window = window_size // 2
    # Calculate start and end of the window
    start = max(center - half_window, min_value)
    end = min(center + half_window, max_value)

    # Adjust start and end if window is smaller than specified size
    if end - start + 1 < window_size:
        if start == min_value:
            end = min(start + window_size - 1, max_value)
        elif end == max_value:
            start = max(end - window_size + 1, min_value)

    return range(start, end + 1)


def HXTableButton(*items, disabled=False, role="button", **kwargs):
    if disabled:
        kwargs["disabled"] = True
    if role:
        kwargs["role"] = role
    return Button(*[str(i) for i in items], **kwargs)


def HXTable(
    id, rows, page, page_size, total_rows, url, headers=None, caption=None
):
    args = []
    if caption:
        args.append(Caption(caption))
    if headers is not None:
        head = Thead(Tr(*(Th(cell) for cell in headers)))
        args.append(head)
    body =Tbody(*(Tr(*[Td(col) for col in row]) for row in rows))
    args.append(body)

    total_columns = len(headers)
    nb_pages = math.ceil(total_rows / page_size)
    user_page = page + 1

    def btn(text, page, **kwargs):
        return HXTableButton(
            text,
            hx_get=f"{url}?page={page}&page_size={page_size}",
            hx_target=f"#{id}",
            hx_swap="outerHTML",
            **kwargs,
        )

    NB_PAGE_BUTTONS = 5
    page_buttons = (
        btn(i + 1, i, cls="" if i == page else "current-page-button", disabled=i == page)
        for i in calculate_window(page, NB_PAGE_BUTTONS, 0, nb_pages - 1)
    )

    previous_page_group = max(0, page - NB_PAGE_BUTTONS)
    previous_page = max(0, page - 1)
    next_page = min(nb_pages - 1, page + 1)
    next_page_group = min(nb_pages - 1, page + NB_PAGE_BUTTONS)
    buttons = (
        btn(3*"&lt;", 0, disabled=page == 0, data_tooltip="Go to fist page"),
        btn(2*"&lt;", previous_page_group, disabled=page == 0, data_tooltip=f"Back to page {previous_page_group + 1}"),
        btn(1*"&lt;", previous_page, disabled=page == 0, data_tooltip=f"Go to page {previous_page + 1}"),
        *page_buttons,
        btn(1*"&gt;", next_page, disabled=user_page >= nb_pages, data_tooltip=f"Go to page {next_page + 1}"),
        btn(
            2*"&gt;",
            next_page_group,
            disabled=user_page >= nb_pages,
            data_tooltip=f"Forward to page {next_page_group + 1}"
        ),
        btn(3*"&gt;", nb_pages - 1, disabled=user_page >= nb_pages, data_tooltip=f"Go to last page ({nb_pages})"),
    )

    pagination = Td(
        Div(
            *buttons,
            role="group",
        ),
        colspan=total_columns - 1,
    )
    args.append(Tfoot(Tr(Th(f"Total: {total_rows}"), pagination)))
    return Table(*args, id=id)
