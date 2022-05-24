
from deepface import DeepFace
from emotion_model import EmotionModel

def analyze_emotion(image_temp,return_dict):
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

    return_dict["dominant"]=dominant
    return_dict["current_feeling"]=current_feeling

def analyze_person(image_temp, return_dict):
    verification = DeepFace.find(image_temp, db_path = "User", enforce_detection=False)

    return_dict["verification"]=verification