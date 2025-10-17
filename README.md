# Lyrics Singer CLI

A small Python CLI that:
- Fetches song lyrics from the Lyrics.ovh API.
- Converts lyrics to speech (MP3) using gTTS.
- Attempts synchronized on-screen karaoke-style lyric display while playing the generated MP3.
- Supports microphone-based song/title capture (optional) and manual entry fallback.

---

## Features
- Fetches real lyrics (no API key required).
- Generates TTS audio (gTTS -> MP3).
- Attempts automatic playback using python-vlc (preferred) or playsound if available.
- Falls back to manual playback if automatic playback is not available.
- Lightweight CLI with ANSI-colored output.

---

## Requirements

Recommended Python
- Python 3.10 or 3.11 (some packages and prebuilt wheels behave better on these versions). Python 3.13 can work but some packages (playsound, PyAudio) may have compatibility issues.

Python packages (installed in a virtual environment)
- requests
- gTTS
- pydub
- SpeechRecognition
- python-vlc (recommended)
- sounddevice, soundfile, numpy (optional — for microphone recording without PyAudio)

System tools
- VLC Player (VideoLAN) — required for python-vlc runtime on Windows.
- FFmpeg — required by pydub to determine audio duration reliably.

---

## Quick setup (PowerShell)

1. Open PowerShell and go to the project folder:
```powershell
cd 
```

2. Create and activate a virtual environment:
```powershell
py -3 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned -Force
.\.venv\Scripts\Activate.ps1
```

3. Upgrade pip and install Python dependencies:
```powershell
pip install --upgrade pip
pip install requests gTTS pydub SpeechRecognition python-vlc sounddevice soundfile numpy
```

4. Install system tools:
- VLC (download or use winget):
```powershell
winget install --id=VideoLAN.VLC -e
```
- FFmpeg (with Chocolatey or download):
```powershell
choco install ffmpeg -y
```
Or download ffmpeg and add its `bin` folder to PATH. Restart terminal after installing.

---

## Run

With the venv activated:
```powershell
python "Lyrics Singer CLI.py"
```

Follow prompts:
- Choose "1" to record artist/title (requires microphone and sounddevice installed).
- Choose "2" to type artist/title manually.

If automatic playback works you will see synchronized lyric lines while audio plays. If not, the script will prompt you to play `song_lyrics.mp3` manually.

---

## Troubleshooting

- Import / Pylance errors in VS Code:
  - Ensure VS Code uses the project venv: Ctrl+Shift+P → "Python: Select Interpreter" → `.venv\Scripts\python.exe`.
  - Reload window after installation.

- playsound fails to install or build (common on newer Python):
  - Do not rely on playsound. The code prefers python-vlc. Install VLC and python-vlc instead.

- pipwin/js2py errors while installing PyAudio:
  - pipwin can fail on some systems. Prefer using sounddevice (already in this repo) for microphone input or install a matching PyAudio wheel manually from reliable sources.

- Pydub warns "Couldn't find ffprobe":
  - Install FFmpeg and ensure `ffmpeg`/`ffprobe` are on PATH. Restart terminal.

- No audio heard:
  - Verify `song_lyrics.mp3` was created.
  - Try manual playback: `start song_lyrics.mp3` (PowerShell) or double-click the file.
  - Test VLC playback in Python:
    ```powershell
    python - <<'PY'
    import vlc, time
    p = vlc.MediaPlayer("song_lyrics.mp3")
    p.play()
    time.sleep(2)
    p.stop()
    print("playback test done")
    PY
    ```

---

## .gitignore

Include a `.gitignore` in the project root to exclude venv, generated audio, and editor folders. Example entries:
- `.venv/`
- `*.mp3` (if you don't want to track generated audio)
- `.vscode/`, `__pycache__/`

---

## Notes

- This project demonstrates TTS + simple synchronization heuristics (line-based average timing). It is not a precision karaoke synchronizer.
- If you want precise alignment, provide timestamps or use real audio analyzers and proper timing metadata.

---

## License

Add a license of your choice (e.g., MIT) by creating a `LICENSE` file.
