import io
import select
import PIL.Image
import flask
import v4l2capture

app = flask.Flask('basic-web-cam')

def gen_frames():
    cam = v4l2capture.Video_device("/dev/video0")
    cam.set_format(640, 480)
    cam.create_buffers(1)
    cam.queue_all_buffers()
    buff = io.BytesIO()
    cam.start()
    while True:
        select.select((cam,), (), ())
        frame = cam.read_and_queue()
        image = PIL.Image.frombytes("RGB", (640, 480), frame)
        image.save(buff, format="jpeg")
        data = buff.getvalue()
        yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + data + b"\r\n"
        buff.seek(0)
        buff.truncate()


app.route("/")(lambda: '<!DOCTYPE html><html><body><img src="/stream" /></body></html>')
@app.route("/stream")
def stream():
    return flask.Response(
        gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host="0.0.0.0")
