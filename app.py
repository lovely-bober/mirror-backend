from celery_app import celery_init_app
from flask import Flask
from celery import shared_task

app = Flask(__name__)
app.config.from_mapping(
    CELERY=dict(
        task_ignore_result=True,
    ),
)
celery_app = celery_init_app(app)

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
    

    

    
def __main__():
    init_services()
    app.run(debug=True)