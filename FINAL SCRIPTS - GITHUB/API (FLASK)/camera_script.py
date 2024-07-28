import requests
import cv2 
import time


cap = cv2.VideoCapture()
# cap.open("rtsp://camera_name:password@0.0.0.0.0/Streaming/channels/1?tcp&buffer_size=102400") # for rtsp protocol
# cap.open("https://0.0.0.0/video") # for simple https protocol

time_last = time.time()

while True:
    success, img = cap.read()
    time_now = time.time()
    if success:    
        # cv2.imshow("OUTPUT", img)
        
        _ , imdata = cv2.imencode('.JPG', img)

        print('.', end='', flush=True)
        if time_now - time_last >= 3:
            time_last = time.time()
            data = imdata.tobytes()
            # requests.put('http://0.0.0.0/upload', data) # your IP OF SERVER

        # 40ms = 25 frames per second (1000ms/40ms), 
        # 1000ms = 1 frame per second (1000ms/1000ms)
        # but this will work only when `imshow()` is used.
        # Without `imshow()` it will need `time.sleep(0.04)` or `time.sleep(1)`

    if cv2.waitKey(1) == 27:  # 40ms = 25 frames per second (1000ms/40ms) 
        break

cv2.destroyAllWindows()
cap.release()
