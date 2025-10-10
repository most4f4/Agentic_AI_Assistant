# 🔥 Firebase Firestore Setup Guide

Complete guide to add cloud storage to your AI Assistant.

---

## 🎯 Why Use Firebase Firestore?

### **Benefits:**
- ☁️ **Cloud Storage** - Messages persist across sessions
- 🔄 **Multi-device** - Access from any device
- 👥 **User Management** - Track conversations per user
- 📊 **Analytics** - Analyze usage patterns
- 🆓 **Free Tier** - Generous free quota

---

## 📋 Step-by-Step Setup

### **Step 1: Create Firebase Project**

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add project"
3. Enter project name (e.g., "ai-assistant")
4. Follow the setup wizard
5. **Copy your Project ID** (e.g., `ai-assistant-12345`)

---

### **Step 2: Enable Firestore**

1. In Firebase Console, click "Firestore Database"
2. Click "Create database"
3. Choose **"Start in production mode"**
4. Select your region (choose closest to you)
5. Click "Enable"

---

### **Step 3: Set Up Security Rules** (Important!)

1. In Firestore, go to "Rules" tab
2. Replace with these rules:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Allow read/write to chat_sessions collection
    match /chat_sessions/{session} {
      allow read, write: if true;  // For development
      // For production, add authentication:
      // allow read, write: if request.auth != null;
    }
  }
}
```

3. Click "Publish"

**⚠️ Note:** These rules allow anyone to read/write. For production, add authentication!

---

### **Step 4: Create Service Account**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your Firebase project
3. Go to **IAM & Admin → Service Accounts**
4. Click **"Create Service Account"**
5. Name it: `langchain-assistant`
6. Click **"Create and Continue"**
7. **Grant Role:** Select **"Cloud Datastore Owner"**
   - For production: Use "Cloud Datastore User" instead
8. Click **"Continue"** then **"Done"**

---

### **Step 5: Generate Service Account Key**

1. Click on your new service account
2. Go to **"Keys"** tab
3. Click **"Add Key" → "Create new key"**
4. Choose **JSON**
5. Click **"Create"**
6. A JSON file downloads (e.g., `ai-assistant-12345-a1b2c3d4.json`)
7. **Keep this file secure!** It's like a password

---

### **Step 6: Configure Your Project**

1. Move the JSON file to your project root:
   ```bash
   mv ~/Downloads/ai-assistant-*.json ./firebase-key.json
   ```

2. Update `.env` file:
   ```bash
   # Add to your .env file
   GOOGLE_APPLICATION_CREDENTIALS=./firebase-key.json
   ```

3. Update `config/settings.py`:
   ```python
   FIRESTORE_CONFIG = {
       "enabled": True,  # ← Set to True
       "project_id": "ai-assistant-12345",  # ← Your project ID
       "collection_name": "chat_sessions",
       "auto_save": True,
   }
   ```

4. Add to `.gitignore`:
   ```bash
   # Add this line to .gitignore
   firebase-key.json
   ```

---

### **Step 7: Install Dependencies**

```bash
pip install google-cloud-firestore langchain-google-firestore
```

Or add to `requirements.txt`:
```
google-cloud-firestore>=2.11.0
langchain-google-firestore>=0.1.0
```

---

### **Step 8: Enable Firestore API**

1. Go to [Firestore API Page](https://console.cloud.google.com/apis/library/firestore.googleapis.com)
2. Select your project
3. Click **"Enable"**

---

### **Step 9: Test Connection**

Run this test script:

```python
# test_firestore.py
import os
from google.cloud import firestore

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./firebase-key.json"

try:
    client = firestore.Client(project="your-project-id")
    doc_ref = client.collection('test').document('test_doc')
    doc_ref.set({'test': 'Hello Firebase!'})
    print("✅ Connection successful!")
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

```bash
python test_firestore.py
```

---

## 🚀 Using Cloud Storage

### **In Your App:**

1. **Start the app:**
   ```bash
   streamlit run app.py
   ```

2. **You'll see in sidebar:**
   ```
   ☁️ Cloud Storage
   ✅ Connected to Firebase
   Session: a1b2c3d4...
   
   [💾 Save to Cloud] [📥 Load from Cloud]
   ☑️ Auto-save messages
   ```

3. **Features:**
   - **Auto-save**: Every message saved automatically
   - **Manual save**: Click "💾 Save to Cloud"
   - **Load**: Click "📥 Load from Cloud"
   - **New session**: Start fresh chat
   - **Session list**: See all saved sessions

---

## 📊 View Your Data

### **In Firebase Console:**

1. Go to Firestore Database
2. Click "chat_sessions" collection
3. You'll see documents (one per session)
4. Click a document to see messages

**Structure:**
```
chat_sessions/
├── session-uuid-1/
│   └── history: [
│       {type: "human", data: {content: "Hello"}},
│       {type: "ai", data: {content: "Hi there!"}}
│   ]
├── session-uuid-2/
│   └── history: [...]
```

---

## 🔧 Configuration Options

### **In `config/settings.py`:**

```python
FIRESTORE_CONFIG = {
    # Enable/disable cloud storage
    "enabled": True,
    
    # Your Firebase project ID
    "project_id": "your-project-id",
    
    # Firestore collection name
    "collection_name": "chat_sessions",
    
    # Auto-save after each message
    "auto_save": True,
}
```

---

## 💰 Pricing

### **Firestore Free Tier (Generous!):**
- 1 GB storage
- 50,000 reads/day
- 20,000 writes/day
- 20,000 deletes/day

**For typical usage:**
- ~1000 messages = ~1 MB
- ~50 active users/day = well within limits

**Paid tier:** Only $0.18/GB after free tier

[Full Pricing Details](https://firebase.google.com/pricing)

---

## 🛡️ Security Best Practices

### **Development (Current Setup):**
```javascript
// Allow anyone to read/write
allow read, write: if true;
```

### **Production (Recommended):**

1. **Add Firebase Authentication:**
   ```bash
   pip install firebase-admin
   ```

2. **Update Firestore Rules:**
   ```javascript
   rules_version = '2';
   service cloud.firestore {
     match /databases/{database}/documents {
       match /chat_sessions/{userId}/{document=**} {
         // Only allow users to access their own sessions
         allow read, write: if request.auth != null 
                            && request.auth.uid == userId;
       }
     }
   }
   ```

3. **Add User Authentication in App:**
   ```python
   # Use user ID as session prefix
   session_id = f"{user_id}_{uuid.uuid4()}"
   ```

---

## 🧪 Testing

### **Test 1: Save and Load**
```
1. Start app
2. Send a message: "Hello"
3. Click "💾 Save to Cloud"
4. Clear local chat
5. Click "📥 Load from Cloud"
✅ Message should reappear
```

### **Test 2: Auto-save**
```
1. Enable "Auto-save messages"
2. Send several messages
3. Refresh page
4. Click "📥 Load from Cloud"
✅ All messages should load
```

### **Test 3: Multiple Sessions**
```
1. Have a conversation
2. Click "🆕 New Session"
3. Have different conversation
4. Open session dropdown
✅ See both sessions listed
```

---

## ⚠️ Troubleshooting

### **"Failed to connect to Firestore"**

**Check:**
1. Is `GOOGLE_APPLICATION_CREDENTIALS` set correctly?
   ```bash
   echo $GOOGLE_APPLICATION_CREDENTIALS
   ```

2. Does the JSON file exist?
   ```bash
   ls -la firebase-key.json
   ```

3. Is the project ID correct in `config/settings.py`?

4. Is Firestore API enabled?

---

### **"Permission denied"**

**Solution:**
1. Check Firestore Rules allow access
2. Verify service account has "Cloud Datastore Owner" role
3. Try re-creating service account key

---

### **"Collection not found"**

**Solution:**
- Collections are created automatically on first write
- Send a message and save it
- Check Firebase Console

---

## 📝 Quick Reference

### **Environment Variables:**
```bash
GOOGLE_APPLICATION_CREDENTIALS=./firebase-key.json
```

### **Config:**
```python
# config/settings.py
FIRESTORE_CONFIG = {
    "enabled": True,
    "project_id": "your-project-id",
    "collection_name": "chat_sessions",
    "auto_save": True,
}
```

### **Usage:**
```python
from utils.firestore_manager import init_firestore, save_current_chat

# Initialize
firestore = init_firestore("your-project-id")

# Save messages
save_current_chat(session_id)

# Load messages
messages = firestore.load_messages(session_id)
```

---

## 🎓 Advanced Features

### **1. User-Specific Sessions**

If you add user authentication:

```python
# In app.py
def get_user_id():
    """Get current user ID from authentication"""
    # Your auth logic here
    return "user123"

# Create user-specific session
user_id = get_user_id()
session_id = f"{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
st.session_state.session_id = session_id
```

---

### **2. Session Naming**

Add custom names to sessions:

```python
# Save with metadata
firestore_manager.client.collection("chat_sessions").document(session_id).set({
    "name": "Project Planning Chat",
    "created_at": datetime.now(),
    "tags": ["work", "planning"]
})
```

---

### **3. Search Messages**

Find messages across sessions:

```python
def search_messages(firestore_manager, query):
    """Search for messages containing query"""
    sessions = firestore_manager.client.collection("chat_sessions").stream()
    results = []
    
    for session in sessions:
        messages = session.to_dict().get("history", [])
        for msg in messages:
            if query.lower() in msg.get("data", {}).get("content", "").lower():
                results.append({
                    "session_id": session.id,
                    "message": msg
                })
    
    return results
```

---

### **4. Export Conversations**

Export to JSON or PDF:

```python
import json

def export_session(firestore_manager, session_id, filename):
    """Export session to JSON"""
    messages = firestore_manager.load_messages(session_id)
    
    with open(filename, 'w') as f:
        json.dump({
            "session_id": session_id,
            "messages": messages,
            "exported_at": datetime.now().isoformat()
        }, f, indent=2)
    
    print(f"✅ Exported to {filename}")
```

---

### **5. Analytics Dashboard**

Track usage metrics:

```python
def get_usage_stats(firestore_manager):
    """Get usage statistics"""
    sessions = firestore_manager.client.collection("chat_sessions").stream()
    
    total_sessions = 0
    total_messages = 0
    
    for session in sessions:
        total_sessions += 1
        messages = session.to_dict().get("history", [])
        total_messages += len(messages)
    
    return {
        "total_sessions": total_sessions,
        "total_messages": total_messages,
        "avg_messages_per_session": total_messages / total_sessions if total_sessions > 0 else 0
    }
```

---

## 🔄 Migration from Local to Cloud

### **If you have existing local chats:**

```python
# migrate_to_cloud.py
import streamlit as st
from utils.firestore_manager import init_firestore

def migrate_local_to_cloud():
    """Migrate local session state to Firestore"""
    firestore = init_firestore("your-project-id")
    
    # Get local messages
    local_messages = st.session_state.get("messages", [])
    
    if local_messages:
        # Create new session
        session_id = str(uuid.uuid4())
        
        # Save to cloud
        firestore.save_messages_batch(session_id, local_messages)
        
        print(f"✅ Migrated {len(local_messages)} messages")
        print(f"Session ID: {session_id}")
    else:
        print("No local messages to migrate")
```

---

## 📱 Multi-Platform Support

### **Access from Different Devices:**

1. **Desktop:** Run Streamlit app
2. **Mobile:** Access via IP address
   ```bash
   streamlit run app.py --server.address=0.0.0.0
   # Access at: http://your-ip:8501
   ```
3. **Cloud Deploy:** Use Streamlit Cloud
   - Same session ID works everywhere!

---

## 🎯 Summary

### **What You Get:**

✅ **Persistent Storage** - Messages saved to cloud  
✅ **Session Management** - Multiple conversations  
✅ **Auto-save** - Automatic cloud backup  
✅ **Session Recovery** - Resume from any device  
✅ **User Tracking** - Analytics and insights  

### **Quick Start:**

```bash
# 1. Set up Firebase (Steps 1-8 above)
# 2. Install dependencies
pip install google-cloud-firestore langchain-google-firestore

# 3. Configure
# Add to .env:
GOOGLE_APPLICATION_CREDENTIALS=./firebase-key.json

# Update config/settings.py:
FIRESTORE_CONFIG = {
    "enabled": True,
    "project_id": "your-project-id",
}

# 4. Run
streamlit run app.py
```

### **Using the App:**

1. Messages auto-save (if enabled)
2. Click "💾 Save" to backup manually
3. Click "📥 Load" to restore
4. Switch sessions from dropdown
5. Create new sessions anytime

---

## 🆘 Need Help?

### **Common Issues:**

| Issue | Solution |
|-------|----------|
| Connection fails | Check credentials path |
| Permission denied | Update Firestore rules |
| API not enabled | Enable in Google Cloud |
| Slow performance | Check Firestore indexes |

### **Resources:**

- [Firebase Documentation](https://firebase.google.com/docs/firestore)
- [LangChain Firestore Integration](https://python.langchain.com/docs/integrations/memory/google_firestore/)
- [Firestore Security Rules](https://firebase.google.com/docs/firestore/security/get-started)

---

## 🎉 You're Ready!

Your AI Assistant now has:
- ☁️ Cloud storage
- 💾 Auto-save
- 🔄 Session management
- 📊 Data persistence
- 👥 Multi-user support

**Start chatting and your conversations are safely stored in the cloud!** 🚀

---

## 📋 Checklist

Before going live:

- [ ] Firebase project created
- [ ] Firestore enabled
- [ ] Service account created with key
- [ ] JSON key file downloaded
- [ ] `GOOGLE_APPLICATION_CREDENTIALS` set in .env
- [ ] `FIRESTORE_CONFIG` updated in settings
- [ ] Dependencies installed
- [ ] Connection tested
- [ ] Security rules configured
- [ ] `.gitignore` updated (firebase-key.json)
- [ ] Backup strategy planned

**All done? Start using cloud storage!** 🎊
