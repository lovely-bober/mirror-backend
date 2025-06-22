import threading
import speech_recognition as sr




class VoiceReconService:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.current_voice_command = None
        thread = threading.Thread(target=self.main_loop, daemon=True)
        thread.start()
    def main_loop(self):
        while True:
            self.current_voice_command = recognize_voice(self.recognizer, self.microphone)
            
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
        
        