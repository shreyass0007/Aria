# Water Reminder Functionality

I have implemented a water reminder feature that reminds you to drink water at set intervals.

## Features
- **Start/Stop Reminder**: You can start or stop the reminder using voice commands.
- **Custom Interval**: You can set the reminder interval (default is 90 minutes).
- **Notifications**: Sends a system notification and speaks a reminder message.
- **Reset Timer**: You can tell Aria you drank water to reset the timer.

## Voice Commands
- "Start water reminder" / "Remind me to drink water"
- "Stop water reminder"
- "Set water reminder to 30 minutes"
- "I drank water" (Resets the timer)

## Implementation Details
- **`aria/water_manager.py`**: New class `WaterManager` that handles the timer and notifications.
- **`aria/aria_core.py`**: Integrated `WaterManager` into the core system.
- **`aria/command_processor.py`**: Added logic to handle water-related voice commands.

## Verification
- Created and ran `tests/test_water_manager.py` to verify the logic.
- All tests passed.
