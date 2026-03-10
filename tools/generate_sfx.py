#!/usr/bin/env python3
"""Generate match-3 game sound effects as .wav files."""

import numpy as np
import struct
import wave
import subprocess
import os

SAMPLE_RATE = 44100
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "sfx")


def write_wav(filename: str, samples: np.ndarray):
    """Write float samples [-1, 1] to 16-bit mono .wav."""
    path = os.path.join(OUTPUT_DIR, filename)
    int_samples = np.clip(samples * 32767, -32768, 32767).astype(np.int16)
    with wave.open(path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(int_samples.tobytes())
    return path


def convert_to_ogg(wav_path: str):
    """Convert .wav to .ogg via ffmpeg, then remove the .wav."""
    ogg_path = wav_path.replace(".wav", ".ogg")
    subprocess.run(
        ["ffmpeg", "-y", "-i", wav_path, "-c:a", "libvorbis", "-q:a", "4", ogg_path],
        capture_output=True,
        check=True,
    )
    os.remove(wav_path)
    print(f"  -> {os.path.basename(ogg_path)}")


def envelope(length: int, attack: float = 0.01, release: float = 0.05) -> np.ndarray:
    """Simple attack-release envelope."""
    env = np.ones(length)
    attack_samples = int(attack * SAMPLE_RATE)
    release_samples = int(release * SAMPLE_RATE)
    if attack_samples > 0:
        env[:attack_samples] = np.linspace(0, 1, attack_samples)
    if release_samples > 0:
        env[-release_samples:] = np.linspace(1, 0, release_samples)
    return env


def sine(freq: float, duration: float) -> np.ndarray:
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    return np.sin(2 * np.pi * freq * t)


def noise(duration: float) -> np.ndarray:
    return np.random.uniform(-1, 1, int(SAMPLE_RATE * duration))


# --- Sound effect generators ---


def gen_swap():
    """Quick two-tone whoosh: ascending slide."""
    duration = 0.15
    n = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    # Frequency sweep from 300 to 900 Hz
    freq = np.linspace(300, 900, n)
    signal = np.sin(2 * np.pi * np.cumsum(freq) / SAMPLE_RATE)
    signal *= envelope(n, attack=0.005, release=0.04)
    return signal * 0.6


def gen_match():
    """Bright sparkle: stacked harmonics with fast decay."""
    duration = 0.3
    n = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    # Major chord arpeggio feel
    freqs = [523.25, 659.25, 783.99]  # C5, E5, G5
    signal = np.zeros(n)
    for i, f in enumerate(freqs):
        delay = int(i * 0.03 * SAMPLE_RATE)
        tone_len = n - delay
        tone = np.sin(2 * np.pi * f * np.linspace(0, tone_len / SAMPLE_RATE, tone_len, endpoint=False))
        env = envelope(tone_len, attack=0.005, release=0.12)
        padded = np.concatenate([np.zeros(delay), tone * env])[:n]
        signal += padded
    signal /= len(freqs)
    signal *= envelope(n, attack=0.005, release=0.1)
    return signal * 0.7


def gen_no_match():
    """Dull buzz: descending tone with slight distortion."""
    duration = 0.25
    n = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    # Descending frequency
    freq = np.linspace(400, 200, n)
    signal = np.sin(2 * np.pi * np.cumsum(freq) / SAMPLE_RATE)
    # Add second detuned tone for "sad" feel
    freq2 = np.linspace(380, 180, n)
    signal2 = np.sin(2 * np.pi * np.cumsum(freq2) / SAMPLE_RATE)
    combined = (signal + signal2 * 0.5) / 1.5
    combined *= envelope(n, attack=0.01, release=0.1)
    return combined * 0.5


def gen_cascade():
    """Rising sparkle cascade: rapid ascending notes."""
    notes = [523.25, 659.25, 783.99, 1046.50]  # C5, E5, G5, C6
    note_dur = 0.07
    gap = 0.05
    total = note_dur * len(notes) + gap * (len(notes) - 1)
    # Recalculate with overlap
    total = 0.35
    n = int(SAMPLE_RATE * total)
    signal = np.zeros(n)
    for i, f in enumerate(notes):
        start = int(i * 0.07 * SAMPLE_RATE)
        tone_n = int(note_dur * SAMPLE_RATE)
        if start + tone_n > n:
            tone_n = n - start
        t_tone = np.linspace(0, tone_n / SAMPLE_RATE, tone_n, endpoint=False)
        tone = np.sin(2 * np.pi * f * t_tone)
        # Add shimmer harmonic
        tone += 0.3 * np.sin(2 * np.pi * f * 2 * t_tone)
        tone *= envelope(tone_n, attack=0.003, release=0.03)
        signal[start : start + tone_n] += tone
    signal = np.clip(signal, -1, 1)
    signal *= envelope(n, attack=0.005, release=0.05)
    return signal * 0.65


def gen_refill():
    """Soft bubbling: randomized short pops."""
    duration = 0.3
    n = int(SAMPLE_RATE * duration)
    signal = np.zeros(n)
    num_pops = 6
    for i in range(num_pops):
        start = int((i / num_pops) * n * 0.8)
        pop_dur = 0.03
        pop_n = int(SAMPLE_RATE * pop_dur)
        if start + pop_n > n:
            pop_n = n - start
        freq = 600 + i * 80  # Rising pitch
        t_pop = np.linspace(0, pop_n / SAMPLE_RATE, pop_n, endpoint=False)
        pop = np.sin(2 * np.pi * freq * t_pop)
        pop *= envelope(pop_n, attack=0.002, release=0.015)
        signal[start : start + pop_n] += pop
    # Gentle noise layer
    noise_layer = noise(duration) * 0.05 * envelope(n, attack=0.01, release=0.15)
    signal += noise_layer
    signal = np.clip(signal, -1, 1)
    return signal * 0.5


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    generators = {
        "swap.wav": gen_swap,
        "match.wav": gen_match,
        "no_match.wav": gen_no_match,
        "cascade.wav": gen_cascade,
        "refill.wav": gen_refill,
    }

    for filename, gen_fn in generators.items():
        print(f"Generating {filename}...")
        samples = gen_fn()
        wav_path = write_wav(filename, samples)
        convert_to_ogg(wav_path)

    print("\nDone! All .ogg files in assets/sfx/")


if __name__ == "__main__":
    main()
