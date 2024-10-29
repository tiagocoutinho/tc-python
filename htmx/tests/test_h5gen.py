from regex import D
from h5gen import Html, Head, Title, Link, Script, Body, H1, P, I, Div, render


SAMPLE = Html(
    Head(
        Title("Sample Page"),
        Link(rel="stylesheet", href="style.css"),
        Script(src="https://unpkg.com/htmx.org@2.0.3", defer=True, dont_show=False),
    ),
    Body(
        H1("Welcome to My Website"),
        P("This is a paragraph."),
        Div(
            P("Another paragraph inside an ", I("italic"), " div."),
            id="content",
        ),
    ),
)

EXPECTED_SAMPLE_RENDER = """<!doctype html><html><head><title>Sample Page</title><link rel="stylesheet" href="style.css"><script src="https://unpkg.com/htmx.org@2.0.3" defer></script></head><body><h1>Welcome to My Website</h1><p>This is a paragraph.</p><div id="content"><p>Another paragraph inside an <i>italic</i> div.</p></div></body></html>"""
# <!doctype html><html><head><title>Sample Page</title><link rel="stylesheet" href="style.css"><script src="https://unpkg.com/htmx.org@2.0.3" defer ></script></head><body><h1>Welcome to My Website</h1><p>This is a paragraph.</p><div id="content"><p>Another paragraph inside an <i>italic</i> div.</p></div></body></html>                     # <!doctype html><html><head><title>Sample Page</{tag}><link rel="stylesheet" href="style.css"><script src="https://unpkg.com/htmx.org@2.0.3" defer ></{tag}></{tag}><body><h1>Welcome to My Website</{tag}><p>This is a paragraph.</{tag}><div id="content"><p>Another paragraph inside an <i>italic</{tag}> div.</{tag}></{tag}></{tag}></{tag}>
EXPECTED_SAMPLE_RENDER_PRETTY = """\
<!doctype html>
<html>
  <head>
    <title>Sample Page</title>
    <link rel="stylesheet" href="style.css">
    <script src="https://unpkg.com/htmx.org@2.0.3" defer></script>
  </head>
  <body>
    <h1>Welcome to My Website</h1>
    <p>This is a paragraph.</p>
    <div id="content">
      <p>
        Another paragraph inside an 
        <i>italic</i>
         div.
      </p>
    </div>
  </body>
</html>
"""


def test_render():
    assert str(SAMPLE) == EXPECTED_SAMPLE_RENDER


def test_render_pretty():
    assert render(SAMPLE) == EXPECTED_SAMPLE_RENDER_PRETTY
