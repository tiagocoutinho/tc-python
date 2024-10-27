def render_attr(key, value):
    if key == "cls":
        key = "class"
    else:
        key = key.strip("_").replace("_", "-")
    return key if value is True else f'{key}="{value}"'


def render_attrs(options):
    return " ".join(render_attr(k, v) for k, v in options.items())
