import h5gen as h


SAMPLE = h.html(
    h.head(
        h.title("Sample Page"),
        h.link(rel="stylesheet", href="style.css"),
        h.script(src="https://unpkg.com/htmx.org@2.0.3", defer=True, dont_show=False),
    ),
    h.body(
        h.h1("Welcome to My Website"),
        h.p("This is a paragraph."),
        h.div(
            h.p("Another paragraph inside an ", h.i("italic"), " div."),
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
    assert h.render_pretty(SAMPLE) == EXPECTED_SAMPLE_RENDER_PRETTY