from celery import shared_task
import asyncio
import os
import speech_recognition as sr



class VoiceReconService:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        # self.loop = asyncio.new_event_loop()
        # asyncio.set_event_loop(self.loop)
    def recognize_voice(self) -> str:
        
        with self.microphone as source:
            print("Say something!")
            audio =  self.recognizer.listen(source)
        # recognize speech using Google Speech Recognition
        try:
            d = self.recognizer.recognize_google(audio)
            return d
        except Exception as e:
            print("Could not understand audio")
            return None
    
    def recognize_voice_task(self):
        result = self.loop.run_until_complete(self.recognize_voice())
        return result