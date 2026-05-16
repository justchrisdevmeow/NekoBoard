import threading
import time
import keyboard

class HotkeyListener:
    def __init__(self, sound_manager, gui):
        self.sound_manager = sound_manager
        self.gui = gui
        self.running = False
        self.thread = None
        self.current_keys = set()  # Track currently pressed keys for edge detection
    
    def start(self):
        """Start the hotkey listener thread"""
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._listen, daemon=True)
        self.thread.start()
        print("Hotkey listener started")
    
    def stop(self):
        """Stop the hotkey listener"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        print("Hotkey listener stopped")
    
    def _listen(self):
        """Main listener loop - detects key presses and triggers sounds"""
        while self.running:
            # Get all currently pressed keys
            pressed = set(keyboard.get_hotkey_name())
            
            # Find newly pressed keys (keys in pressed but not in current_keys)
            new_keys = pressed - self.current_keys
            
            for key in new_keys:
                # Check if this key has a sound assigned
                sound = self.sound_manager.get_sound(key)
                if sound:
                    # Play sound (will be mixed by audio engine)
                    self._play_sound(key, sound)
            
            self.current_keys = pressed
            time.sleep(0.01)  # 10ms poll rate, low CPU
    
    def _play_sound(self, hotkey, sound):
        """Queue sound for playback (called from audio thread context)"""
        # The audio engine will pick this up in its mix loop
        # We need a thread-safe way to notify audio engine
        # For now, we'll set a flag that audio engine checks
        if hasattr(self, '_audio_engine'):
            self._audio_engine.queue_sound(hotkey)
