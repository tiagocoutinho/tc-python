import time
import queue
import select
import threading
import contextlib

import flask
import v4l2capture

app = flask.Flask('basic-web-cam')

clients = set()


def gen_frames():
    cam = v4l2capture.Video_device("/dev/video0")
    with contextlib.closing(cam):
        cam.set_format(640, 480, fourcc='MJPG')
        cam.create_buffers(1)
        cam.queue_all_buffers()
        cam.start()
        while True:
            select.select((cam,), (), ())
            yield cam.read_and_queue()


def engine(stop):
    while not stop:
        while not clients:
            if stop:
                return
            print ("waiting for clients...")
            time.sleep(1)
        for frame in gen_frames():
            if not clients:
                break
            if stop:
                return
            broadcast(clients, frame)


def broadcast(clients, frame):
    frame = b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
    for client in clients:
        if client.empty():
            client.put(frame)


def gen_stream():
    client = queue.Queue()
    clients.add(client)
    try:
        for frame in iter(client.get, None):
            yield frame
    finally:
        clients.remove(client)


@app.route("/")
def index():
    return '<!DOCTYPE html><html><body><img src="/stream" /></body></html>'


@app.route("/stream")
def stream():
    return flask.Response(
        gen_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    stop = []
    task = threading.Thread(target=engine, args=(stop,))
    task.start()
    try:
        app.run(host="0.0.0.0")
    finally:
        stop.append(1)
        task.join()
