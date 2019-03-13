from flask import Flask, Response, redirect, request, url_for, render_template
from flask_bootstrap import Bootstrap
from flask_socketio import SocketIO, emit
import cv2
import threading
from imutils.video import FPS
import itertools
import time

class StreamServer:
    def __init__(self):
        self.c = threading.Condition()
        self.chartCondition = threading.Condition()
        self.chartCounter = 0 # Refresh people counter only when detection run

        self.current_frame = None

        self.app = Flask(__name__)
        Bootstrap(self.app)
        self.app.config['SECRET_KEY'] = 'secret!'
        self.socketio = SocketIO(self.app)

        self.movements = []

        self.advertisement_time = 0
        self.advertisement_state = 'budget'
        self.images = {}
        im_names = ['down', 'up', 'left', 'right', 'budget']
        images = [open('images/' + f + '.jpg', 'rb').read() for f in im_names]
        for i, im in enumerate(images):
            self.images[im_names[i]] = im

        self.number_of_people = []

        self.fps_video_feed = FPS().start()
        self.fps_gen = FPS().start()

        @self.app.route('/')
        def index():
            return render_template('index.html')

        @self.app.route('/video_feed')
        def video_feed():
            self.fps_video_feed.update()
            return Response(self.gen(),
                            mimetype='multipart/x-mixed-replace; boundary=frame')

        @self.app.route('/advertisement')
        def advertisement():
            return Response(self.getAdvertisement(),
                            mimetype='multipart/x-mixed-replace; boundary=frame')

        @self.app.route('/line')
        def line():
            self.c.acquire()
            line_labels = [i for i in range(len(self.number_of_people)//30)]
            # print(line_labels)
            line_values = self.number_of_people[::30].copy()
            # print(self.number_of_people)
            self.c.notify_all()
            self.c.release()
            return render_template('chart_full.html', title='Number of people on frame', max=20,
                                   labels=line_labels, values=line_values)

        @self.app.route('/number_of_people')
        def number_of_people():
            if request.headers.get('accept') == 'text/event-stream':
                def events():
                    # for i, c in enumerate(itertools.cycle('\|/-')):
                    #     yield "data: %s %d\n\n" % (c, i)
                    #     time.sleep(.1)  # an artificial delay

                    # i = 0
                    # while True:
                    #     i += 1
                    #     yield "data: %d\n\n" % (i)
                    #     time.sleep(.5)

                    while True:
                        self.chartCondition.acquire()
                        self.chartCondition.wait()
                        data = self.number_of_people[-1]
                        self.chartCondition.notify_all()
                        self.chartCondition.release()
                        yield "data: %d\n\n" % (data)

                return Response(events(), content_type='text/event-stream')
            # return redirect(url_for('static', filename='data_stream.html'))
            return render_template('data_stream.html')

        @self.socketio.on('test')  # Decorator to catch an event called "my event":
        def test_message(message):  # test_message() is the event callback function.
            emit('my response', {'data': 'got it!'})  # Trigger a new event called "my response"

    def getFps(self):
        self.fps_gen.stop()
        self.fps_video_feed.stop()

        ret = self.fps_video_feed.fps(), self.fps_gen.fps()

        self.fps_gen = FPS().start()
        self.fps_video_feed = FPS().start()

        return ret

    def getPeopleChart(self):
        while True:
            self.c.acquire()
            self.c.wait()
            line_labels = [i for i in range(len(self.number_of_people))]
            print(line_labels)
            line_values = self.number_of_people.copy()
            print(self.number_of_people)
            template = render_template('chart_full.html', title='Number of people on frame', max=20,
                                       labels=line_labels, values=line_values)
            self.c.release()
            yield (b'--frame\r\n'
                   b'Content-Type: text/html\r\n\r\n' + template + b'\r\n')

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


    def setMovingPeople(self, movements):
        prev_adv = self.advertisement_state
        self.movements = movements

        moving_out, moving_in, moving_in_left, moving_in_right = movements
        self.number_of_people.append(moving_in + moving_out)

        self.chartCounter += 1
        if(self.chartCounter >= 15):
            self.chartCounter = 0
            self.chartCondition.acquire()
            self.chartCondition.notify_all()
            self.chartCondition.release()

        self.advertisement_time += 1
        if self.advertisement_time < 30:
            return

        if moving_in + moving_out < 5:
            self.advertisement_state = 'budget'
        else:
            if moving_out > moving_in:
                self.advertisement_state = 'up'
            else:
                if max(moving_in_right, moving_in_left) == 0:
                    self.advertisement_state = 'down'
                else:
                    if moving_in_left > moving_in_right:
                        self.advertisement_state = 'left'
                    else:
                        self.advertisement_state = 'right'

        if prev_adv != self.advertisement_state:
            self.advertisement_time = 0
