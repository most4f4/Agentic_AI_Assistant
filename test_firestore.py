# test_firestore.py
import os
from google.cloud import firestore

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./firebase-key.json"

try:
    client = firestore.Client(project="ai-assistant-25549") # Connect to your Firebase project with project ID
    doc_ref = client.collection('test').document('test_doc') # Reference to a test document
    doc_ref.set({'test': 'Hello Firebase!'}) # Write test data to Firestore to verify connection
    print("✅ Connection successful!") 
except Exception as e:
    print(f"❌ Connection failed: {e}")