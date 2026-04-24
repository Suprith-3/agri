import requests
import time
import sys
import json
from datetime import datetime

# ANSI Color Codes for premium CLI feel
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class AgriSmartTester:
    def __init__(self, base_url="http://127.0.0.1:5000", email=None, password=None):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.email = email
        self.password = password
        self.is_logged_in = False

    def log(self, type, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        if type == "info":
            print(f"[{timestamp}] {Colors.OKBLUE}INFO{Colors.ENDC}  - {message}")
        elif type == "success":
            print(f"[{timestamp}] {Colors.OKGREEN}SUCCESS{Colors.ENDC} - {message}")
        elif type == "error":
            print(f"[{timestamp}] {Colors.FAIL}ERROR{Colors.ENDC}   - {message}")
        elif type == "warning":
            print(f"[{timestamp}] {Colors.WARNING}WARN{Colors.ENDC}    - {message}")
        elif type == "header":
            print(f"\n{Colors.BOLD}{Colors.HEADER}=== {message} ==={Colors.ENDC}")

    def test_health(self):
        self.log("header", "Testing Health Endpoint")
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            duration = time.time() - start_time
            if response.status_code == 200 and response.text == "OK":
                self.log("success", f"Health OK ({duration:.2f}s)")
                return True
            else:
                self.log("error", f"Health check failed with status {response.status_code}")
                return False
        except Exception as e:
            self.log("error", f"Could not connect to server: {e}")
            return False

    def test_login(self):
        if not self.email or not self.password:
            self.log("warning", "Skipping login: No credentials provided.")
            return False

        self.log("header", "Testing Authentication")
        try:
            # First GET to check if login page is accessible
            self.session.get(f"{self.base_url}/auth/login")
            
            # POST Login
            data = {
                'email': self.email,
                'password': self.password
            }
            response = self.session.post(f"{self.base_url}/auth/login", data=data, allow_redirects=True)
            
            if "Logged in successfully" in response.text or "Logout" in response.text:
                self.log("success", f"Login successful for {self.email}")
                self.is_logged_in = True
                return True
            else:
                self.log("error", "Login failed. Check credentials or server state.")
                return False
        except Exception as e:
            self.log("error", f"Login attempt failed: {e}")
            return False

    def test_chatbot(self):
        if not self.is_logged_in:
            self.log("warning", "Chatbot test requires login. Skipping.")
            return

        self.log("header", "Testing Chatbot API")
        try:
            payload = {"message": "Hello, how can I improve my crop yield?"}
            response = self.session.post(
                f"{self.base_url}/chatbot/ask",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    bot_text = data.get('response', '')[:100] + "..."
                    self.log("success", f"Chatbot Response: {bot_text}")
                else:
                    self.log("error", f"Chatbot API error: {data.get('message')}")
            else:
                self.log("error", f"Chatbot request failed ({response.status_code})")
        except Exception as e:
            self.log("error", f"Chatbot test crashed: {e}")

    def test_vision_poll(self):
        self.log("header", "Testing Vision Poll API")
        try:
            response = self.session.get(f"{self.base_url}/api/poll")
            if response.status_code == 200:
                data = response.json()
                self.log("success", f"Poll Success. Current State: Detected={data.get('detected')}")
            else:
                self.log("error", f"Poll failed ({response.status_code})")
        except Exception as e:
            self.log("error", f"Vision poll test crashed: {e}")

    def run_all(self):
        print(f"{Colors.BOLD}{Colors.OKCYAN}")
        print("   ___              _  ___                      _   ")
        print("  / _ | ___ _ ____ (_)/ __| _ __  ___ _ _  _ _ | |_ ")
        print(" / __ |/ _` |/ _  || |\\__ \\| '  \\/ _` |/ _|| || |  _|")
        print("/_/ |_|\\_, |\\_,  ||_|/___/|_|_|_|\\_,_|\\__| \\_,_|\\__|")
        print("       |__/ |___/                                    ")
        print(f"             API TEST SUITE v1.0{Colors.ENDC}")
        
        if not self.test_health():
            self.log("error", "Base connectivity check failed. Aborting remaining tests.")
            return

        self.test_login()
        self.test_chatbot()
        self.test_vision_poll()
        
        self.log("header", "Test Suite Complete")

if __name__ == "__main__":
    # If users provide args: python api_tester.py <email> <password> <url>
    email = sys.argv[1] if len(sys.argv) > 1 else None
    password = sys.argv[2] if len(sys.argv) > 2 else None
    url = sys.argv[3] if len(sys.argv) > 3 else "http://127.0.0.1:5000"

    tester = AgriSmartTester(base_url=url, email=email, password=password)
    tester.run_all()
