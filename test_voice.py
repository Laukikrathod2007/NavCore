"""Test voice pipeline with a real short audio file.
Generates a synthetic WAV (silence + known pattern) to measure latency.
"""
import wave, struct, math, time, os, urllib.request, json, tempfile

# Generate a 2-second 16kHz WAV containing a simple 440Hz sine tone
# (not real speech, but enough to test the pipeline end-to-end)
SAMPLE_RATE = 16000
DURATION = 2
wav_path = tempfile.mktemp(suffix=".wav")

with wave.open(wav_path, "w") as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(SAMPLE_RATE)
    for i in range(SAMPLE_RATE * DURATION):
        # 440Hz sine — Whisper will likely return silence/hallucination
        # but this tests the full pipeline timing
        val = int(32767 * 0.3 * math.sin(2 * math.pi * 440 * i / SAMPLE_RATE))
        wf.writeframes(struct.pack("<h", val))

print(f"Test WAV created: {wav_path} ({os.path.getsize(wav_path)} bytes)")

# POST to /query/audio
import urllib.request, urllib.parse
boundary = "NavCoreBoundary"
with open(wav_path, "rb") as f:
    audio_data = f.read()

body = (
    f"--{boundary}\r\n"
    f'Content-Disposition: form-data; name="file"; filename="test.wav"\r\n'
    f"Content-Type: audio/wav\r\n\r\n"
).encode() + audio_data + f"\r\n--{boundary}--\r\n".encode()

req = urllib.request.Request(
    "http://localhost:8001/query/audio",
    data=body,
    headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    method="POST",
)

t0 = time.time()
try:
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.loads(r.read())
    elapsed = time.time() - t0
    print(f"\nTotal latency: {elapsed:.1f}s")
    print(f"API reported:  {data.get('latency_ms', 0):.0f}ms")
    print(f"Transcribed:   '{data.get('transcribed_text', 'N/A')}'")
    print(f"Destination:   {data.get('destination', 'N/A')}")
    print(f"Directions:    {data.get('directions', 'N/A')[:80]}")
except Exception as e:
    print(f"Error: {e}")

os.unlink(wav_path)
