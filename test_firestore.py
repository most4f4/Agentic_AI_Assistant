# test_firestore.py
import os
from google.cloud import firestore

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./firebase-key.json"

try:
    client = firestore.Client(project="ai-assistant-25549")
    doc_ref = client.collection('test').document('test_doc')
    doc_ref.set({'test': 'Hello Firebase!'})
    print("✅ Connection successful!")
except Exception as e:
    print(f"❌ Connection failed: {e}")