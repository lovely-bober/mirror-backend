from celery import shared_task
import asyncio
import os
import speech_recognition as sr



class VoiceReconService:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
    def recognize_voice(self) -> str | None:
        
        with self.microphone as source:
            #print("Say something!")
            audio =  self.recognizer.listen(source)
        # recognize speech using Google Speech Recognition
        try:
            d = self.recognizer.recognize_google(audio)
            return d
        except Exception as e:
            #print("Could not understand audio")
            return None
    def recognize_voice_async(self) -> asyncio.Future[str | None]:
        loop = asyncio.get_event_loop()
        result = loop.run_in_executor(None, self.recognize_voice)
        return result
    
    
    