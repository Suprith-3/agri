import os
from twilio.rest import Client
import time

class AlertSystem:
    def __init__(self):
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.twilio_phone = os.getenv('TWILIO_PHONE_NUMBER')
        self.client = None
        
        if self.account_sid and self.auth_token:
            try:
                self.client = Client(self.account_sid, self.auth_token)
            except Exception as e:
                print(f"[Twilio Init Error] {e}")

    def make_automated_call(self, target_phone, animal_name):
        """Initiates an automated voice call to the farmer."""
        if not self.client or not self.twilio_phone:
            print("[AlertSystem] Twilio not configured.")
            return False
            
        try:
            # TwiML for the call message
            twiml = f'''
                <Response>
                    <Say voice="alice">Attention! This is BHOOMITRA 3-EYE Security alert. A {animal_name} has been detected in your field. Please check your dashboard immediately.</Say>
                    <Pause length="1"/>
                    <Say>I repeat, a {animal_name} is in your farm.</Say>
                    <Hangup/>
                </Response>
            '''
            
            call = self.client.calls.create(
                to=target_phone,
                from_=self.twilio_phone,
                twiml=twiml
            )
            print(f"[AlertSystem] Call initiated: {call.sid}")
            return True
        except Exception as e:
            print(f"[AlertSystem] Call failed: {e}")
            return False

    def send_whatsapp_alert(self, target_phone, animal_name):
        """Sends a WhatsApp message with the alert."""
        if not self.client or not self.twilio_phone:
            return False
            
        try:
            message = self.client.messages.create(
                from_=f'whatsapp:{self.twilio_phone}',
                body=f"🚨 *BHOOMITRA 3-EYE ALERT* 🚨\n\n⚠️ *{animal_name.upper()}* detected in your field!\n\n🕒 Time: {time.strftime('%H:%M:%S')}\n📍 Check Live Feed: https://bhoomitra.onrender.com/vision/3-eye",
                to=f'whatsapp:{target_phone}'
            )
            print(f"[AlertSystem] WhatsApp sent: {message.sid}")
            return True
        except Exception as e:
            print(f"[AlertSystem] WhatsApp failed: {e}")
            return False
