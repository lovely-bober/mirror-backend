#from celery_app import celery_init_app
from flask import Flask
from flask_socketio import SocketIO
from threading import Lock

app = Flask(__name__)
# app.config.from_mapping(
#     CELERY=dict(
#         task_ignore_result=True,
#     ),
# )
#celery_app = celery_init_app(app)
socketio = SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*",async_mode= 'threading')
thread = None
thread_lock = Lock()

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
    print("Services initialized")
    last_voice_command = None
    last_gesture = None
    #recon.add_done_callback(lambda future: on_voice_recognition_result(future.result()))

    while True: 
        if voice_recon_service.current_voice_command != None and voice_recon_service.current_voice_command != last_voice_command:
            socketio.emit("voice_recognition_result", {"command": voice_recon_service.current_voice_command})
            last_voice_command = voice_recon_service.current_voice_command
        if gestures_service.current_gesture != None and gestures_service.current_gesture != last_gesture:
            socketio.emit("gesture_recognition_result", {"gesture": gestures_service.current_gesture})
            last_gesture = gestures_service.current_gesture
        socketio.sleep(0)
            
    

@socketio.on("connect")
def handle_connect():
    start_background_tasks()
    print("Client connected")
    
    
@app.route("/api/voice_recognition", methods=["POST"])
def voice_recognition():
    global voice_recon_service
    result = voice_recon_service.recognize_voice()
    if result:
        return {"result": result}, 200
    else:
        return {"error": "Could not recognize voice"}, 500
    

def start_background_tasks():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(init_services)
            print("Background task started")
    
if __name__ == '__main__':
    socketio.run(app)
    
    
    
    
    