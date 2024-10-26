def render_attr(key, value):
    return key if value is True else f'{key}="{value}"'


def render_attrs(options):
    return " ".join(render_attr(k, v) for k, v in options.items() if v is not False)


def py_dict_to_attrs(attrs: dict[str, str]) -> dict[str, str]:
    return {name.strip("_").replace("_", "-"): value for name, value in attrs.items()}
