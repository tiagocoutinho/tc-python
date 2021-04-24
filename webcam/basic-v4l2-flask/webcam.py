import flask
import select
import v4l2capture


app = flask.Flask('basic-web-cam')

def gen_frames():
    cam = v4l2capture.Video_device("/dev/video0")
    cam.set_format(640, 480, fourcc='MJPG')
    cam.create_buffers(1)
    cam.queue_all_buffers()
    cam.start()
    while True:
        select.select((cam,), (), ())
        frame = cam.read_and_queue()
        yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"


app.route("/")(lambda: '<!DOCTYPE html><html><body><img src="/stream" /></body></html>')
@app.route("/stream")
def stream():
    return flask.Response(
        gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host="0.0.0.0")
