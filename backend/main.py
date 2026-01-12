import sys
import io
import asyncio
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Force UTF-8 encoding for Windows console to prevent crashes with emojis
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.dependencies import init_dependencies, get_system_monitor, get_aria_core
from backend.routers import chat, voice, music, system, notion, general, dashboard, websocket

from aria.logger import setup_logger

logger = setup_logger(__name__)

# Background Tasks
async def background_scheduler():
    """Runs scheduled tasks periodically."""
    logger.info("Background Scheduler Started")
    while True:
        try:
            # Add your scheduled tasks here
            # e.g., aria.proactive_manager.check_calendar()
            # For now, we just sleep
            await asyncio.sleep(60)
        except asyncio.CancelledError:
            logger.info("Scheduler cancelled")
            break
        except Exception as e:
            logger.error(f"Scheduler Error: {e}")
            await asyncio.sleep(60)

async def background_health_monitor():
    """Monitors system health periodically."""
    logger.info("Health Monitor Started")
    while True:
        try:
            monitor = get_system_monitor()
            aria = get_aria_core()
            if monitor and aria:
                alerts = monitor.check_health()
                for alert in alerts:
                    logger.warning(f"Health Alert: {alert}")
                    aria.tts_manager.speak(alert)
            
            await asyncio.sleep(60) # Check every 1 minute
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Health Monitor Error: {e}")
            await asyncio.sleep(60)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_dependencies()
    
    # Start background tasks
    scheduler_task = asyncio.create_task(background_scheduler())
    health_task = asyncio.create_task(background_health_monitor())
    
    yield
    
    # Shutdown
    scheduler_task.cancel()
    health_task.cancel()
    
    # Clean up Aria resources
    aria = get_aria_core()
    if aria:
        if aria.wake_word_listener:
            aria.wake_word_listener.stop()
        if aria.tts_manager:
            aria.tts_manager.stop()

app = FastAPI(lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(general.router)
app.include_router(chat.router)
app.include_router(voice.router)
app.include_router(music.router)
app.include_router(system.router)
app.include_router(notion.router)
app.include_router(notion.router)
app.include_router(dashboard.router)
app.include_router(websocket.router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
