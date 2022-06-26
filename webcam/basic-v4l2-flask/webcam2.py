import flask
import v4l2py

app = flask.Flask('basic-web-cam')

def gen_frames(camera_id):
    with v4l2py.Device.from_id(camera_id) as cam:
        cam.video_capture.set_format(640, 480, 'MJPG')
        for frame in cam:
            yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"

@app.route("/")
def index():
    return '<!DOCTYPE html><html><body><img src="/stream" /></body></html>'

@app.route("/stream/")
@app.route("/stream/<int:video>")
def stream(video=0):
    return flask.Response(
        gen_frames(video), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    app.run(host="0.0.0.0")
