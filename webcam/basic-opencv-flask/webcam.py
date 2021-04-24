import cv2
import flask


app = flask.Flask('basic-web-cam')


def gen_frames():
    cam = cv2.VideoCapture(0)
    while True:
        _, frame = cam.read()
        _, data = cv2.imencode('.jpg', frame)
        yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + data.tobytes() + b"\r\n"


@app.route("/")
def index():
    return '<!DOCTYPE html><html><body><img src="/stream" /></body></html>'


@app.route("/stream")
def stream():
    return flask.Response(
        gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    app.run(host="0.0.0.0")
