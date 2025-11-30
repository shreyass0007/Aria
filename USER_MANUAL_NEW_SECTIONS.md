# NEW SECTIONS TO ADD TO ARIA_USER_MANUAL.md
# Insert these sections BEFORE the "## 🔧 Troubleshooting" section (line 1059)

---

## 🧠 RAG Memory System

### What is RAG Memory?

RAG (Retrieval-Augmented Generation) Memory allows Aria to remember and search through **ALL** your past conversations, not just the current one. It's like giving Aria a perfect long-term memory!

**How It Works:**
- Every message you send is converted into a "semantic embedding" (meaning-based fingerprint)
- These embeddings are stored in a vector database (ChromaDB)
- When you ask something, Aria searches for relevant past conversations
- The most relevant context is automatically injected into the current response

### Tutorial: Experiencing RAG in Action

**Scenario 1: Restaurant Recommendations**

```
Week 1:
You: "Aria, I loved that Italian place - Mario's Bistro on 5th Street"
Aria: "Glad you enjoyed it! I'll remember that."

Week 3 (different conversation):
You: "Aria, what was that restaurant I mentioned?"
Aria: "You mentioned loving Mario's Bistro on 5th Street! 
       Would you like directions or want to make a reservation?"
```

**What Just Happened?**
- Aria searched across ALL conversations (not just current one)
- Found semantically similar content about restaurants
- Retrieved the specific restaurant name from weeks ago
- Provided contextual response with that information

### Tutorial: Asking About Past Conversations

**Work-Related:**
```
You: "What was that project deadline we discussed last month?"
Aria: [Searches past conversations for deadline mentions]
→ Returns relevant context from previous discussions
```

**Personal Notes:**
```
You: "Did I mention my doctor's appointment date?"
Aria: [Finds past mention in conversation history]
→ "Yes, you scheduled it for December 15th at 2 PM"
```

**Study Topics:**
```
You: "What did we discuss about quantum physics?"
Aria: [Retrieves relevant past conversations]
→ Summarizes previous discussions on the topic
```

### When RAG Memory is Most Helpful

✅ **Great Use Cases:**
- Recalling recommendations (restaurants, books, movies, products)
- Finding past decisions or commitments
- Retrieving information you shared weeks/months ago
- Understanding long-term context and preferences
- Continuing topics from previous conversations
- Remembering personal details you've mentioned

❌ **Not Needed For:**
- Current conversation context (handled by conversation history)
- Real-time facts (Aria doesn't store external web information)
- Web searches (use search commands instead)
- File contents (Aria remembers file operations, not file data)

### Privacy & Data

**What's Stored:**
- Your messages (user) and Aria's responses (assistant)
- Semantic embeddings (mathematical representations of meaning)
- Conversation IDs and timestamps
- Message metadata

**What's NOT Stored:**
- External web content
- Actual file contents (only file operations)
- API keys or sensitive credentials
- Passwords or authentication tokens

**Storage Location:**
All RAG data is stored locally on your computer in:
```
D:\CODEING\PROJECTS\ARIA\vector_db\
```

This folder contains the ChromaDB database. You can delete it anytime to clear all memory.

### Configuration Options

The RAG system uses these settings (configured in `memory_manager.py`):

| Setting | Default Value | Description |
|---------|---------------|-------------|
| `EMBEDDING_MODEL` | `text-embedding-3-small` | OpenAI embedding model used |
| `SIMILARITY_THRESHOLD` | `0.4` | Minimum similarity score (0.0-1.0) |
| `MAX_LONG_TERM_RESULTS` | `5` | Number of past memories to inject |

**To Adjust Settings:**

Edit your `.env` file:
```env
EMBEDDING_MODEL=text-embedding-3-small
SIMILARITY_THRESHOLD=0.4
MAX_LONG_TERM_RESULTS=5
```

**Understanding Similarity Threshold:**
- Lower (e.g., 0.3) = More permissive, retrieves loosely related memories
- Higher (e.g., 0.6) = More strict, only very similar matches
- Default 0.4 = Good balance for most use cases

### Managing Your Memory

**View Memory Statistics:**
Currently stored in `memory_manager.py`. You can check:
- Total messages stored
- Embedding model used
- Current configuration

**Clear All Memories:**
```powershell
python clear_memory.py
```

This resets the vector database completely.

**⚠️ Note:** Clearing memory is permanent! Your conversation history in MongoDB remains intact.

---

## 🤖 Proactive Actions & Automation

### What are Proactive Actions?

Proactive Actions make Aria act **before** you ask! When certain events appear in your calendar, Aria automatically:
- Launches relevant applications
- Enables Do Not Disturb mode
- Sends you timely reminders
- Minimizes distracting apps

**It's like having a proactive assistant who knows your schedule and prepares everything for you!**

### Tutorial 22: Calendar-Triggered Actions

**Scenario: Zoom Meeting Auto-Launch**

**Step 1: Create a calendar event**
```
Event Title: "Zoom Standup @ 10 AM"
Date: Tomorrow
Time: 10:00 AM
```

**Step 2: What happens automatically**
```
At 9:55 AM (5 minutes before):
- Aria speaks: "You have a Zoom meeting in 5 minutes. Opening Zoom."
- Zoom application launches automatically
- You're ready when the meeting starts!
```

**How It Works:**
1. Proactive Manager checks your Google Calendar every 60 seconds
2. Detects the keyword "zoom" in the event title
3. Triggers the action 5 minutes before event starts
4. Launches Zoom application
5. Marks event as "reminded" so it never reminds twice

### Supported Keywords & Automatic Actions

| Keyword in Event Title | What Aria Does |
|------------------------|----------------|
| `zoom` | Opens Zoom application + reminder |
| `teams` | Opens Microsoft Teams + reminder |
| `meet` or `google meet` | Opens browser to meet.google.com |
| `discord` | Opens Discord application |
| `coding` or `dev` | Opens VS Code |
| `focus time` | **Activates Deep Work Mode** |
| `gym` or `workout` | Announces workout time |

### Tutorial 23: Deep Work Mode

**Scenario: Protecting Your Focus Time**

**Step 1: Create a Focus Time event**
```
Event Title: "Focus Time - Write Report"
Date: Today
Time: 2:00 PM - 4:00 PM
```

**Step 2: At 2:00 PM (event starts) - Automatic Actions**
```
Aria announces:
"Focus Time detected. Activating Deep Work mode."

What happens:
✅ Windows Do Not Disturb (DND) enabled
✅ Distracting apps minimized (Discord, Spotify, etc.)
✅ Notifications silenced
✅ Full focus environment created
```

**Step 3: At 4:00 PM (event ends) - Automatic Deactivation**
```
Aria announces:
"Focus Time ended. Deactivating Deep Work mode."

What happens:
✅ DND disabled
✅ Normal operation resumes
✅ Apps can be reopened
```

**What Gets Minimized During Deep Work:**
- Social media apps (Discord, Slack personal channels)
- Chat applications (except work-related ones)
- Email clients (to prevent distractions)
- Entertainment apps (Spotify, YouTube)
- Everything except Aria and your specified work tools

### Real-World Usage Scenarios

**Morning Standup:**
```
Calendar Event: "Daily Standup (Teams) @ 9 AM"
Result at 8:55 AM:
- Aria announces: "Daily standup in 5 minutes. Opening Teams."
- Microsoft Teams launches
- You're ready to join
```

**Client Presentations:**
```
Calendar Event: "Client Demo via Zoom @ 3 PM"
Result at 2:55 PM:
- Aria: "Client Demo starting soon. Opening Zoom."
- Zoom launches
- You have time to test audio/video
```

**Coding Sessions:**
```
Calendar Event: "Dev Time - Feature Implementation @ 10 AM"
Result at 9:55 AM:
- Aria: "Coding session starting soon. Opening VS Code."
- VS Code launches
- Project ready to go
```

**Workout Reminders:**
```
Calendar Event: "Gym Session @ 6 PM"
Result at 5:55 PM:
- Aria: "Time for the gym! Get moving."
- Motivational reminder
```

### Customizing Proactive Actions

**To Add More Keywords** (Advanced Users):

Edit `proactive_manager.py`:

```python
def _trigger_action_for_event(self, event):
    summary = event.get('summary', '').lower()
    
    # Add your custom trigger:
    if "standup" in summary:
        self._speak(f"Standup meeting in 5 minutes. Opening Teams.")
        self.app_launcher.open_desktop_app("teams")
```

**Tips for Event Naming:**
- Use clear keywords: "Zoom Call" not just "Call"
- Be specific: "Focus Time" not just "Work"
- Consistent naming helps: Always use "Teams" for Teams meetings

### Configuration

**Proactive monitoring runs automatically in the background.**

**Default Settings:**
- Check Interval: Every 60 seconds
- Reminder Timing: 5 minutes before events
- Deep Work Trigger: "focus time" in event title (case-insensitive)

**To Disable Proactive Actions** (if needed):

Edit `aria_core.py` and comment out:
```python
# self.proactive_manager.start_monitoring()
```

Then restart Aria.

---

## 📡 Background Services

### Understanding Background Services

Background Services run silently while you use Aria, constantly monitoring your system and calendar to keep you informed and prepared.

**Two Main Services:**
1. **Health Monitor** - Watches battery level and CPU usage
2. **Calendar Scheduler** - Sends intelligent event reminders

These services work 24/7 to ensure you never miss important events or system alerts!

### Tutorial 24: Health Monitoring

**Battery Alerts**

Aria automatically notifies you when your battery needs attention:

**Low Battery Alert:**
```
[Battery drops to 18%]
Aria speaks + UI notification:
"⚠️ Low battery detected: 18%. Please plug in your charger."
```

**When It Triggers:**
- Battery level drops below 20%
- Device is NOT currently charging
- Prevents unexpected shutdowns during work

**High Battery (Optional):**
Some users like to know when fully charged to preserve battery health (feature can be added).

**CPU Alerts**

When your system is under heavy load:

```
[CPU usage hits 94%]
Aria speaks + UI notification:
"⚠️ High CPU usage detected: 94%. Some applications may be slowing down your system."
```

**When It Triggers:**
- CPU usage exceeds 90%
- Sustained for more than a few seconds
- Helps identify performance issues

**Monitoring Frequency:**
- Health checks run every 60 seconds
- Lightweight, minimal system impact
- Alerts spoken via TTS + shown in UI

### Tutorial 25: Calendar Event Reminders

Aria provides two levels of event reminders with AI-generated messages.

**30-Minute Early Reminders (Friendly Heads-Up)**

For events 5-30 minutes away:

```
[Event in 15 minutes]
Aria speaks:
"Excuse me, just a heads up that your meeting starts in 15 minutes."
```

**Example Variations** (LLM-generated):
- "Hey, friendly reminder - your client call is in 20 minutes."
- "Heads up! Team standup starts in 10 minutes."
- "Just so you know, your presentation begins in 25 minutes."

**5-Minute Urgent Reminders**

For imminent events (0-5 minutes away):

```
[Event in 3 minutes]
Aria speaks urgently:
"Hurry up, your meeting starts in 3 minutes!"
```

**Example Variations** (LLM-generated):
- "Quick! Your call starts in 2 minutes!"
- "You need to join now - meeting in 1 minute!"
- "Last call - your event is starting in 4 minutes!"

**Why LLM-Generated Messages?**
- Natural variety (never repetitive)
- Context-aware based on event details
- Appropriate urgency level
- Feels more human and less robotic

### Tutorial 26: UI Notification Queue

**How the System Works:**

```
1. Background service detects event (battery low, meeting soon, etc.)
   ↓
2. Notification added to queue
   ↓
3. Frontend polls /notifications endpoint
   ↓
4. Notification appears in Aria UI
   ↓
5. Queue clears after retrieval
```

**Types of Notifications You'll See:**

**System Alerts:**
```
⚡ Battery: 15% - Please charge
🔥 CPU: 92% - High usage detected
```

**Calendar Reminders:**
```
📅 Team Standup in 10 minutes
⏰ Client Call in 5 minutes - Join now!
```

**Proactive Actions:**
```
🚀 Opening Zoom for your meeting
🎯 Deep Work mode activated
```

**Viewing Notifications:**

Notifications appear automatically in the Aria UI. No manual action needed!

**For Developers** (API Access):
```bash
GET http://localhost:5000/notifications
```

Response:
```json
{
  "status": "success",
  "notifications": [
    {
      "type": "assistant_message",
      "content": "Hurry up, your meeting starts in 5 minutes!",
      "timestamp": "2025-11-30T15:55:00"
    },
    {
      "type": "assistant_message",
      "content": "Low battery: 18%. Please plug in.",
      "timestamp": "2025-11-30T15:50:30"
    }
  ]
}
```

### Configuration & Customization

**Health Monitor Settings:**

Default thresholds:
- Battery alert: Below 20%
- CPU alert: Above 90%
- Check frequency: Every 60 seconds

**Calendar Scheduler Settings:**

Default timing:
- Check frequency: Every 15 minutes (900 seconds)
- Early reminder window: 5-30 minutes before event
- Urgent reminder window: 0-5 minutes before event

**To Modify Settings** (Advanced):

Edit `backend_fastapi.py`:

```python
# Health monitor check interval (line ~794)
await asyncio.sleep(60)  # Change to your preference

# Calendar check interval (line ~755)
await asyncio.sleep(900)  # 900s = 15min, try 300s = 5min
```

**To Disable Background Services** (Not Recommended):

Comment out in `backend_fastapi.py`:
```python
# asyncio.create_task(background_scheduler())
# asyncio.create_task(background_health_monitor())
```

**⚠️ Note:** Disabling these reduces Aria's proactive capabilities significantly.

### Benefits of Background Services

**Never Miss Important Events:**
- Automatic, timely reminders
- Even when Aria UI is minimized
- Works across all your calendars

**System Health Awareness:**
- Prevents unexpected shutdowns
- Early warning for performance issues
- Battery preservation

**Hands-Free Operation:**
- No manual checking needed
- Proactive rather than reactive
- Focus on your work, Aria handles the rest

---

# END OF NEW SECTIONS
# Continue with existing "## 🔧 Troubleshooting" section
