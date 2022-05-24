

from tkinter import E

from cv2 import detail_SeamFinder


class EmotionModel:

    emotion_order_name = ["angry","disgust","sad","happy","surprise","fear"]
    
    _angry_list = ["Hurt", "Threatened", "Hateful", "Mad", "Aggressive", "Frustrated", "Distant", "Critical", "Critical"]         #0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1
    _disgust_list = ["Disapproval", "Disappointed", "Awful", "Avoidance", "Avoidance"]                                             #0, 0.25, 0.5, 0.75, 1
    _sad_list = ["Guilty", "Abandoned", "Despair", "Depressed", "Lonely", "Bored", "Bored"]
    _happy_list = ["Optimistic", "Intimate", "Peaceful", "Powerful", "Accepted", "Proud", "Interested", "Joyful", "Joyful"]
    _surprise_list = ["Excited", "Amazed", "Confused", "Startled", "Startled"]
    _fear_list = ["Scared", "Anxious", "Insecure", "Submissive", "Rejected", "Humiliated", "Humiliated"]                            #0, 0.166, 0.333, 0.5, 0.666, 0.833, 1
    

    _detail_emotion_list = [
        _angry_list,
        _disgust_list,
        _sad_list,
        _happy_list,
        _surprise_list,
        _fear_list,
    ]

    def __init__(self,angry,disgust,fear,happy,sad, surprise):
        self.angry = angry
        self.disgust = disgust
        self.fear = fear
        self.happy = happy
        self.sad = sad
        self.surprise = surprise
        self.emotion_order = [angry,disgust,sad,happy,surprise,fear]
        self.dominant_index, self.dominant = self.get_dominant()
    
    def get_dominant(self):
        emotion_list = [self.angry,self.disgust,self.sad,self.happy,self.surprise,self.fear]
        dominant = max(emotion_list)
        index = emotion_list.index(dominant)
        return index, self.emotion_order[index]

    def get_emotion(self):
        dominant_detail_emotion = self._detail_emotion_list[self.dominant_index]
        dominant_detail_length =  len(dominant_detail_emotion)
        dominant_power=self.emotion_order[self.dominant_index] 
        dominant_rank = dominant_power / dominant_detail_length
        
        pos_sub_emotion = self.emotion_order[(self.dominant_index + 1)%len(self.emotion_order)]
        minus_sub_emotion = self.emotion_order[(self.dominant_index - 1)%len(self.emotion_order)]
        calc_emotion_index = int((pos_sub_emotion / (pos_sub_emotion + minus_sub_emotion)) * dominant_detail_length)
        
        # # calc_emotion_power = 0
        # # if (sub_emotion_power < 0):
        # #     calc_emotion_power = dominant_power + sub_emotion_power
        # # else:
        # #     calc_emotion_power = sub_emotion_power
        
        # # final_emotion_index = (calc_emotion_power // dominant_rank) - 1
        
        # #   (sub_emotion_power // dominant_rank) + (dominant_detail_length // 2)
        print(self.emotion_order)
        print(self.emotion_order_name[self.dominant_index] , dominant_detail_emotion[int(calc_emotion_index)])
        return self.emotion_order_name[self.dominant_index] , dominant_detail_emotion[int(calc_emotion_index)]