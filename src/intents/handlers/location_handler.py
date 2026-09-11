import json
import os

def get_location_reply():
    try:
        path = os.path.join(os.path.dirname(__file__), "../../../data/static/location.json")
        with open(path, "r") as f:
            data = json.load(f)
    except:
        data = {"address": "2nd Floor, Ghauri Arcade Plaza, Saleemi Chowk, Satiana Road, Batala Colony, Faisalabad, Punjab 38000, Pakistan.", "maps_url": "https://www.google.com/maps?q=Ghauri+Arcade+Plaza+Saleemi+Chowk+Satiana+Road+Faisalabad", "phone": "0321-7658485", "timings": "Mon-Fri: 10AM-7PM, Sat: 10AM-5PM"}
    
    return f"📍 Address: {data.get('address')}\n🗺️ Maps: {data.get('maps_url')}\n📱 Phone: {data.get('phone')}\n🕒 Timings: {data.get('timings')}"
