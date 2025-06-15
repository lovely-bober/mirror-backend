#from celery_app import celery_init_app
from flask import Flask
from flask_socketio import SocketIO
from threading import Lock
from services.gestures_service import GesturesService
from services.voiceRecon_service import VoiceReconService
from services.smartHome_service import SmartHomeService
from services.spotify_service import SpotifyService
import time


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

gestures_service: GesturesService = None
voice_recon_service: VoiceReconService = None
smart_home_service: SmartHomeService = None
spotify_service: SpotifyService = None


def init_services():
    """"Core of the application, initializes all services that are used in the application. It runs in a background thread."""
    
    global gestures_service
    global voice_recon_service
    global smart_home_service
    global spotify_service
     
     
     # Our application is split into several services, each responsible for a specific functionality.
     # First we initialize them by creating their instances. Next we can use them to handle events and execute commands.
     # These services are resuable and can be used in other parts of the application (after the initialization).

    gestures_service = GesturesService()
    voice_recon_service = VoiceReconService()
    smart_home_service = SmartHomeService()
    spotify_service = SpotifyService()
    print("Services initialized")
    last_voice_command = None
    last_gesture_time = 0
    # The main loop of the application, it runs in a background thread and handles events from the services.
    # It emits events to the client and executes commands based on the events.
    while True: 
        if voice_recon_service.current_voice_command != None:
            # emits are for GUI
            socketio.emit("voice_recognition_result", {"command": voice_recon_service.current_voice_command})
            voice_command_handler(voice_recon_service.current_voice_command)
            last_voice_command = voice_recon_service.current_voice_command
        if gestures_service.current_gesture != None and last_gesture_time + 30 < time.time():
            socketio.emit("gesture_recognition_result", {"gesture": gestures_service.current_gesture})
            gesture_command_handler(gestures_service.current_gesture)
            last_gesture_time = time.time()
        socketio.sleep(0)
            
    
# IMPORTANT: services are initialized only when the client connects to the server.
@socketio.on("connect")

def handle_connect():
    """This function is called when a client connects to the server. """
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
    """helper function to start the background task that initializes the services."""
    
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(init_services)
            print("Background task started")
    

def voice_command_handler(command: str):
    """Handles voice commands by executing the appropriate service methods based on the command."""
    global smart_home_service
    global spotify_service
    
    simple_commands = {
        "play": spotify_service.play,
        "pause": spotify_service.stop,
        "next": spotify_service.next,
        "previous": spotify_service.previous,
        "light on": smart_home_service.light_switch,
        "light off": smart_home_service.light_switch,
    }
    
    variable_commands = {
        "set color to": smart_home_service.change_color,
        "set brightness to": smart_home_service.set_rgb_color,
        "increase volume with": spotify_service.increase_volume,
        "decrease volume with": spotify_service.decrease_volume,
        "set volume to": spotify_service.set_volume,
    }
    
    if command in simple_commands:
        simple_commands[command]()
        return
    
    for key, func in variable_commands.items():
        if not command.startswith(key): return
        value = command[len(key):].split()[0]
        try: 
            value = int(value)
        except ValueError:
            try:
                func(value)
            except Exception as e:
                print(f"Error executing command '{command}': {e}")

def gesture_command_handler(gesture: str):
    global smart_home_service
    global spotify_service
    
    raise NotImplementedError
    
if __name__ == '__main__':
    socketio.run(app)
    