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
    last_voice_time = 0
    last_gesture_time = 0
    last_gesture = None
    # The main loop of the application, it runs in a background thread and handles events from the services.
    # It emits events to the client and executes commands based on the events.
    while True: 
        if voice_recon_service.current_voice_command != None and last_voice_time + 10 < time.time():
            # emits are for GUI
            socketio.emit("voice_recognition_result", {"command": voice_recon_service.current_voice_command})
            voice_command_handler(voice_recon_service.current_voice_command)
            last_voice_command = voice_recon_service.current_voice_command
            last_voice_time = time.time()
            voice_recon_service.current_voice_command = None
        if gestures_service.current_gesture != None and  gestures_service.current_gesture != last_gesture:
            print(f"Gesture recognized: {gestures_service.current_gesture}")
            socketio.emit("gesture_recognition_result", {"gesture": gestures_service.current_gesture})
            gesture_command_handler(gestures_service.current_gesture.lower())
            last_gesture_time = time.time()
            last_gesture = gestures_service.current_gesture
        if last_gesture_time + 45 < time.time():
            # if no gesture is recognized for 45 seconds, reset the last gesture
            print("No gesture recognized for 45 seconds, resetting last gesture")
            last_gesture = None
            gestures_service.current_gesture = None
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
        "play music": spotify_service.play,
        "stop music": spotify_service.stop,
        "next music": spotify_service.next,
        "previous music": spotify_service.previous,
        "next page": smart_mirrow_next,
        "previous page": smart_mirrow_previous,
    }
    
    variable_commands = {
        "color to": smart_home_service.set_color_by_name,
        "colour to": smart_home_service.set_color_by_name,
        "brightness to": smart_home_service.set_rgb_color,
        "increase volume with": spotify_service.increase_volume,
        "decrease volume with": spotify_service.decrease_volume,
        "set volume to": spotify_service.set_volume,
        "light": smart_home_service.light_switch,

    }
    
    if command in simple_commands:
        simple_commands[command]()
        return
    
    print(variable_commands.keys())
    for key in variable_commands:
        print(f"Checking command: {command} against key: {key}")
        if command.find(key)== -1: continue
        try: 
            value = command[len(key):].split()[0]
            value = int(value)
        except ValueError:
            try:
                variable_commands[key](value)
                return
            except Exception as e:
                print(f"Error executing command '{command}': {e}")
        except Exception as e:
            print(f"Error parsing command '{command}': {e}")
            return
        
def smart_mirrow_next():
    """Function to handle the 'next' command for the smart mirror."""
    print("next page")
    socketio.emit("smart_mirror_next")

def smart_mirrow_previous():
    """Function to handle the 'previous' command for the smart mirror."""
    print("prev page")
    socketio.emit("smart_mirror_previous")

def gesture_command_handler(gesture: str):
    
    global smart_home_service
    global spotify_service
    
    #closed_fist, down, left, ok, open_fist, peace, right, rock, stop, up, none
    simple_commands = {
        "closed_fist": spotify_service.play,
        "open_palm": spotify_service.stop,
        "right": spotify_service.next,
        "left": spotify_service.previous,
        "up":  smart_mirrow_next,
        "down": smart_mirrow_previous,
    }
    
    if gesture in simple_commands:
        simple_commands[gesture]()
        return
    
if __name__ == '__main__':
    socketio.run(app, port=4444)
    
