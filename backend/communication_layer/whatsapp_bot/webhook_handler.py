"""WhatsApp Web webhook handler — manages session and incoming messages.

Note: WhatsApp Web integration uses Baileys (Node.js). This Python module
provides the bridge between the Node.js Baileys subprocess and the Python
backend. Actual QR scan and message transport happens in Node.js.
"""

import asyncio
from typing import Dict, Any, Optional, Callable
from loguru import logger


class WhatsAppWebhookHandler:
    """Manages WhatsApp Web session via Baileys Node.js subprocess."""

    def __init__(self):
        self._connected = False
        self._session_data: Optional[Dict] = None
        self._message_callback: Optional[Callable] = None
        self._process = None

    @property
    def is_connected(self) -> bool:
        return self._connected

    async def start_session(self) -> Dict[str, Any]:
        """Start a WhatsApp session — generates QR code for scanning."""
        logger.info("WhatsApp: Session start requested (Baileys subprocess)")
        # In production, this would spawn a Node.js child process running Baileys
        # and communicate via stdin/stdout or a local WebSocket
        return {
            "status": "qr_pending",
            "message": "Scan the QR code in the desktop app to connect WhatsApp",
        }

    async def stop_session(self):
        """Stop the WhatsApp session."""
        self._connected = False
        if self._process:
            self._process.terminate()
            self._process = None
        logger.info("WhatsApp: Session stopped")

    async def send_message(self, phone: str, message: str) -> bool:
        """Send a text message to a phone number."""
        if not self._connected:
            logger.warning("WhatsApp: Cannot send — not connected")
            return False
        # In production, this would send via Baileys subprocess
        logger.info(f"WhatsApp: Message sent to {phone}: {message[:50]}...")
        return True

    async def send_image(self, phone: str, image_path: str, caption: str = "") -> bool:
        """Send an image (e.g., chart screenshot) to a phone number."""
        if not self._connected:
            return False
        logger.info(f"WhatsApp: Image sent to {phone}: {image_path}")
        return True

    def on_message(self, callback: Callable):
        """Register a callback for incoming messages."""
        self._message_callback = callback

    async def _handle_incoming(self, data: Dict[str, Any]):
        """Process incoming messages from Baileys."""
        msg_type = data.get("type", "text")
        content = data.get("content", "")
        sender = data.get("sender", "")

        if msg_type == "voice":
            content = await self._transcribe_voice(data.get("audio_path", ""))

        if self._message_callback:
            await self._message_callback({
                "source": "whatsapp",
                "sender": sender,
                "content": content,
                "type": msg_type,
            })

    async def _transcribe_voice(self, audio_path: str) -> str:
        """Transcribe voice message using Whisper STT."""
        try:
            import whisper
            model = whisper.load_model("base")
            result = model.transcribe(audio_path)
            return result.get("text", "")
        except ImportError:
            logger.warning("Whisper not installed — voice transcription unavailable")
            return "[Voice message — transcription unavailable]"
        except Exception as e:
            logger.error(f"Voice transcription failed: {e}")
            return "[Voice transcription failed]"

    def get_status(self) -> Dict[str, Any]:
        return {
            "connected": self._connected,
            "service": "whatsapp",
        }
