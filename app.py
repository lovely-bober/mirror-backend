#from celery_app import celery_init_app
from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)
# app.config.from_mapping(
#     CELERY=dict(
#         task_ignore_result=True,
#     ),
# )
#celery_app = celery_init_app(app)
socketio = SocketIO(app)
services = None

gestures_service = None
voice_recon_service = None
smart_home_service = None



def init_services():
    global gestures_service
    global voice_recon_service
    global smart_home_service

    from services.gestures_service import GesturesService
    from services.voiceRecon_service import VoiceReconService
    from services.smartHome_service import SmartHomeService

    gestures_service = GesturesService()
    voice_recon_service = VoiceReconService()
    smart_home_service = SmartHomeService()
        
    while True:
        if voice_recon_service.recognize_voice_async().done():
            result = voice_recon_service.recognize_voice_async().result()
            if result:
                socketio.emit("voice_recognition_result", {"result": result})
        
            
        
    

@socketio.on("connect")
def handle_connect():
    print("Client connected")
    
@app.route("/api/voice_recognition", methods=["POST"])
def voice_recognition():
    global voice_recon_service
    result = voice_recon_service.recognize_voice()
    if result:
        return {"result": result}, 200
    else:
        return {"error": "Could not recognize voice"}, 500

    
if __name__ == '__main__':
    socketio.run(app)
    services = socketio.start_background_task(init_services)
    