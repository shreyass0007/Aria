# System Control Module Documentation

## Overview
The System Control module provides Aria with comprehensive system-level control capabilities on Windows, including volume management, power control, and system maintenance.

## Features

### 1. Volume Control
Control your system's audio settings with natural voice commands.

#### Voice Commands
- **Check Volume**: "What's the volume?", "Check volume", "What is current volume"
- **Set Volume**: "Set volume to 50", "Volume 75"
- **Increase Volume**: "Increase volume", "Turn up volume", "Louder", "Volume up"
- **Decrease Volume**: "Decrease volume", "Turn down volume", "Quieter", "Volume down"
- **Mute**: "Mute system", "Mute volume"
- **Unmute**: "Unmute system", "Unmute volume"

#### Examples
```
You: "Aria, increase volume"
Aria: "Volume increased to 60%"

You: "Aria, set volume to 30"
Aria: "Volume set to 30%"

You: "Aria, mute"
Aria: "System muted"
```

### 2. Power Management
Manage your system's power state with safety confirmations.

#### Voice Commands
- **Lock Screen**: "Lock the system", "Lock computer", "Lock screen"
- **Sleep**: "Put computer to sleep", "Sleep system", "Go to sleep"
- **Shutdown**: "Shutdown computer", "Shut down system"
  - Includes 10-second timer for safety
  - Cancel with: "Cancel shutdown"
- **Restart**: "Restart computer", "Restart system", "Reboot"
  - Includes 10-second timer for safety
  - Cancel with: "Cancel restart"

#### Safety Features
- Shutdown and restart commands include a 10-second countdown
- You can cancel these operations by saying "cancel shutdown" or "cancel restart"
- Lock and sleep execute immediately

#### Examples
```
You: "Aria, lock the system"
Aria: "Locking workstation"

You: "Aria, shutdown computer"
Aria: "Are you sure? Shutting down in 10 seconds. Say 'cancel shutdown' to abort."
[Wait a moment]
You: "Aria, cancel shutdown"
Aria: "Shutdown/restart cancelled"
```

### 3. System Maintenance
Keep your system clean with recycle bin management.

#### Voice Commands
- **Check Recycle Bin**: "Check recycle bin", "What's in the recycle bin", "Recycle bin size"
- **Empty Recycle Bin**: "Empty recycle bin", "Empty trash", "Clear recycling"

#### Examples
```
You: "Aria, check recycle bin"
Aria: "Recycle bin contains 23 items (145.67 MB)"

You: "Aria, empty recycle bin"
Aria: "Recycle bin contains 23 items (145.67 MB). Emptying it now..."
Aria: "Recycle bin emptied successfully"
```

## Technical Details

### Dependencies
The system control module requires three additional Python packages:
- **pycaw**: For audio volume control
- **comtypes**: For COM interface support
- **winshell**: For recycle bin management

Install with:
```bash
pip install pycaw comtypes winshell
```

### Module Structure
The `SystemControl` class in `system_control.py` provides:
- Audio interface initialization using Windows Core Audio APIs
- Volume manipulation methods (get, set, increase, decrease, mute, unmute)
- Power management commands using Windows system calls
- Recycle bin operations using winshell

### Integration
The module is integrated into `aria_core.py`:
1. Imported as `from system_control import SystemControl`
2. Initialized in `AriaCore.__init__()` as `self.system_control`
3. Voice commands are processed in the `process_command()` method

## Error Handling
All system control operations include comprehensive error handling:
- Audio interface failures are gracefully handled
- Power management errors are reported to the user
- Recycle bin operations handle empty states and errors

## Platform Support
Currently supports **Windows only**. The module uses Windows-specific APIs:
- Windows Core Audio API for volume control
- Windows system commands for power management
- Windows recycle bin for maintenance

## Safety Considerations
1. **Shutdown/Restart**: Include 10-second timers with cancellation options
2. **Recycle Bin**: Empties without confirmation dialog (by design for voice control)
3. **Volume**: Clamped between 0-100% to prevent extreme values
4. **Lock Screen**: Executes immediately (standard security practice)

## Future Enhancements
Potential improvements:
- Cross-platform support (macOS, Linux)
- Display brightness control
- Network adapter management
- More granular timer controls
- Configurable safety timers
