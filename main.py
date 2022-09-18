from ast import IsNot
from asyncio.windows_events import NULL
from glob import glob
import string
import cv2
import dxcam
import time

startWith = 1 # 0: Camera, 1: Screenshoot
cameraNo = 1
color = (255,255,255)
dx = dxcam.create()
frameWidth = 1100
frameHeight = 500

def screenSize(x = 0, y= 0, width = 1920/2, height = 1080/2):
    global left
    left = int (1920 - (1920-x))
    global top 
    top =  int (1080 - (1080-y))
    global right 
    right = int (left + width)
    global bottom 
    bottom = int (top + height)
    global region
    region = (left, top, right, bottom)
    return region


path = 'cars.xml'
cascade = cv2.CascadeClassifier(path)
cascades = [cascade] # Add to use other Haarcascade model
region = screenSize(100, 300, frameWidth, frameHeight)
dx.start(target_fps=120, region=region)

camera = cv2.VideoCapture(cameraNo)
camera.set(3, frameWidth)
camera.set(3, frameHeight)

def empty(a):
    pass

cv2.namedWindow("Result")
cv2.resizeWindow("Result", frameWidth, frameHeight+100)
cv2.createTrackbar("Scale", "Result", 100, 199, empty)
cv2.createTrackbar("Neighbor", "Result", 11, 20,empty)
cv2.createTrackbar("Min Width", "Result", 45, 100, empty)
cv2.createTrackbar("Brightness", "Result", 180, 255, empty)

if startWith == 0:
    while True:
        start_time = time.time()
        cameraBrightness = cv2.getTrackbarPos("Brightness", "Result")
        camera.set(10, cameraBrightness)
        success, img = camera.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        scaleVal = 1 + (cv2.getTrackbarPos("Scale", "Result")/1000)
        neigh = cv2.getTrackbarPos("Neighbor", "Result")
        for c in cascades:
            objects = c.detectMultiScale(gray, scaleVal, neigh)

            for (x,y,w,h) in objects:
                area = w*h
                minArea = cv2.getTrackbarPos("Min Width", "Result")
                if area > minArea:
                    cv2.rectangle(img, (x,y), (x+w, y+h), color, 3)
                    roi_color = img[y: y+h, x: x+w]

        cv2.imshow("Result", img)
        print("FPS: ", 1.0 / (time.time() - start_time))
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

if startWith == 1:
    while True:
        start_time = time.time()
        img = dx.get_latest_frame()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        scaleVal = 1.001 + (cv2.getTrackbarPos("Scale", "Result")/1000)
        neigh = cv2.getTrackbarPos("Neighbor", "Result")
        if scaleVal > 0 and neigh > 0:
            for c in cascades:
                objects = c.detectMultiScale(gray, scaleVal, neigh)
                for (x,y,w,h) in objects:
                    minArea = cv2.getTrackbarPos("Min Width", "Result")
                    if w > minArea:
                        cv2.rectangle(img, (x,y), (x+w, y+h), color, 2)
                        cv2.putText(img, 'Car', (x,y+h), cv2.FONT_HERSHEY_SIMPLEX, w/75, color, 2)
                        roi_color = img[y: y+h, x: x+w]
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
        fps = 1.0 / (time.time() - start_time)
        print("FPS: ", fps)
        cv2.putText(text= f"FPS: {fps}", img=img, org=(50,50), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=color)
        cv2.imshow("Result", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break