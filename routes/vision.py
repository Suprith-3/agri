from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required
import os
import base64
import time
import numpy as np
import cv2
import requests
import gc

vision_bp = Blueprint('vision', __name__)

# GLOBAL MODEL CONTAINER (Lazy Loaded)
_model = None
# Rate limiting for Telegram alerts
last_alert_time = 0
ALERT_COOLDOWN = 120 # 2 minutes between alerts

def send_telegram_alert(animal_name):
    bot_token = current_app.config.get('TELEGRAM_BOT_TOKEN')
    chat_id = current_app.config.get('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        return False
        
    message = f"🚨 <b>3-EYE SECURITY ALERT!</b> 🚨\n\n⚠️ <b>{animal_name.upper()}</b> detected in your field!\n\n🕒 Time: {time.strftime('%H:%M:%S')}\n📍 Check Dashboard: 3-EYE LIVE FEED"
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
    
    try:
        requests.post(url, json=payload, timeout=5)
        return True
    except Exception as e:
        print(f"Telegram Error: {e}")
        return False

def get_yolo_model():
    """Lazy-load the YOLO model to prevent boot-time OOM on Render."""
    global _model
    if _model is None:
        from ultralytics import YOLO
        # It will load 'yolov8n.pt' which is small (~6MB) but still takes RAM
        _model = YOLO('yolov8n.pt')
    return _model

# Global storage for the latest alert (for local script polling)
latest_alert = {
    "detected": False,
    "class_name": "",
    "timestamp": 0,
    "action": ""
}

@vision_bp.route('/3-eye')
@login_required
def three_eye():
    """Tactical 3-EYE Dashboard."""
    return render_template('vision/three_eye.html')

@vision_bp.route('/api/process', methods=['POST'])
@login_required
def process_frame():
    """Analyze incoming camera frame from browser."""
    global latest_alert
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({"status": "error", "message": "No data"}), 400

        # Decode base64 frame
        img_data = base64.b64decode(data['image'].split(',')[1])
        nparr = np.frombuffer(img_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Run AI Inference (Lazy loaded model)
        model = get_yolo_model()
        results = model.predict(source=frame, conf=0.4, save=False, verbose=False)
        
        detections = []
        found_threat = False
        threat_name = ""
        
        # Specific Agricultural Animal Filter
        threat_classes = ['bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe']
        
        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                label = get_yolo_model().names[cls_id]
                conf = float(box.conf[0])
                
                det = {"class": label, "confidence": conf}
                detections.append(det)

                if label.lower() in threat_classes:
                    found_threat = True
                    threat_name = label
        
        # Update Cloud Status if threat found
        if found_threat:
            global last_alert_time
            current_time = time.time()
            
            latest_alert = {
                "detected": True,
                "class_name": threat_name,
                "timestamp": current_time
            }
            
            # Rate limited Telegram Alert
            if current_time - last_alert_time > ALERT_COOLDOWN:
                if send_telegram_alert(threat_name):
                    last_alert_time = current_time
                    print(f"TELEGRAM NOTIFICATION SENT: {threat_name}")
            
            print(f"SECURITY ALERT: {threat_name} Detected!")

        # Explicit Memory Management for Render
        del frame
        gc.collect()

        return jsonify({
            "status": "success", 
            "found": found_threat, 
            "class": threat_name,
            "detections": detections
        })

    except Exception as e:
        print(f"Cloud Processing Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@vision_bp.route('/api/poll', methods=['GET'])
def poll():
    """Low-latency endpoint for local main.py alarm script."""
    return jsonify(latest_alert)

@vision_bp.route('/api/clear', methods=['POST'])
def clear_alert():
    """Clear alert state after local alarm has been triggered."""
    global latest_alert
    latest_alert["detected"] = False
    return jsonify({"status": "cleared"})
