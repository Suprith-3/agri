import time
import requests
import winsound

# --- CONFIGURATION ---
# Replace this with your actual Render URL (e.g., https://your-app.onrender.com)
CLOUD_URL = "http://127.0.0.1:5000" 
POLL_INTERVAL = 1.0  # Check every 1 second

def run_alarm_hub():
    print("--------------------------------------------------")
    print("🛡️  3-EYE LOCAL ALARM HUB INITIALIZED")
    print(f"📡 Monitoring Cloud: {CLOUD_URL}")
    print("--------------------------------------------------")
    
    last_alert_time = 0
    
    while True:
        try:
            # 1. Ping the Cloud Brain /poll endpoint
            response = requests.get(f"{CLOUD_URL}/api/poll", timeout=5)
            data = response.json()
            
            if data['detected']:
                current_timestamp = data['timestamp']
                
                # 2. If it's a NEW detection, trigger the hardware alarm
                if current_timestamp > last_alert_time:
                    animal = data['class_name']
                    print(f"⚠️  ALARM TRIGGERED: {animal.upper()} DETECTED ON PROPERTY!")
                    
                    # Play Windows Hardware Beep (Frequency 1000Hz, Duration 1000ms)
                    for _ in range(3):
                        winsound.Beep(1000, 500)
                        time.sleep(0.1)
                    
                    # 3. Clear the alert in the cloud so it doesn't repeat
                    requests.post(f"{CLOUD_URL}/api/clear")
                    last_alert_time = current_timestamp
            
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error: Is the Cloud Brain online?")
        except Exception as e:
            print(f"❌ Error: {e}")
            
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    run_alarm_hub()
