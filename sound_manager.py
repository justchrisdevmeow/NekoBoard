import wave
import numpy as np
import threading

class SoundManager:
    def __init__(self):
        self.sounds = {}  # hotkey -> {'data': bytes, 'params': tuple, 'file_path': str}
        self.lock = threading.Lock()
    
    def add_sound(self, hotkey, file_path):
        """Load a WAV file and store it for playback"""
        try:
            wf = wave.open(file_path, 'rb')
            data = wf.readframes(wf.getnframes())
            params = (wf.getnchannels(), wf.getsampwidth(), wf.getframerate(), wf.getnframes())
            wf.close()
            
            with self.lock:
                self.sounds[hotkey] = {
                    'data': data,
                    'params': params,
                    'file_path': file_path
                }
            return True
        except Exception as e:
            print(f"Error loading sound {file_path}: {e}")
            return False
    
    def remove_sound(self, hotkey):
        """Remove a sound by hotkey"""
        with self.lock:
            if hotkey in self.sounds:
                del self.sounds[hotkey]
                return True
        return False
    
    def change_hotkey(self, old_hotkey, new_hotkey):
        """Change hotkey for a sound"""
        with self.lock:
            if old_hotkey in self.sounds:
                self.sounds[new_hotkey] = self.sounds.pop(old_hotkey)
                return True
        return False
    
    def get_sound(self, hotkey):
        """Get sound data for a hotkey (returns None if not found)"""
        with self.lock:
            return self.sounds.get(hotkey, None)
    
    def get_all_hotkeys(self):
        """Return list of all hotkeys"""
        with self.lock:
            return list(self.sounds.keys())
