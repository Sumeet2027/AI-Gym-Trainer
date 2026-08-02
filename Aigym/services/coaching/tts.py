import concurrent.futures
from io import BytesIO
from gtts import gTTS

# Shared thread pool so a stuck network call never blocks the app past its timeout.
_executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)


class TextToSpeech:
    def speak(self, text, lang="en"):
        cleaned = (text or "").strip()

        if not cleaned:
            return None

        def _generate():
            buffer = BytesIO()
            gTTS(text=cleaned, lang=lang).write_to_fp(buffer)
            buffer.seek(0)
            return buffer.read()

        try:
            future = _executor.submit(_generate)
            # Hard cap: never let a stuck network call freeze the workout loop.
            return future.result(timeout=6)
        except Exception as e:
            # Network hiccups, gTTS rate limits, or timeouts must never crash
            # or freeze the workout loop -- just skip this line of audio.
            print(f"[TTS] Failed to generate voice, skipping audio: {e}")
            return None