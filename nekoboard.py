import threading
import sys
from gui import NekoBoardGUI
from hotkeys import HotkeyListener
from audio import AudioEngine
from sound_manager import SoundManager

class NekoBoard:
    def __init__(self):
        self.sound_manager = SoundManager()
        self.audio_engine = None
        self.hotkey_listener = None
        self.gui = None
        
    def init_audio(self):
        """Initialize audio engine (must be called after GUI shows status)"""
        self.audio_engine = AudioEngine(self.sound_manager)
        if not self.audio_engine.init():
            print("Failed to initialize audio")
            return False
        return True
    
    def start_hotkey_listener(self):
        """Start background hotkey listener"""
        self.hotkey_listener = HotkeyListener(self.sound_manager, self.gui)
        self.hotkey_listener.start()
    
    def run(self):
        """Main entry point"""
        # Create GUI first
        self.gui = NekoBoardGUI(self)
        
        # Initialize audio (may show errors in GUI)
        if not self.init_audio():
            self.gui.show_error("VB-Cable not found.\nInstall from vb-audio.com/Cable/")
        else:
            # Start hotkey listener only if audio works
            self.start_hotkey_listener()
        
        # Start GUI main loop
        self.gui.run()
        
    def shutdown(self):
        """Clean shutdown"""
        if self.hotkey_listener:
            self.hotkey_listener.stop()
        if self.audio_engine:
            self.audio_engine.close()

if __name__ == "__main__":
    app = NekoBoard()
    try:
        app.run()
    except KeyboardInterrupt:
        app.shutdown()
        sys.exit(0)