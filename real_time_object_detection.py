# USAGE
# python3 real_time_object_detection.py --prototxt MobileNetSSD_deploy.prototxt.txt --model MobileNetSSD_deploy.caffemodel

import argparse
import time

import cv2
import imutils
import numpy as np
from imutils.video import FPS
from imutils.video import VideoStream
import matplotlib.pyplot as plt

# import the necessary packages
# import detection_alerts as detected

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()

ap.add_argument("-c", "--confidence", type=float, default=0.2,
                help="minimum probability to filter weak detections")
args = vars(ap.parse_args())

# initialize the list of class labels MobileNet SSD was trained to
# detect, then generate a set of bounding box colors for each class
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
           "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
           "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
           "sofa", "train", "tvmonitor"]

COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

width_loc = {}
height_loc = {}

for item in CLASSES:
    width_loc[item] = []
    height_loc[item] = []

# load our serialized model from disk
print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe('MobileNetSSD_deploy.prototxt.txt', 'MobileNetSSD_deploy.caffemodel')

# initialize the video stream, allow the cammera sensor to warmup,
# and initialize the FPS counter
print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()
time.sleep(2.0)
fps = FPS().start()

start = time.time()

# loop over the frames from the video stream
while True:
    # grab the frame from the threaded video stream and resize it
    # to have a maximum width of 400 pixels
    frame = vs.read()
    frame = imutils.resize(frame, width=400)

    # grab the frame dimensions and convert it to a blob
    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),
                                 0.007843, (300, 300), 127.5)

    # pass the blob through the network and obtain the detections and
    # predictions
    net.setInput(blob)
    detections = net.forward()

    # loop over the detections
    for i in np.arange(0, detections.shape[2]):
        # extract the confidence (i.e., probability) associated with
        # the prediction

        confidence = detections[0, 0, i, 2]

        # filter out weak detections by ensuring the `confidence` is
        # greater than the minimum confidence
        if confidence > args["confidence"]:
            # extract the index of the class label from the
            # `detections`, then compute the (x, y)-coordinates of
            # the bounding box for the object
            idx = int(detections[0, 0, i, 1])
            # set up alert for Person, Dog, Cat
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])

            (startX, startY, endX, endY) = box.astype("int")


            width = int((endX + startX) / 2)
            height = int((endY + startY) / 2)

            center = (width, height)

            # draw the prediction on the frame
            label = "{}: {:.2f}%".format(CLASSES[idx],
                                         confidence * 100)
            cv2.rectangle(frame, (startX, startY), (endX, endY),
                          COLORS[idx], 2)
            cv2.circle(frame, (width, height), 2, COLORS[idx], 2)
            y = startY - 15 if startY - 15 > 15 else startY + 15
            cv2.putText(frame, label, (startX, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)

            if CLASSES[idx] == 'person':
                width_loc[CLASSES[idx]].append(width)
                height_loc[CLASSES[idx]].append(height)

    # show the output frame
    cv2.imshow("Frame", frame)

    key = cv2.waitKey(1) & 0xFF

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break

    # update the FPS counter
    fps.update()

    end = time.time()
    loop_time = end - start

    if loop_time > 15:
        counter = True
        start = time.time()

    print(loop_time)


# stop the timer and display FPS information
fps.stop()
print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

direction = []


for n in range(len(width_loc['person'])):
    try:
        slope = width_loc['person'][n + 10] - width_loc['person'][n]
        direction.append(slope)
    except:
        None
# For item i in a range that is a length of l,
def create_chunks(l, n):
    # For item i in a range that is a length of l,
    for i in range(0, len(l), n):
        # Create an index range for l of n items:
        yield l[i:i+n]
chunks = create_chunks(direction, 10)

average_slope = []

for chunk in chunks:
    average_slope.append(np.mean(chunk))



print(average_slope)
for movement in average_slope:
    if movement <= -20:
        print('Moving Right')
    if movement >= 20:
        print('Moving Left')


plt.plot(average_slope)
plt.show()

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()
