# NekoBoard - Virtual Soundboard with Mic Mixing

Play sounds through your mic while talking. Works with Discord, Zoom, games, etc.

## Requirements

- Windows 10/11
- VB-Cable (download from https://vb-audio.com/Cable/)
- Python 3.8+ with pip

## Installation

1. Install VB-Cable (required for virtual mic output)
2. Install Python packages:
   ```
   pip install pyaudio numpy keyboard
   ```
   (tkinter is built-in to Python)

3. Run NekoBoard:
   ```
   python nekoboard.py
   ```

## Usage

1. Set VB-Cable as your default microphone in Windows
2. In NekoBoard, click "Add Sound" and select a .wav file
3. Press a key to assign as hotkey
4. Press that key to play the sound
5. Your microphone is automatically mixed with sounds

## Troubleshooting

- **No sound?** Make sure VB-Cable is installed and selected as your default microphone
- **VB-Cable not detected?** Run as administrator or reinstall VB-Cable
- **PyAudio error?** Install from https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

## Files

- `nekoboard.py` - Main entry
- `gui.py` - Interface
- `audio.py` - Audio processing
- `sound_manager.py` - Sound storage
- `hotkeys.py` - Keyboard listener
- `config.json` - Saved sound assignments


---

**To run NekoBoard:**

```
pip install pyaudio numpy keyboard
python nekoboard.py
```
or download NekoBoard.exe from releases.
