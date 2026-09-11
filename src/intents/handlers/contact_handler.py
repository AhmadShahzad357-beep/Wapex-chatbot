import json
import os

def get_contact_reply():
    try:
        path = os.path.join(os.path.dirname(__file__), "../../../data/static/location.json")
        with open(path, "r") as f:
            data = json.load(f)
    except:
        data = {"phone": "0321-7658485", "email": "wapexposition@gmail.com", "timings": "Mon-Fri: 10AM-7PM, Sat: 10AM-5PM"}
    
    return f"📞 Phone/WhatsApp: {data.get('phone')}\n✉️ Email: {data.get('email')}\n🕒 Timings: {data.get('timings')}"
