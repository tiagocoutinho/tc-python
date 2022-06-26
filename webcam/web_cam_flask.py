import io

from flask import Flask, render_template, Response
from camera import Camera

app = Flask(__name__)


def cv2_camera(camera_id, fps, size):
    import cv2
    cam = cv2.VideoCapture(camera_id)
    cam.set(cv2.CAP_PROP_FPS, fps)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, size[0])
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, size[1])
    return cam


def gen_frame(cam):
    while True:
        result, frame = cam.read()
        if not result:
            frame = None
        yield frame

def gen
#        buff = io.BytesIO()
#        image = Image.fromarray(frame)
#        image.save(buff, 'JPEG')
#        yield buff.getvalue()
       result, buf =  cv2.imencode(".jpg", frame)
       
       yield 


@app.route('/')
def index():
        return render_template('index.html')


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')



@app.route('/video_feed')
def video_feed():
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
