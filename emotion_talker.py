from audioop import mul
import datetime
from queue import Queue
from time import sleep
from cv2 import imshow
import cv2
from deepface import DeepFace
from emotion_model import EmotionModel
from gtts import gTTS
import threading
import multiprocessing
from emotion_tts import save_tts, speak_tts, delete_tts


faceCascade = cv2.CascadeClassifier('haarcascade_frontface.xml')


image_queue = []

def emotion_tts(e, speach_queue):

    music_queue = []
    lock = threading.Lock()

    while True:
        e.wait()

        th1 = threading.Thread(target=save_tts, args = (speach_queue,music_queue,lock))
        th2 = threading.Thread(target=speak_tts, args = (music_queue,lock))
        th3 = threading.Thread(target=delete_tts, args = (music_queue,lock))
        
        th1.start()
        th2.start()
        th3.start()

        th1.join()
        th2.join()




# 메인 함수
def main_func(e, speach_queue):
    cv2.setUseOptimized(True)
    cap = cv2.VideoCapture(0)
    cap.set(3,1920) # set Width
    cap.set(4,1080) # set Height

    count = 0

    while True:
        ret, img = cap.read(0)
        img = cv2.resize(img, (1920, 1080))

        # 띄워진 창 지우기
        if(count % 2 == 0):
            while(len(image_queue) > 0):
                try:
                    cv2.destroyWindow(image_queue.pop(0))
                except:
                    print("e")
                finally:
                    print('')
        count += 1

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
                
                # 표정 분석
                face_analysis = DeepFace.analyze(image_temp, actions=["emotion"], enforce_detection=False)["emotion"]
                
                emotion = EmotionModel(
                    angry=face_analysis["angry"],
                    disgust=face_analysis["disgust"],
                    fear=face_analysis["fear"],
                    happy=face_analysis["happy"],
                    sad=face_analysis["sad"],
                    surprise=face_analysis["surprise"],
                )

                dominant, current_feeling = emotion.get_emotion()

                
                   
                # 지인 인식
                verification = DeepFace.find(image_temp, db_path = "User", enforce_detection=False)
                speach = ""


                # 화면 그리기
                if(verification.loc[0][1] < 0.25):
                    cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 10)
                    person_img = cv2.imread(f'{verification.loc[0][0]}')
                    user_name = verification.loc[0][0].split("/")[-2]
                    image_queue.append(user_name)
                    imshow(f'{user_name}',cv2.resize(person_img, (300,300)))
                    speach = f"Your friend {user_name} is feeling {current_feeling}."
                    cv2.putText(img, f'{dominant}-{current_feeling}', (x+w+30,y+h), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0))
                    cv2.putText(img, f'{24}years old', (x+w+30,y+h +30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0))
                    cv2.putText(img, f'{user_name}', (x+w+30,y+h +60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0))
                    cv2.putText(img, 'Relation: friend', (x+w+30,y+h +90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0))
                    cv2.putText(img, 'Last Met: 2022-05-24', (x+w+30,y+h +120), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0))
                else:                    
                    cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 10)
                    cv2.putText(img, f'{dominant}-{current_feeling}', (x+w+30,y+h), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255))
                    cv2.putText(img, f'{24}years old', (x+w+30,y+h +30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255))
                    cv2.putText(img, 'UNKNOWN', (x+w+30,y+h+60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255))
                    speach = f"A stranger is feeling {current_feeling}."
                while( not speach_queue.empty()):
                    speach_queue.get()
                speach_queue.put(speach)
                e.set()
            
        cv2.imshow('camera', img)


        k = cv2.waitKey(100) & 0xff
        if k == 27: # press 'ESC' to quit # ESC를 누르면 종료
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    speach_queue = multiprocessing.Queue()
    e = multiprocessing.Event()


    Pc1 = multiprocessing.Process(target=main_func,args=(e,speach_queue,))
    Pc2 = multiprocessing.Process(target=emotion_tts,args=(e, speach_queue,))

    Pc1.start()
    Pc2.start()

    # main_func(e,speach_queue)