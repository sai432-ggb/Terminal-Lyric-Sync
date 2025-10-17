import time
import requests
import sys
import os
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
import threading

# Optional playback libraries — prefer VLC, fallback to playsound if available
try:
    import playsound as _playsound
    HAS_PLAYSOUND = True
except Exception:
    _playsound = None
    HAS_PLAYSOUND = False

try:
    import vlc
    HAS_VLC = True
except Exception:
    vlc = None
    HAS_VLC = False

# --- Configuration & Setup ---
COLOR_INPUT = '\033[96m'   # Cyan
COLOR_ACTION = '\033[92m'  # Green
COLOR_WARNING = '\033[91m' # Red
COLOR_RESET = '\033[0m'    # Reset color
OUTPUT_FILENAME = "song_lyrics.mp3"
LYRICS_API_BASE_URL = "https://api.lyrics.ovh/v1"


# ...existing code...
def get_song_info_by_speech() -> tuple[str, str] | None:
    """
    Record a short clip via sounddevice and send to Google's recognizer.
    Falls back to manual entry on error.
    """
    import sounddevice as sd
    import numpy as np

    r = sr.Recognizer()
    fs = 16000
    duration = 5  # seconds
    try:
        print(f"\n{COLOR_INPUT}Recording {duration}s from the default microphone...{COLOR_RESET}")
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()
        raw_bytes = recording.tobytes()
        audio_data = sr.AudioData(raw_bytes, fs, 2)  # 2 bytes per sample (int16)
        spoken_text = r.recognize_google(audio_data)
        print(f"{COLOR_ACTION}You said: '{spoken_text}'{COLOR_RESET}")
        parts = spoken_text.split()
        if len(parts) >= 2:
            artist_guess = parts[0]
            title_guess = " ".join(parts[1:])
            return artist_guess, title_guess
        return spoken_text, ""
    except Exception as e:
        print(f"{COLOR_WARNING}Speech capture/recognition failed: {e}{COLOR_RESET}")
        print(f"{COLOR_WARNING}Falling back to manual typing.{COLOR_RESET}")
        return None, None
# ...existing code...

def fetch_lyrics(artist: str, title: str) -> str:
    url = f"{LYRICS_API_BASE_URL}/{artist}/{title}"
    print(f"\n{COLOR_ACTION}Searching for lyrics at: {url}...{COLOR_RESET}")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if 'lyrics' in data:
            return data['lyrics'].strip()
        elif 'error' in data:
            return f"Error: API reported: {data['error']}"
        else:
            return "Error: Lyrics not found or unexpected API response format."
    except requests.exceptions.RequestException as e:
        return f"Error connecting to lyrics API: {e}"


def generate_tts_audio(lyrics: str, filename: str) -> float:
    print(f"\n{COLOR_ACTION}Generating TTS audio file: {filename}...{COLOR_RESET}")
    cleaned_lyrics = "\n".join([line.strip() for line in lyrics.split('\n') if line.strip()])
    try:
        tts = gTTS(text=cleaned_lyrics, lang='en')
        tts.save(filename)
        print(f"{COLOR_ACTION}SUCCESS: Audio saved to '{filename}'.{COLOR_RESET}")
        try:
            audio = AudioSegment.from_mp3(filename)
            duration_s = len(audio) / 1000
            return duration_s
        except Exception:
            print(f"{COLOR_WARNING}Note: Pydub could not determine duration. Is ffmpeg installed? Using default estimate.{COLOR_RESET}")
            return max(1.0, len(cleaned_lyrics) * 0.15)
    except Exception as e:
        print(f"{COLOR_WARNING}TTS Generation Error: {e}{COLOR_RESET}")
        return 0.0


def _start_playback(filename: str) -> tuple[bool, object | None]:
    """
    Attempt to start playback. Returns (started, player_object_or_None).
    Uses playsound if available, otherwise VLC if available.
    """
    # Try playsound (non-blocking where supported)
    if HAS_PLAYSOUND:
        try:
            _playsound.playsound(filename, block=False)
            return True, None
        except TypeError:
            try:
                threading.Thread(target=_playsound.playsound, args=(filename,), daemon=True).start()
                return True, None
            except Exception:
                pass
        except Exception:
            pass

    # Fallback to VLC (recommended on Windows)
    if HAS_VLC:
        try:
            player = vlc.MediaPlayer(filename)
            player.play()
            return True, player
        except Exception:
            pass

    return False, None


def karaoke_display_and_play(lyrics: str, filename: str, duration_s: float):
    lines = [line.strip() for line in lyrics.split('\n') if line.strip()]
    num_lines = len(lines)
    if num_lines == 0 or duration_s <= 0.0:
        print(f"{COLOR_WARNING}Cannot synchronize: No lyrics or zero duration.{COLOR_RESET}")
        return

    time_per_line = (duration_s * 0.95) / num_lines

    print("\n" + "=" * 50)
    print(f"      {COLOR_INPUT}--- Starting Karaoke Playback ---{COLOR_RESET}")
    print("=" * 50)

    started, player = _start_playback(filename)
    if not started:
        print(f"\n{COLOR_ACTION}1. Please start playing the audio file '{filename}' NOW to synchronize.{COLOR_RESET}")
        print(f"{COLOR_ACTION}   (Install python-vlc or playsound to enable automatic playback){COLOR_RESET}\n")
    else:
        print(f"{COLOR_ACTION}Audio playback started automatically.{COLOR_RESET}\n")

    time.sleep(1.0)
    start_time = time.monotonic()

    for i, line in enumerate(lines):
        if time.monotonic() - start_time >= duration_s * 0.98:
            break
        print(f"{COLOR_ACTION}>> {line}{COLOR_RESET}", flush=True)
        time.sleep(time_per_line)

    end_time = time.monotonic()

    # If we used VLC, stop the player to release resources
    if started and player is not None:
        try:
            player.stop()
        except Exception:
            pass

    print("\n" + "=" * 50)
    print(f"      {COLOR_INPUT}--- Karaoke Finished (Elapsed: {end_time - start_time:.2f}s) ---{COLOR_RESET}")
    print("=" * 50 + "\n")


def main():
    print(f"{COLOR_INPUT}--- Python CLI Karaoke/TTS Project (Lyrics.ovh) ---{COLOR_RESET}")
    print("This version fetches real lyrics using a no-key API, creates an MP3, and attempts simultaneous display.\n")

    artist = ""
    title = ""

    print("How would you like to enter the song details? (1) Speak it, (2) Type it: ")
    choice = input(f"{COLOR_INPUT}Enter 1 or 2: {COLOR_RESET}").strip()

    if choice == '1':
        artist, title = get_song_info_by_speech()
        if not artist:
            choice = '2'

    if choice == '2' or not artist:
        print("\n--- Manual Entry ---")
        artist = input("Enter the Artist Name (e.g., John Lennon): ").strip()
        title = input("Enter the Song Title (e.g., Imagine): ").strip()

    artist = artist.replace(" ", "%20")
    title = title.replace(" ", "%20")

    if not artist or not title:
        print(f"{COLOR_WARNING}Artist and Title cannot be empty. Exiting.{COLOR_RESET}")
        return

    lyrics = fetch_lyrics(artist, title)

    if lyrics.startswith("Error"):
        print(f"\n{COLOR_WARNING}{lyrics}{COLOR_RESET}")
    else:
        print("\n" + "=" * 50)
        print(f"      {COLOR_INPUT}--- Lyrics Found ---{COLOR_RESET}")
        print("=" * 50)
        print(f"{COLOR_RESET}{lyrics}")
        print("=" * 50 + "\n")

        duration_s = generate_tts_audio(lyrics, OUTPUT_FILENAME)
        karaoke_display_and_play(lyrics, OUTPUT_FILENAME, duration_s)
        print(f"\n{COLOR_ACTION}The 'singing' session is complete. The audio file '{OUTPUT_FILENAME}' was used for timing.{COLOR_RESET}")


if __name__ == "__main__":
    main()