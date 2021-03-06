# USAGE
# To read and write back out to video:
# python people_counter.py --prototxt mobilenet_ssd/MobileNetSSD_deploy.prototxt \
#	--model mobilenet_ssd/MobileNetSSD_deploy.caffemodel --input videos/example_01.mp4 \
#	--output output/output_01.avi
#
# To read from webcam and write back out to disk:
# python people_counter.py --prototxt mobilenet_ssd/MobileNetSSD_deploy.prototxt \
#	--model mobilenet_ssd/MobileNetSSD_deploy.caffemodel \
#	--output output/webcam_output.avi

# import the necessary packages
from pyimagesearch.centroidtracker import CentroidTracker
from pyimagesearch.trackableobject import TrackableObject
from pyimagesearch.tracker_box import drop_overlapping_boxes
from pyimagesearch.tracker_box import TrackerBox
from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import argparse
import imutils
import time
import dlib
import cv2
from stream_server import *

# Find OpenCV version - for reading fps of video files
(major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--prototxt", required=True,
                help="path to Caffe 'deploy' prototxt file")
ap.add_argument("-m", "--model", required=True,
                help="path to Caffe pre-trained model")
ap.add_argument("-i", "--input", type=str,
                help="path to optional input video file")
ap.add_argument("-o", "--output", type=str,
                help="path to optional output video file")
ap.add_argument("-c", "--confidence-tracking", type=float, default=0.4,
                help="minimum probability to filter weak detections")
ap.add_argument("-d", "--confidence-detecting", type=float, default=0.95,
                help="minimum probability to filter weak detections")
ap.add_argument("-s", "--skip-frames", type=int, default=30,
                help="# of skip frames between detections")
args = vars(ap.parse_args())


class StreamingThread(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name
        self.stream_server = StreamServer()

    def run(self):
        self.stream_server.run()


streaming_thread = StreamingThread("Stream server")

threading.Thread(target=streaming_thread.run, daemon=True).start()

# initialize the list of class labels MobileNet SSD was trained to
# detect
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
           "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
           "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
           "sofa", "train", "tvmonitor"]

# load our serialized model from disk
print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])

start_time = time.time() # To calculate fps from the processing speed when using webcam

a = True

while a:
    if args["input"] is None:
        a = False

    if args["input"] is None:
        print("[INFO] starting video stream...")
        vs = cv2.VideoCapture(0) # In some cases replace 0 with 1 if not working

        if vs.isOpened():
            print("Camera OK")
        else:
            print("Camera is not opened")

    else:
        print("[INFO] opening video file...")
        vs = cv2.VideoCapture(args["input"])

        # Reading original fps of the video file
        video_fps = vs.get(cv2.cv.CV_CAP_PROP_FPS) if int(major_ver) < 3 else vs.get(cv2.CAP_PROP_FPS)

    # initialize the video writer (we'll instantiate later if need be)
    writer = None

    # initialize the frame dimensions (we'll set them as soon as we read
    # the first frame from the video)
    W = None
    H = None

    # instantiate our centroid tracker, then initialize a list to store
    # each of our dlib correlation trackers, followed by a dictionary to
    # map each unique object ID to a TrackableObject
    ct = CentroidTracker(maxDisappeared=40, maxDistance=80)

    trackers = []
    trackableObjects = {}

    # initialize the total number of frames processed thus far, along
    # with the total number of objects that have moved either up or down
    totalFrames = 0
    totalDown = 0
    totalUp = 0

    # start the frames per second throughput estimator
    fps = FPS().start()

    # loop over frames from the video stream
    while True:
        # grab the next frame and handle if we are reading from either
        # VideoCapture or VideoStream
        frame = vs.read()
        # frame = frame[1] if args["input"] is None else frame
        frame = frame[1]

        if frame is None:
            break

        # Skip some frames when using video file to make it more real time, few skips does not hurt to tracking
        if args["input"] is not None and totalFrames % 1 != 0:
            fps.update()
            totalFrames += 1
            continue

        # resize the frame to have a maximum width of 500 pixels (the
        # less data we have, the faster we can process it), then convert
        # the frame from BGR to RGB for dlib

        # Added special slicing to test videos
        # TODO: Remove these
        if args["input"] == "videos\walkingpeople.mp4":
            frame = frame[-480:, 400:-240, :]
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        elif args["input"] == "videos\custom.mp4":
            frame = np.flip(frame, axis=0)
            frame = np.flip(frame, axis=1)
            frame = imutils.resize(frame, width=640)
            rgb = frame
        else:
            frame = imutils.resize(frame, width=640)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # if the frame dimensions are empty, set them
        if W is None or H is None:
            (H, W) = frame.shape[:2]

        # if we are supposed to be writing a video to disk, initialize
        # the writer
        if args["output"] is not None and writer is None:
            fourcc = cv2.VideoWriter_fourcc(*"MJPG")
            writer = cv2.VideoWriter(args["output"], fourcc, 30,
                                     (W, H), True)

        # initialize the current status along with our list of bounding
        # box rectangles returned by either (1) our object detector or
        # (2) the correlation trackers
        status = "Waiting"
        boxes = []

        # check to see if we should run a more computationally expensive
        # object detection method to aid our tracker
        if totalFrames % args["skip_frames"] == 0:
            # set the status and initialize our new set of object trackers
            status = "Detecting"

            # Tracker candidates - we may not want to use every bounding box as a correlation tracker
            # if boxes are way too much overlapping
            tracker_box_candidates = []

            # convert the frame to a blob and pass the blob through the
            # network and obtain the detections
            blob = cv2.dnn.blobFromImage(frame, 0.007843, (W, H), 127.5)
            net.setInput(blob)
            detections = net.forward()

            (H, W) = rgb.shape[:2]

            # loop over the detections
            for i in np.arange(0, detections.shape[2]):
                # extract the confidence (i.e., probability) associated
                # with the prediction
                confidence = detections[0, 0, i, 2]

                # filter out weak detections by requiring a minimum
                # confidence
                if confidence > args["confidence_tracking"]:
                    # extract the index of the class label from the
                    # detections list
                    idx = int(detections[0, 0, i, 1])

                    # if the class label is not a person, ignore it
                    if CLASSES[idx] != "person":
                        continue

                    # compute the (x, y)-coordinates of the bounding box
                    # for the object
                    rect = (detections[0, 0, i, 3:7] * np.array([W, H, W, H])).astype("int")
                    box = TrackerBox(rect, confidence)
                    tracker_box_candidates.append(box)

            tracker_boxes = []

            if len(tracker_box_candidates) > 0:
                tracker_boxes = drop_overlapping_boxes(tracker_box_candidates)
                dropped = len(tracker_box_candidates) - len(tracker_boxes)
                # if dropped > 0:
                #     print('Dropped tracker boxes because ovelapping: {}'.format(dropped))

            trackers = []
            for box in tracker_boxes:
                # construct a dlib rectangle object from the bounding
                # box coordinates and then start the dlib correlation
                # tracker
                tracker = dlib.correlation_tracker()
                rect = dlib.rectangle(box.coordinates[0], box.coordinates[1], box.coordinates[2], box.coordinates[3])
                tracker.start_track(rgb, rect)

                # add the tracker to our list of trackers so we can
                # utilize it during skip frames
                trackers.append(tracker)

                boxes.append(box)

        # otherwise, we should utilize our object *trackers* rather than
        # object *detectors* to obtain a higher frame processing throughput
        else:
            # loop over the trackers
            for tracker in trackers:
                # set the status of our system to be 'tracking' rather
                # than 'waiting' or 'detecting'
                status = "Tracking"

                # update the tracker and grab the updated position
                tracker.update(rgb)
                pos = tracker.get_position()

                # unpack the position object
                startX = int(pos.left())
                startY = int(pos.top())
                endX = int(pos.right())
                endY = int(pos.bottom())

                # add the bounding box coordinates to the rectangles list
                boxes.append(TrackerBox((startX, startY, endX, endY)))
                cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 1)

        frame = imutils.resize(frame, width=frame.shape[1])
        (H, W) = frame.shape[:2]

        # draw a horizontal line in the center of the frame -- once an
        # object crosses this line we will determine whether they were
        # moving 'up' or 'down'
        # cv2.line(frame, (0, H // 2), (W, H // 2), (0, 255, 255), 2)

        # use the centroid tracker to associate the (1) old object
        # centroids with (2) the newly computed object centroids
        objects = ct.update(boxes, args["confidence_detecting"])

        moving_in_left = 0
        moving_in_right = 0
        moving_out = 0
        moving_in = 0

        # loop over the tracked objects to show them
        for (objectID, centroid) in objects.items():
            # check to see if a trackable object exists for the current
            # object ID
            to = trackableObjects.get(objectID, None)

            # if there is no existing trackable object, create one
            if to is None:
                to = TrackableObject(objectID, centroid)

            # otherwise, there is a trackable object so we can utilize it
            # to determine direction
            else:
                # the difference between the y-coordinate of the *current*
                # centroid and the mean of *previous* centroids will tell
                # us in which direction the object is moving (negative for
                # 'up' and positive for 'down')
                y = [c[1] for c in to.centroids]
                direction = centroid[1] - np.mean(y)
                to.centroids.append(centroid)

                to.number_of_speed_data += 1
                to.y_speed = 0.6 * to.y_speed + 0.4 * (centroid[1] - to.centroids[-2][1])
                to.x_speed = 0.6 * to.x_speed + 0.4 * (centroid[0] - to.centroids[-2][0])

                # print("{0}: {1:.2f} {2:.2f}".format(to.objectID, to.x_speed, to.y_speed))

                if to.y_speed < -2: moving_out += 1
                if to.y_speed > 2:
                    moving_in += 1
                if to.x_speed < -2: moving_in_left += 1
                if to.x_speed > 2: moving_in_right += 1

                # check to see if the object has been counted or not
                if not to.counted:
                    # if the direction is negative (indicating the object
                    # is moving up) AND the centroid is above the center
                    # line, count the object
                    if direction < 0 and centroid[1] < H // 2:
                        totalUp += 1
                        to.counted = True

                    # if the direction is positive (indicating the object
                    # is moving down) AND the centroid is below the
                    # center line, count the object
                    elif direction > 0 and centroid[1] > H // 2:
                        totalDown += 1
                        to.counted = True

            # store the trackable object in our dictionary
            trackableObjects[objectID] = to

            # draw both the ID of the object and the centroid of the
            # object on the output frame
            text = "ID {}".format(objectID)
            cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.circle(frame, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)

        # print("up: {}, down: {}, left: {}, right: {}".format(moving_out, moving_in, moving_in_left, moving_in_right))

        # construct a tuple of information we will be displaying on the
        # frame
        info = [
            ("Up", totalUp),
            ("Down", totalDown),
            ("Status", status),
        ]

        # loop over the info tuples and draw them on our frame
        # for (i, (k, v)) in enumerate(info):
        #     text = "{}: {}".format(k, v)
        #     cv2.putText(frame, text, (10, H - ((i * 20) + 20)),
        #                 cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        # check to see if we should write the frame to disk
        if writer is not None:
            writer.write(frame)

        # show the output frame
        cv2.imshow("Frame", frame)

        ss = streaming_thread.stream_server
        ss.c.acquire()
        ss.current_frame = np.copy(frame)

        ss.setMovingPeople([moving_out, moving_in, moving_in_left, moving_in_right],
                           totalFrames // video_fps if args["input"] is not None else time.time() - start_time)

        ss.c.notify_all()
        ss.c.release()

        key = cv2.waitKey(200) & 0xFF

        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break

        # increment the total number of frames processed thus far and
        # then update the FPS counter
        totalFrames += 1
        fps.update()

    # stop the timer and display FPS information
    fps.stop()
    print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

    stream_fps = streaming_thread.stream_server.getFps()
    print("[INFO] video_feed: {:.2f}, gen:{:.2f} ".format(stream_fps[0], stream_fps[1]))

# check to see if we need to release the video writer pointer
if writer is not None:
    writer.release()

# if we are not using a video file, stop the camera video stream
if args["input"] is not None:
    vs.stop()

# otherwise, release the video file pointer
else:
    vs.release()

# close any open windows
cv2.destroyAllWindows()
