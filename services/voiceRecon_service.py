from celery import shared_task
import os
import speech_recognition as sr
import concurrent.futures



class VoiceReconService:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
    def recognize_voice_async(self): 
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(recognize_voice, self.recognizer, self.microphone)
            return future
def recognize_voice(recognizer, microphone) -> str | None:
        with microphone as source:
            #print("Say something!")
            audio = recognizer.listen(source)
        # recognize speech using Google Speech Recognition
        try:
            d = recognizer.recognize_google(audio)
            print(f"Google Speech Recognition thinks you said: {d}")
            return d
        except Exception as e:
            print(f"Could not understand audio: {e}")
            return None