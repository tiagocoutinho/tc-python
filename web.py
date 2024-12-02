import json
import re
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse


class BaseResponse:
    HEADERS = {}

    def __init__(self, content, headers=None, status_code=200):
        self.content = content
        self.status_code = status_code
        self.headers = {
            "Content-Length": str(len(content)),
            **self.HEADERS,
            **(headers or {})
        }


class TextResponse(BaseResponse):
    HEADERS = {"Content-Type": "text/plain"}

    def __init__(self, content, headers=None, status_code=200):
        if isinstance(content, str):
            content = content.encode()
        super().__init__(content, headers=headers, status_code=status_code)


class HTMLResponse(BaseResponse):
    HEADERS = {"Content-Type": "text/html"}

    def __init__(self, content, headers=None, status_code=200):
        if isinstance(content, str):
            content = content.encode()
        super().__init__(content, headers=headers, status_code=status_code)


class JSONResponse(BaseResponse):
    HEADERS = {"Content-Type": "application/json"}

    def __init__(self, content, headers=None, status_code=200):
        content = json.dumps(content).encode()
        super().__init__(content, headers=headers, status_code=status_code)


def send(handler, response):
    if isinstance(response, str):
        response = response.encode()
    if isinstance(response, bytes):
        response = HTMLResponse(response) if response.startswith(b"<") else TextResponse(response)
    elif isinstance(response, (dict, list, tuple)):
        response = JSONResponse(response)
    handler.send_response(response.status_code)
    for name, value in response.headers.items():
        handler.send_header(name, value)
    handler.end_headers()
    handler.wfile.write(response.content)


class Router:
    def __init__(self):
        self.routes = []

    def add_route(self, path, methods, handler):
        # Convert Flask-like paths to regex (e.g., "/user/{id}" -> r"^/user/(?P<id>[^/]+)$")
        path_regex = re.sub(r"{(\w+)}", r"(?P<\1>[^/]+)", path)
        path_regex = f"^{path_regex}$"
        self.routes.append((re.compile(path_regex), methods, handler))

    def route(self, path, methods=None):
        if methods is None:
            methods = ['GET']

        def decorator(handler):
            self.add_route(path, [method.upper() for method in methods], handler)
            return handler

        return decorator

    def get(self, path):
        return self.route(path)

    def post(self, path):
        return self.route(path, ["POST"])

    def handle_request(self, handler):
        parsed_path = urlparse(handler.path).path
        method = handler.command

        for path_regex, methods, func in self.routes:
            match = path_regex.match(parsed_path)
            if match and method in methods:
                # Pass path variables as keyword arguments
                response = func(**match.groupdict())
                send(handler, response)
                return

        handler.send_error(404, "Route not found")


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "TiagoServer/0.1"

    def __init__(self, *args, **kwargs):
        self.router = kwargs.pop("router")
        super().__init__(*args, **kwargs)

    def do_GET(self):
        return self.router.handle_request(self)


class App:
    def __init__(self):
        self.router = Router()
        self.route = self.router.route
        self.get = self.router.get
        self.post = self.router.post

    def __call__(self, *args, **kwargs):
        handler = Handler(*args, router=self.router, **kwargs)
        return handler


# Router instance
app = App()

# Define routes
@app.get('/hello')
def hello_handler():
    return b"Hello, Flask-like HTTPServer!"

@app.get('/user/{id}')
def user_handler(id):
    return f"User ID: {id}"


if __name__ == "__main__":
    with HTTPServer(('', 8080), app) as httpd:
        print(f"Server running on {httpd.server_address}")
        httpd.serve_forever()

