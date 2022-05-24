import datetime
from time import sleep
from cv2 import imshow
import numpy as np
import cv2
import os
from PIL import Image
from deepface import DeepFace
from emotion_model import EmotionModel
from gtts import gTTS
import playsound
from IPython.display import Audio  
import threading

from multiprocessing import Process
font = cv2.FONT_HERSHEY_SIMPLEX

cap = cv2.VideoCapture(0)
cap.set(3,1920) # set Width
cap.set(4,1080) # set Height

faceCascade = cv2.CascadeClassifier('haarcascade_frontface.xml')
count2 = 1
count3 = 0

flag = 0
count = 0
isFirst = True
pass_image = ""
isSpeaching = False
lock = threading.Lock() # threading에서 Lock 함수 가져오기
queue_lock = threading.Lock() # threading에서 Lock 함수 가져오기

image_queue = []
music_queue = []


def speach_native(speech):
    kor_wav = gTTS(f'{speech}')
    music_name = f'{datetime.datetime.now().microsecond}.mp3'
    music_queue.append(music_name)
    kor_wav.save(music_name)
    # playsound.playsound(music_name)


def speak():
    if(len(music_queue)>0):
        music = music_queue.pop(0)
        playsound.playsound(music)
        if(len(music_queue)>0):
            music_queue.clear()
        





while True:
    
    ret, img = cap.read(0)
    img = cv2.resize(img, (1920, 1080))


    if(ret):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor = 1.2,
            minNeighbors = 3,
            minSize = (20,20)
        )
        
        for (x, y, w, h) in faces:
            image_temp = cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 0), 0)
            #cv2.imwrite("User/" + str(count2) + ".jpg", gray[y:y+h,x:x+w])
            #count2+=1
            # DeepFace.stream('User')
            face_analysis = DeepFace.analyze(image_temp, actions=["emotion"], enforce_detection=False)["emotion"]
            emotion = EmotionModel(
                angry=face_analysis["angry"],
                disgust=face_analysis["disgust"],
                fear=face_analysis["fear"],
                happy=face_analysis["happy"],
                sad=face_analysis["sad"],
                surprise=face_analysis["surprise"],
            )
            if(count % 1 == 0 or isFirst):
                dominant, current_feeling = emotion.get_emotion()
                isFirst = False

            if(count % 1 == 0 and len(image_queue) > 0):
               try:
                   cv2.destroyWindow(image_queue.pop(0))
               except:
                   print("e")
               finally:
                   print("sdfs")

            verification = DeepFace.find(image_temp, db_path = "User", enforce_detection=False)
            speech = ""
            if(verification.loc[0][1] < 0.25):
            #if(True):
                cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 10)
                # person_img = cv2.imread(f'{verification.loc[0][0]}')
                person_img = cv2.imread('User/Jaeyoon_Park/0.jpg')
            #    dst =  cv2.bitwise_or(img,person_img)
            #    DeepFace.stream('User')
                user_name = verification.loc[0][0].split("/")[-2]
                image_queue.append(user_name)
                imshow(f'{user_name}',cv2.resize(person_img, (300,300)))


            #    # set adjusted colors
            #    if (flag == 10):
            #         flag = 0
            #    else:
            #         flag += 1
               

            #    # normalize alpha channels from 0-255 to 0-1
            #    alpha_background = img[:,:,3] / 255.0
            #    alpha_foreground = person_img[:,:,3] / 255.0ㅏ

            #    for color in range(0, 3):
            #     img[:,:,color] = alpha_foreground * person_img[:,:,color] + \
            #     alpha_background * img[:,:,color] * (1 - alpha_foreground)
            #     dst[:,:,3] = (1 - (1 - alpha_foreground) * (1 - alpha_background)) * 255
                speech = f"Your friend {user_name} is feeling {current_feeling}."
                
               
                cv2.putText(img, f'{dominant}-{current_feeling}', (x+w+30,y+h), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0))
                cv2.putText(img, f'{24}years old', (x+w+30,y+h +30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0))
                cv2.putText(img, f'{user_name}', (x+w+30,y+h +60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0))
                cv2.putText(img, 'Relation: friend', (x+w+30,y+h +90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0))
                cv2.putText(img, 'Last Met: 2022-05-24', (x+w+30,y+h +120), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0))
            else:
                speech = f"A stranger is feeling {current_feeling}."
                
                cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 10)
                cv2.putText(img, f'{dominant}-{current_feeling}', (x+w+30,y+h), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255))
                cv2.putText(img, f'{24}years old', (x+w+30,y+h +30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255))
                cv2.putText(img, 'UNKNOWN', (x+w+30,y+h+60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255))
               
            # if count3 % 7 == 0:
            th1 = threading.Thread(target=speach_native,args=(speech,))

            th2 = threading.Thread(target=speak,args=())

            th1.start()

            th2.start()
            
            #elif len(music_queue) == 1:
            #    music_queue.clear()
                # music = music_queue.pop(0)
                # playsound.playsound(music)
            count3 += 1



            #face_analysis = DeepFace.analyze(image_result, actions=["age"], enforce_detection=False)
            #cv2.putText(img, face_analysis, (x+5,y-5), font, 1, (0, 255, 255), 2)
            #print(face_analysis)
        
    cv2.imshow('camera', img)
    count += 1


    k = cv2.waitKey(100) & 0xff
    if k == 27: # press 'ESC' to quit # ESC를 누르면 종료
        break

cap.release()
cv2.destroyAllWindows()
