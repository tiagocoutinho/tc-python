from regex import D
from h5gen import Html, Head, Title, Link, Script, Body, H1, P, I, Div, render_pretty


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

EXPECTED_SAMPLE_RENDER = """<HTML><HEAD><TITLE>Sample Page</TITLE><LINK rel="stylesheet" href="style.css"/><SCRIPT src="https://unpkg.com/htmx.org@2.0.3" defer /></HEAD><BODY><H1>Welcome to My Website</H1><P>This is a paragraph.</P><DIV id="content"><P>Another paragraph inside an <I>italic</I> div.</P></DIV></BODY></HTML>"""

EXPECTED_SAMPLE_RENDER_PRETTY ="""\
<HTML>
  <HEAD>
    <TITLE>Sample Page</TITLE>
    <LINK rel="stylesheet" href="style.css"/>
    <SCRIPT src="https://unpkg.com/htmx.org@2.0.3" defer />
  </HEAD>
  <BODY>
    <H1>Welcome to My Website</H1>
    <P>This is a paragraph.</P>
    <DIV id="content">
      <P>
        Another paragraph inside an 
        <I>italic</I>
         div.
      </P>
    </DIV>
  </BODY>
</HTML>
""" 


def test_render():
    assert str(SAMPLE) == EXPECTED_SAMPLE_RENDER


def test_render_pretty():
    assert render_pretty(SAMPLE) == EXPECTED_SAMPLE_RENDER_PRETTY