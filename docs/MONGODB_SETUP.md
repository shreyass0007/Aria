# MongoDB Setup for Conversation History

Aria now saves all your conversations to MongoDB, allowing you to view and resume previous chats.

## Installation

### Option 1: Local MongoDB (Recommended for Development)
1. **Download MongoDB**:
   - Visit [MongoDB Download Center](https://www.mongodb.com/try/download/community)
   - Download MongoDB Community Server for Windows
   
2. **Install MongoDB**:
   - Run the installer
   - Choose "Complete" installation
   - Install MongoDB as a Service (recommended)
   
3. **Start MongoDB** (if not running as service):
   ```powershell
   mongod
   ```

### Option 2: MongoDB Atlas (Cloud - No Installation Required)
1. Create free account at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free cluster
3. Get connection string (looks like: `mongodb+srv://...`)
4. Add to `.env`:
   ```
   MONGODB_URI=your_connection_string_here
   ```

## Verification

Test your MongoDB connection:
```powershell
d:\CODEING\PROJECTS\ARIA\.venv\Scripts\python.exe verify_mongodb.py
```

## Usage

Once MongoDB is running, Aria will automatically:
- ✅ Save all conversations
- ✅ Show conversation history (click 📜 button)
- ✅ Let you switch between past chats
- ✅ Create new conversations (click ➕ button)

## Features

- **Automatic Saving**: Every message is saved in real-time
- **Smart Titles**: Conversations are automatically titled based on first message
- **Search & Browse**: View all your past conversations
- **Seamless Switching**: Click any conversation to load it
- **New Chats**: Start fresh conversations anytime

## Troubleshooting

**"Not connected" warning**: MongoDB service isn't running
- Local: Run `mongod` in terminal
- Atlas: Check connection string in `.env`

**"No conversations yet"**: Database is empty (normal for first use)

**Connection error**: Check firewall or try MongoDB Atlas instead
