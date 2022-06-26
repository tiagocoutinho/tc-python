import time
from io import BytesIO
from queue import Queue
from functools import lru_cache
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

import cv2
from PIL import Image


@lru_cache(maxsize=1)
def render(server):
    host, port = server.server_address
    return f"""\
<!DOCTYPE HTML>
<html>
    <head>
        <title>Camera on {host}:{port}</title>
    </head>
    <body>
        <img src="http://{host}:{port}/camera.mjpg" />
    </body>
</html>""".encode()


class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path.endswith("camera.mjpg"):
            self.send_response(200)
            self.send_header('Content-type','multipart/x-mixed-replace; boundary=--jpgboundary')
            self.end_headers()
            for frame in stream(2, 20, (1280, 1024)):
                if frame is not None:
                    self.wfile.write(b"\r\n--jpgboundary\r\n")
                    self.send_header('Content-type', 'image/jpeg')
                    self.send_header('Content-length', str(len(frame)))
                    self.end_headers()
                    self.wfile.write(frame)
                    time.sleep(0.05)
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(render(self.server))


def stream(camera_id, fps, size):
    cam = cv2.VideoCapture(camera_id)
    cam.set(cv2.CAP_PROP_FPS, fps)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, size[0])
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, size[1])
    while True:
        result, frame = cam.read()
        if not result:
            return None
        buff = BytesIO()
        image = Image.fromarray(frame)
        image.save(buff, 'JPEG')
        yield buff.getvalue()



def run():
    httpd = ThreadingHTTPServer(("", 8000), Handler)
    httpd.serve_forever()


if __name__ == "__main__":
    run()
