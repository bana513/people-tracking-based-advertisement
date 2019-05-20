# Advertisement system based on people tracking
Default stream server and admin page will be available on http://127.0.0.1:8889/

## Run cofigurations

### Help
Run ```people_counter.py --help``` to see available options

### Video file
Use of webcam as a source of video stream
```
-p
mobilenet_ssd\MobileNetSSD_deploy.prototxt
-m
mobilenet_ssd\MobileNetSSD_deploy.caffemodel
-i
videos\custom.mp4
-s
15
-c
.5
```

### Webcam
Use of webcam as a source of video stream
```
-p
mobilenet_ssd\MobileNetSSD_deploy.prototxt
-m
mobilenet_ssd\MobileNetSSD_deploy.caffemodel
-s
30
```
