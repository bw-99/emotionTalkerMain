import datetime
import threading
from gtts import gTTS
from playsound import playsound



# 음성 파일 저장
def save_tts(speach_queue,music_queue,lock):
    if(speach_queue.qsize() > 0):
        speach = speach_queue.get()
        kor_wav = gTTS(f'{speach}')
        music_name = f'{datetime.datetime.now().microsecond}.mp3'
        if(lock.acquire(timeout=1)):
            kor_wav.save(music_name)
            music_queue.append((datetime.datetime.now(),music_name))
            lock.release()

# 음성 파일 출력
def speak_tts(music_queue,lock):
    if(len(music_queue)>0):
        print("음악 발견")
        if(lock.acquire()):
            while True:
                (time_stamp, music) = music_queue.pop(0)
                now =datetime.datetime.now()
                time_spent = (now - time_stamp).total_seconds()
                if(time_spent > 1):
                    music_queue.pop(0)
                    print(f"delete => {len(music_queue)} : {time_spent}초")
                else:
                    break

            music_queue.clear()
            playsound(music)
            lock.release()
        
# 음성 파일 삭제
def delete_tts(music_queue, lock):
    if(lock.acquire()):
        for (time_stamp, music) in music_queue:
            now =datetime.datetime.now()
            time_spent = (now - time_stamp).total_seconds()
            if(time_spent > 1):
                music_queue.remove((time_stamp, music))
                print(f"delete => {len(music_queue)} : {time_spent}초")
        lock.release()

