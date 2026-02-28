# Create this as backend/audio_engine.py
import gtts
import base64
from io import BytesIO

def text_to_speech_html(text):
    """Generates an invisible HTML audio player that plays the AI response."""
    tts = gtts.gTTS(text=text, lang='en', tld='co.uk') # British accent for "Professor" feel
    fp = BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    audio_b64 = base64.b64encode(fp.read()).decode()
    return f'<audio autoplay src="data:audio/mp3;base64,{audio_b64}"></audio>'