import firebase_admin
from firebase_admin import credentials, firestore
import os, json

cred = credentials.Certificate(os.path.join(os.path.dirname(__file__), 'firebase_key.json'))
firebase_admin.initialize_app(cred)
db = firestore.client()

def seed():
    # sample venue
    v1 = {
        "name": "Sunshine Sports Complex",
        "description": "Indoor badminton courts, clean & bright",
        "address": "101 Main St, City",
        "city": "Mumbai",
        "sports": ["badminton","tennis"],
        "amenities": ["parking","lighting"],
        "photos": [],
        "starting_price_per_hour": 300,
        "approved": True,
        "created_at": firestore.SERVER_TIMESTAMP
    }
    vref = db.collection('venues').document()
    vref.set(v1)
    print("Created venue:", vref.id)

    # create courts for the venue
    courts = [
        {"venue_id": vref.id, "name": "Court A", "sport_type": "badminton", "price_per_hour": 300},
        {"venue_id": vref.id, "name": "Court B", "sport_type": "badminton", "price_per_hour": 300},
    ]
    for c in courts:
        cref = db.collection('courts').document()
        cref.set(c)
        print("Created court:", cref.id)

if __name__ == "__main__":
    seed()
