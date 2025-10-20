"""
Sound Effects System

Generates synthesized sound effects for SpaceCMD using pygame and numpy.
All sounds are procedurally generated - no audio files needed!
"""

import pygame
import numpy as np
import random


class SoundManager:
    """
    Manages all game sound effects.

    Generates procedural sounds:
    - Laser fire
    - Explosions
    - Shield hits
    - System damage alerts
    - UI clicks
    - Engine hum
    """

    def __init__(self, sample_rate=22050):
        """Initialize sound manager"""
        pygame.mixer.init(frequency=sample_rate, size=-16, channels=2, buffer=512)
        self.sample_rate = sample_rate
        self.sounds = {}
        self.enabled = True

        # Generate all sounds
        self._generate_sounds()

    def _generate_sounds(self):
        """Generate all sound effects"""
        print("Generating sound effects...")

        # Weapon sounds
        self.sounds["laser_fire"] = self._generate_laser()
        self.sounds["missile_fire"] = self._generate_missile()
        self.sounds["beam_fire"] = self._generate_beam()

        # Impact sounds
        self.sounds["explosion"] = self._generate_explosion()
        self.sounds["shield_hit"] = self._generate_shield_hit()
        self.sounds["hull_hit"] = self._generate_hull_hit()

        # System sounds
        self.sounds["system_damage"] = self._generate_system_damage()
        self.sounds["system_destroyed"] = self._generate_system_destroyed()
        self.sounds["alarm"] = self._generate_alarm()

        # UI sounds
        self.sounds["click"] = self._generate_click()
        self.sounds["select"] = self._generate_select()
        self.sounds["error"] = self._generate_error()

        # Ambient
        self.sounds["engine_hum"] = self._generate_engine_hum()

        print(f"✓ Generated {len(self.sounds)} sound effects")

    def _make_sound(self, samples):
        """Convert numpy array to pygame Sound"""
        # Ensure samples are in correct range
        samples = np.clip(samples, -1.0, 1.0)

        # Convert to 16-bit integers
        samples = (samples * 32767).astype(np.int16)

        # Create stereo by duplicating mono
        if samples.ndim == 1:
            samples = np.column_stack((samples, samples))

        # Create pygame sound
        sound = pygame.sndarray.make_sound(samples)
        return sound

    def _generate_laser(self):
        """Generate laser fire sound - pew pew!"""
        duration = 0.15  # 150ms
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples)

        # Sweep from high to low frequency
        freq_start = 1200
        freq_end = 400
        freq = freq_start + (freq_end - freq_start) * t / duration

        # Generate swept sine wave
        phase = 2 * np.pi * freq * t
        wave = np.sin(np.cumsum(phase) * duration / samples)

        # Apply envelope (quick attack, fast decay)
        envelope = np.exp(-t * 15)

        return self._make_sound(wave * envelope * 0.3)

    def _generate_missile(self):
        """Generate missile launch sound - whoosh!"""
        duration = 0.3
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples)

        # Low rumble that fades
        rumble = np.sin(2 * np.pi * 80 * t) * 0.5
        rumble += np.sin(2 * np.pi * 120 * t) * 0.3

        # High frequency whoosh
        whoosh_freq = 2000 + 1000 * t / duration
        whoosh = np.sin(2 * np.pi * whoosh_freq * t) * 0.2

        # Combine
        wave = rumble + whoosh

        # Envelope
        envelope = np.exp(-t * 5)

        return self._make_sound(wave * envelope * 0.4)

    def _generate_beam(self):
        """Generate beam weapon sound - continuous zap"""
        duration = 0.5
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples)

        # Multi-frequency beam
        wave = (np.sin(2 * np.pi * 200 * t) * 0.3 +
                np.sin(2 * np.pi * 400 * t) * 0.2 +
                np.sin(2 * np.pi * 600 * t) * 0.1)

        # Add some noise
        wave += np.random.randn(samples) * 0.05

        # Sustain envelope
        attack_len = int(samples * 0.1)
        release_len = int(samples * 0.2)
        sustain_len = samples - attack_len - release_len

        attack = np.linspace(0, 1, attack_len)
        sustain = np.ones(sustain_len)
        release = np.linspace(1, 0, release_len)
        envelope = np.concatenate([attack, sustain, release])

        return self._make_sound(wave * envelope * 0.3)

    def _generate_explosion(self):
        """Generate explosion sound - BOOM!"""
        duration = 0.8
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples)

        # White noise base
        noise = np.random.randn(samples)

        # Low frequency rumble
        rumble = np.sin(2 * np.pi * 60 * t) * 2.0
        rumble += np.sin(2 * np.pi * 40 * t) * 1.5

        # Combine
        wave = noise * 0.5 + rumble

        # Sharp attack, long decay
        attack = np.linspace(0, 1, int(samples * 0.05))
        decay = np.exp(-t[int(samples * 0.05):] * 3)
        envelope = np.concatenate([attack, decay])

        return self._make_sound(wave * envelope * 0.5)

    def _generate_shield_hit(self):
        """Generate shield hit sound - electric zap"""
        duration = 0.2
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples)

        # High frequency electric zap
        wave = np.sin(2 * np.pi * 1500 * t)
        wave += np.sin(2 * np.pi * 3000 * t) * 0.5

        # Add some noise for crackle
        wave += np.random.randn(samples) * 0.3

        # Quick envelope
        envelope = np.exp(-t * 20)

        return self._make_sound(wave * envelope * 0.4)

    def _generate_hull_hit(self):
        """Generate hull impact sound - metallic clang"""
        duration = 0.3
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples)

        # Metallic frequencies
        wave = (np.sin(2 * np.pi * 800 * t) +
                np.sin(2 * np.pi * 1200 * t) * 0.7 +
                np.sin(2 * np.pi * 400 * t) * 0.5)

        # Add noise for impact
        wave += np.random.randn(samples) * 0.4

        # Sharp envelope
        envelope = np.exp(-t * 12)

        return self._make_sound(wave * envelope * 0.5)

    def _generate_system_damage(self):
        """Generate system damage alert - warning beep"""
        duration = 0.15
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples)

        # Alert tone - two frequencies
        wave = np.sin(2 * np.pi * 800 * t) + np.sin(2 * np.pi * 1000 * t)

        # Envelope
        envelope = np.exp(-t * 15)

        return self._make_sound(wave * envelope * 0.3)

    def _generate_system_destroyed(self):
        """Generate system destroyed sound - alarm"""
        duration = 0.4
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples)

        # Descending alarm
        freq = 1200 - 600 * t / duration
        wave = np.sin(2 * np.pi * freq * t)

        # Add distortion
        wave = np.tanh(wave * 2)

        # Envelope
        envelope = np.exp(-t * 5)

        return self._make_sound(wave * envelope * 0.4)

    def _generate_alarm(self):
        """Generate alarm sound - repeating beep"""
        duration = 1.0
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples)

        # Square wave alarm
        wave = np.sign(np.sin(2 * np.pi * 800 * t))

        # Pulse envelope (on/off pattern)
        pulse = (np.sin(2 * np.pi * 4 * t) > 0).astype(float)

        return self._make_sound(wave * pulse * 0.2)

    def _generate_click(self):
        """Generate UI click sound"""
        duration = 0.05
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples)

        # Short click
        wave = np.sin(2 * np.pi * 1200 * t)

        # Very sharp envelope
        envelope = np.exp(-t * 50)

        return self._make_sound(wave * envelope * 0.2)

    def _generate_select(self):
        """Generate UI select sound"""
        duration = 0.1
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples)

        # Rising tone
        freq = 800 + 400 * t / duration
        wave = np.sin(2 * np.pi * freq * t)

        # Envelope
        envelope = np.exp(-t * 20)

        return self._make_sound(wave * envelope * 0.25)

    def _generate_error(self):
        """Generate error sound"""
        duration = 0.2
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples)

        # Harsh buzz
        wave = np.sign(np.sin(2 * np.pi * 200 * t)) * 0.5
        wave += np.sin(2 * np.pi * 100 * t) * 0.3

        # Envelope
        envelope = np.exp(-t * 10)

        return self._make_sound(wave * envelope * 0.3)

    def _generate_engine_hum(self):
        """Generate engine ambient sound"""
        duration = 2.0  # Loopable
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples)

        # Low rumble
        wave = np.sin(2 * np.pi * 60 * t) * 0.3
        wave += np.sin(2 * np.pi * 90 * t) * 0.2
        wave += np.sin(2 * np.pi * 120 * t) * 0.1

        # Add subtle variation
        wave += np.random.randn(samples) * 0.02

        return self._make_sound(wave * 0.15)

    def play(self, sound_name, volume=1.0):
        """
        Play a sound effect.

        Args:
            sound_name: Name of sound to play
            volume: Volume (0.0 to 1.0)
        """
        if not self.enabled:
            return

        if sound_name in self.sounds:
            sound = self.sounds[sound_name]
            sound.set_volume(volume)
            sound.play()

    def stop_all(self):
        """Stop all playing sounds"""
        pygame.mixer.stop()

    def set_enabled(self, enabled):
        """Enable/disable sound effects"""
        self.enabled = enabled
        if not enabled:
            self.stop_all()


# Global sound manager instance
_sound_manager = None


def get_sound_manager():
    """Get global sound manager instance"""
    global _sound_manager
    if _sound_manager is None:
        _sound_manager = SoundManager()
    return _sound_manager


def play_sound(sound_name, volume=1.0):
    """Convenience function to play a sound"""
    get_sound_manager().play(sound_name, volume)
