import numpy as np
import cv2
from Tracking import *
from craftHook import *

x0 = 400
y0 = 200
height = 200
width = 200

cap = cv2.VideoCapture(1)
cap.set(3,640) # set Width
cap.set(4,480) # set Height

detector=Yolo()
classifier=Gesture()
classifier1=Emotion()
hook=CraftHook()


threshold_left=275
threshold_right=350

count=0
per_frame_count=3
classify_flag=True

emotion_count=0
emotion_flag=6
pyautogui.FAILSAFE=False
print("Done!")
while True:
    ret, img = cap.read()
    img = cv2.flip(img, 1)
    
    Width = img.shape[1]
    Height = img.shape[0]
    
    info=detector.get_prediction(img,Width,Height)
    
   
    gesture=classifier.Guess(img,x0,y0,width,height)
    emotion,emotion_arg=classifier1.predict(img)

   
    
    if emotion_flag == emotion_arg:
        emotion_count+=1
    else:
        emotion_flag=emotion_arg
        emotion_count=0

    if emotion_count > per_frame_count and emotion_flag!=6:
        emotion_count=0
        if emotion_flag == 5:
            pyautogui.hotkey('f5','6')
            print("Surpise click")
        if emotion_flag == 3:
            pyautogui.hotkey('f5', '5')
            print("Happy click")
        
        if emotion_flag == 4:
            pyautogui.hotkey('f5', '9')
            print("Sad click")

        if emotion_flag == 0:
            pyautogui.hotkey('f5', '7')
            print("Angry click")
    
    if gesture !=1 and classify_flag :
        classify_flag=False
        count=0
        if gesture == 2:
            pyautogui.hotkey('f5','1')
            print("Peace click")
        if gesture == 3:
            pyautogui.click(button='left')
            print("Panch click")
        if gesture == 4:
            pyautogui.hotkey('f5','1')
            print("Paper click")
        if gesture == 0:
            pyautogui.click(button='left')
            print("Ok click")

    if len(info)>0:
        middle=info[0]+info[2]/2
        if middle>threshold_right:
            pyautogui.keyDown('num9')      
        elif middle<threshold_left:
            pyautogui.keyDown('num7')
        else:
              pyautogui.keyUp('num7')
              pyautogui.keyUp('num9')
    cv2.imshow('Video', img)

    
    k=cv2.waitKey(1)
    if k == 27: # press 'ESC' to quit
        break

    if count==per_frame_count:
        classify_flag=True
    count+=1
    print("e: "+str(emotion_arg)+" g: "+str(gesture))
cap.release()
cv2.destroyAllWindows() 
hook.close()