import datetime
from cv2 import imshow
import cv2
from deepface import DeepFace
from emotion_model import EmotionModel
from gtts import gTTS
import playsound
import threading


faceCascade = cv2.CascadeClassifier('haarcascade_frontface.xml')

lock = threading.Lock() # threading에서 Lock 함수 가져오기

image_queue = []
music_queue = []
speach_queue = []


# 음성 파일 저장
def save_tts():
    while True:
        if(len(speach_queue) > 0):
            speach = speach_queue.pop(0)
            kor_wav = gTTS(f'{speach}')
            music_name = f'{datetime.datetime.now().microsecond}.mp3'
            if(lock.acquire(timeout=1)):
                kor_wav.save(music_name)
                music_queue.append(music_name)
                lock.release()

# 음성 파일 출력
def speak_tts():
    while True:
        if(len(music_queue)>0):
            print("음악 발견")
            if(lock.acquire(timeout=1)):
                music = music_queue.pop(0)
                playsound.playsound(music)
                lock.release()
        


# 메인 함수
def main_func():

    cap = cv2.VideoCapture(0)
    cap.set(3,1920) # set Width
    cap.set(4,1080) # set Height

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

                # 띄워진 창 지우기
                if(len(image_queue) > 0):
                    cv2.destroyWindow(image_queue.pop(0))
                   
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

                speach_queue.append(speach)
            
        cv2.imshow('camera', img)


        k = cv2.waitKey(100) & 0xff
        if k == 27: # press 'ESC' to quit # ESC를 누르면 종료
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    th = threading.Thread(target=main_func,args=())
    th2 = threading.Thread(target=speak_tts,args=())
    th3 = threading.Thread(target=save_tts,args=())

    th.start()
    th2.start()
    th3.start()

    th.join()
    th2.join()
    th3.join()

