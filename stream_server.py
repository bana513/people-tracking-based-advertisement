from flask import Flask, render_template, Response
import cv2
import threading

class StreamServer:
    def __init__(self):
        self.c = threading.Condition()
        self.current_frame = None

        self.app = Flask(__name__)

        self.movements = []

        self.advertisement_time = 0
        self.advertisement_state = 'budget'
        self.images = {}
        im_names = ['down', 'up', 'left', 'right', 'budget']
        images = [open('images/' + f + '.jpg', 'rb').read() for f in im_names]
        for i, im in enumerate(images):
            self.images[im_names[i]] = im

        @self.app.route('/')
        def index():
            return render_template('index.html')

        @self.app.route('/video_feed')
        def video_feed():
            return Response(self.gen(),
                            mimetype='multipart/x-mixed-replace; boundary=frame')

        @self.app.route('/advertisement')
        def advertisement():
            return Response(self.getAdvertisement(),
                            mimetype='multipart/x-mixed-replace; boundary=frame')

        # @self.app.route('/movements')
        # def movements():
        #     return Response(self.getMovements(),
        #                     mimetype='multipart/x-mixed-replace; boundary=frame')


    def gen(self):
        while True:
            self.c.acquire()
            self.c.wait()
            ret, jpeg = cv2.imencode('.jpg', self.current_frame)
            self.c.release()
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
        self.app.run(host='127.0.0.1', debug=False)


    def setMovingPeople(self, movements):
        prev_adv = self.advertisement_state
        self.movements = movements

        self.advertisement_time += 1
        if self.advertisement_time < 30:
            return

        moving_out, moving_in, moving_in_left, moving_in_right = movements

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

    # def getMovements(self):
    #     self.c.acquire()
    #     self.c.wait()
    #     moving_out, moving_in, moving_in_left, moving_in_right = self.movements
    #     self.c.release()
    #     yield (b'--frame\r\n'
    #                b'Content-Type: text/xml\r\n\r\n' + 'asdasda' + b'\r\n')
    #     # yield (b'Moving out: \r\n' + moving_out +
    #     #        b'Moving in: \r\n' + moving_in +
    #     #        b'Moving in left: \r\n' + moving_in_left +
    #     #        b'Moving in rigth: \r\n' + moving_in_right)
