from flask import Flask, Response, redirect, request, url_for, render_template
from flask_bootstrap import Bootstrap
from flask_socketio import SocketIO, emit
import cv2
import threading
from imutils.video import FPS
import itertools
import time
from upload_advertisement import upload
# from advertisement_condition import get_advertisement
import advertisement_condition
import sys, importlib

UPLOAD_FOLDER = r'uploads'

class ChartData:
    """
    Stores data for chart streaming.
    """
    def __init__(self):
        self.timestap = []
        self.movements = []

    def getLast(self, N=1):
        return {'timestamp': self.timestap[-N:], 'movements': self.movements[-N:]}

    def append(self, data):
        self.timestap.append(data['timestamp'])
        self.movements.append(data['movements'])


class StreamServer:
    def __init__(self):
        self.c = threading.Condition()
        self.chartCondition = threading.Condition()
        self.chartCounter = 0 # Refresh people counter only when detection run

        self.advertisement_condition = threading.Condition()

        self.current_frame = None

        self.app = Flask(__name__)
        # Bootstrap(self.app)
        self.app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

        self.chart_data = ChartData()

        self.advertisement_time = 0

        self.advertisement_state = None
        self.advertisement_description = ''
        self.images = {}
        self.set_advertisement_image((None, ''))


        # self.advertisement_state = 'budget'
        # self.images = {}
        # im_names = ['down', 'up', 'left', 'right', 'budget']
        # images = [open('images/' + f + '.jpg', 'rb').read() for f in im_names]
        # for i, im in enumerate(images):
        #     self.images[im_names[i]] = im

        self.fps_video_feed = FPS().start()
        self.fps_gen = FPS().start()

        @self.app.route('/')
        def index():
            return render_template('index.html')

        @self.app.route('/advertisements')
        def advertisements():
            return render_template('advertisements.html')

        @self.app.route('/upload_advertisement', methods=['POST'])
        def upload_advertisement():
            upload(request, self.app.config['UPLOAD_FOLDER'], self.advertisement_condition)
            return render_template('advertisements.html')

        @self.app.route('/video_feed')
        def video_feed():
            self.fps_video_feed.update()
            return Response(self.gen(),
                            mimetype='multipart/x-mixed-replace; boundary=frame')

        @self.app.route('/advertisement')
        def advertisement():
            return Response(self.getAdvertisement(),
                            mimetype='multipart/x-mixed-replace; boundary=frame')

        @self.app.route('/number_of_people')
        def number_of_people():
            if request.headers.get('accept') == 'text/event-stream':
                def events():
                    while True:
                        self.chartCondition.acquire()
                        self.chartCondition.wait()
                        data = self.chart_data.getLast(1);
                        self.chartCondition.notify_all()
                        self.chartCondition.release()
                        yield "data: %d %d %d %d %d %d\n\n" % (data['timestamp'][0],
                                                         data['movements'][0][0]+data['movements'][0][1], # IN + OUT
                                                         data['movements'][0][0],
                                                         data['movements'][0][1],
                                                         data['movements'][0][2],
                                                         data['movements'][0][3])

                return Response(events(), content_type='text/event-stream')
            # return redirect(url_for('static', filename='data_stream.html'))
            return # render_template('data_stream.html')

    def set_advertisement_image(self, condition):
        print(condition)
        self.advertisement_description = condition[1]
        image = condition[0]

        if not image:
            image = 'none.jpg'

        if image not in self.images:
            image_bin = open('uploads/' + image, 'rb').read()
            self.images[image] = image_bin

        # Reload advertisement_condition.py after modifying conditions
        old__ref = advertisement_condition.get_advertisement
        importlib.reload(advertisement_condition)
        old__ref.__code__ = advertisement_condition.get_advertisement.__code__

        self.advertisement_state = image
        print(self.advertisement_state)

    def getFps(self):
        self.fps_gen.stop()
        self.fps_video_feed.stop()

        ret = self.fps_video_feed.fps(), self.fps_gen.fps()

        self.fps_gen = FPS().start()
        self.fps_video_feed = FPS().start()

        return ret

    def gen(self):
        while True:
            self.c.acquire()
            self.c.wait()
            ret, jpeg = cv2.imencode('.jpg', self.current_frame)
            self.c.release()
            self.fps_gen.update()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')

    def getAdvertisement(self):
        while True:
            self.c.acquire()
            self.c.wait()
            jpeg = self.images[self.advertisement_state]
            self.c.release()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg + b'\r\n')

    def run(self):
        self.app.run(host='127.0.0.1', port=8888, debug=False)


    def setMovingPeople(self, movements, timestamp):
        prev_adv = self.advertisement_state

        self.chart_data.append({'timestamp': timestamp, 'movements': movements})

        moving_out, moving_in, moving_in_left, moving_in_right = movements

        self.chartCounter += 1
        if(self.chartCounter >= 15):
            self.chartCounter = 0
            self.chartCondition.acquire()
            self.chartCondition.notify_all()
            self.chartCondition.release()

        self.advertisement_time += 1
        if self.advertisement_time < 30:
            return

        # Csak kód referencia váltás van, nem kell lock
        # (Ugyanazon a szálon fut a kódváltás, mint a felhasználás)
        # self.advertisement_condition.acquire()
        # self.advertisement_condition.wait()

        self.set_advertisement_image(
            advertisement_condition.get_advertisement(
                total_people=moving_in+moving_out,
                moving_in=moving_in,
                moving_out=moving_out,
                moving_left=moving_in_left,
                moving_right=moving_in_right))

        # self.advertisement_condition.notify_all()
        # self.advertisement_condition.release()

        # if moving_in + moving_out < 5:
        #     self.advertisement_state = 'budget'
        # else:
        #     if moving_out > moving_in:
        #         self.advertisement_state = 'up'
        #     else:
        #         if max(moving_in_right, moving_in_left) == 0:
        #             self.advertisement_state = 'down'
        #         else:
        #             if moving_in_left > moving_in_right:
        #                 self.advertisement_state = 'left'
        #             else:
        #                 self.advertisement_state = 'right'

        if prev_adv != self.advertisement_state:
            self.advertisement_time = 0
