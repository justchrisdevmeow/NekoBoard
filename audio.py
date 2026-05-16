import pyaudio
import numpy as np
import threading
import queue
import time

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

class AudioEngine:
    def __init__(self, sound_manager):
        self.sound_manager = sound_manager
        self.p = None
        self.mic_stream = None
        self.output_stream = None
        self.vb_cable_index = None
        self.mic_index = None
        self.sound_queue = queue.Queue()
        self.running = False
        self.audio_thread = None
        
    def init(self):
        """Initialize PyAudio and find devices"""
        try:
            self.p = pyaudio.PyAudio()
        except Exception as e:
            print(f"Failed to init PyAudio: {e}")
            return False
        
        # Find VB-Cable output device (where we send mixed audio)
        for i in range(self.p.get_device_count()):
            info = self.p.get_device_info_by_index(i)
            name = info['name'].lower()
            if any(keyword in name for keyword in ['cable', 'vb-audio', 'virtual']):
                if info['maxInputChannels'] > 0:  # Input side of VB-Cable
                    self.vb_cable_index = i
                    print(f"Found VB-Cable input: {info['name']} (index {i})")
                    break
        
        if self.vb_cable_index is None:
            print("VB-Cable not found")
            return False
        
        # Find physical microphone
        for i in range(self.p.get_device_count()):
            info = self.p.get_device_info_by_index(i)
            name = info['name'].lower()
            if 'mic' in name or 'microphone' in name:
                if info['maxInputChannels'] > 0:
                    self.mic_index = i
                    print(f"Found microphone: {info['name']} (index {i})")
                    break
        
        if self.mic_index is None:
            print("Warning: Microphone not auto-detected. Using default input device.")
            self.mic_index = self.p.get_default_input_device_info()['index']
        
        # Start audio streams
        try:
            self.mic_stream = self.p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                input_device_index=self.mic_index,
                frames_per_buffer=CHUNK
            )
            
            self.output_stream = self.p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                output=True,
                output_device_index=self.vb_cable_index,
                frames_per_buffer=CHUNK
            )
        except Exception as e:
            print(f"Failed to open audio streams: {e}")
            return False
        
        self.running = True
        self.audio_thread = threading.Thread(target=self._audio_loop, daemon=True)
        self.audio_thread.start()
        print("Audio engine initialized")
        return True
    
    def queue_sound(self, hotkey):
        """Queue a sound to be played (called from hotkey thread)"""
        sound = self.sound_manager.get_sound(hotkey)
        if sound:
            self.sound_queue.put(sound)
    
    def _audio_loop(self):
        """Main audio processing loop: read mic, mix with queued sounds, output to VB-Cable"""
        while self.running:
            try:
                # Read mic data
                mic_data = self.mic_stream.read(CHUNK, exception_on_overflow=False)
                mic_array = np.frombuffer(mic_data, dtype=np.int16).astype(np.float32) / 32768.0
                
                # Process any queued sounds
                mixed = mic_array.copy()
                
                # Process all pending sounds (play them simultaneously)
                sounds_to_play = []
                while not self.sound_queue.empty():
                    try:
                        sounds_to_play.append(self.sound_queue.get_nowait())
                    except queue.Empty:
                        break
                
                for sound_data in sounds_to_play:
                    # Convert sound bytes to numpy array
                    sound_array = np.frombuffer(sound_data['data'], dtype=np.int16).astype(np.float32) / 32768.0
                    
                    # If sound is longer than CHUNK, we need to stream it
                    # For simplicity, we'll mix the first CHUNK of the sound
                    if len(sound_array) >= CHUNK:
                        sound_chunk = sound_array[:CHUNK]
                    else:
                        # Pad with zeros if sound is shorter than CHUNK
                        sound_chunk = np.pad(sound_array, (0, CHUNK - len(sound_array)), 'constant')
                    
                    # Mix (with gain to prevent clipping)
                    mixed = mixed + sound_chunk * 0.8
                
                # Clip to valid range
                mixed = np.clip(mixed, -1.0, 1.0)
                
                # Convert back to int16
                output_data = (mixed * 32767).astype(np.int16).tobytes()
                
                # Write to output (VB-Cable)
                self.output_stream.write(output_data)
                
            except Exception as e:
                print(f"Audio loop error: {e}")
                time.sleep(0.001)
    
    def close(self):
        """Clean shutdown"""
        self.running = False
        if self.audio_thread:
            self.audio_thread.join(timeout=1.0)
        if self.mic_stream:
            self.mic_stream.stop_stream()
            self.mic_stream.close()
        if self.output_stream:
            self.output_stream.stop_stream()
            self.output_stream.close()
        if self.p:
            self.p.terminate()
        print("Audio engine closed")
