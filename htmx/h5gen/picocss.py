from h5gen.functions import CSS, Style

PICOCSS_SOURCE = "https://cdn.jsdelivr.net/npm/@picocss/pico@2.0.6/css/pico.min.css"


pico_css = CSS(href=PICOCSS_SOURCE)

pico_css_style = Style("""
button {
    --pico-form-element-spacing-horizontal: 0.5rem;
    --pico-form-element-spacing-vertical: 0.2rem;
}
""")
