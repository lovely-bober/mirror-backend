import time
import cv2
import mediapipe as mp
import threading
#from picamera2 import Picamera2
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class GesturesService():
    def __init__(self):
        self.recognizer = None
        self.cam = cv2.VideoCapture(0)
        self.current_gesture = None
        
        base_opts = python.BaseOptions(model_asset_path='gesture_recognizer.task')
        options = vision.GestureRecognizerOptions(
            base_options=base_opts,
            running_mode=vision.RunningMode.LIVE_STREAM,
            num_hands=1,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5,
            result_callback=self.on_result
        )
        try:
            self.recognizer = vision.GestureRecognizer.create_from_options(options)
        except Exception as e:
            print("‼️ Failed to load classifier. Check your .task file. Error:\n", e)

        # 2) Spin up a square camera feed (320×320)
        # self.picam2 = Picamera2()
        # cfg = self.picam2.create_preview_configuration(
        #     main={"format": "BGR888", "size": (320, 320)}
        # )
        # self.picam2.configure(cfg)
        # self.picam2.start()
        if not self.cam.isOpened():
            raise RuntimeError("Failed to open camera")
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 320)
        
        thread = threading.Thread(target=self.main_loop, daemon=True)
        thread.start()
        
        
        print("GesturesService initialized")
        

    def main_loop(self):
        while True:
            ret, frame = self.cam.read()
            #frame = self.picam2.capture_array()
            if frame is None:
                return
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            ts = time.time_ns() // 1_000_000
            self.recognizer.recognize_async(mp_image, ts)
    def stop(self):
        if self.picam2:
            self.picam2.stop()
            self.picam2.close()
        if self.recognizer:
            self.recognizer.close()
        print("GesturesService stopped")

    def on_result(self, result, image, timestamp_ms):
            # result.gestures is a list of lists (one per hand). Skip if empty.
            if not result.gestures:
                return

            for hand_idx, gestures_per_hand in enumerate(result.gestures):
                if not gestures_per_hand:
                    continue
                top_gesture = gestures_per_hand[0]
                if top_gesture.category_name != "None":
                    print(f"→ Hand {hand_idx}: {top_gesture.category_name} "
                    f"({top_gesture.score:.2f}) at {timestamp_ms}")
                    if self.current_gesture != top_gesture.category_name:
                        self.current_gesture = top_gesture.category_name
                
                
                