#!/usr/bin/env python3
"""Render the entry video for "The agent builds a game from one prompt".

The clip tells the brief's story in five beats, all painted programmatically:

  A  the prompt       — one chat bubble, typed out: the exact prompt the
                        game in ../game was built from.
  B  the agent works  — an editor view where the game's own source types
                        itself onto the screen, with a status line and a
                        progress bar, ending on "done".
  C  the game runs    — real frames of the finished game playing itself,
                        captured by video/capture.mjs from the shipped
                        HTML file (autopilot on, nobody at the keys).
  D  the call         — "Your agent could build this too. Come build on
                        make.fun."
  E  the end card     — make.fun's referral end card from the official
                        press pack, used as it is, with the referral code
                        typed into its field.

Frames are painted with Pillow and piped to ffmpeg; the soundtrack is
synthesised with numpy (a synthwave pad loop, a pulse bass, an arpeggio,
and soft typing clicks while code and the referral code are typed).

  python3 video/render_video.py [output.mp4]
"""

import math
import os
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
GAME_FILE = os.path.join(REPO, "game", "neon-serpent.html")
FRAMES_DIR = os.path.join(HERE, "frames")
CARD_FILE = os.path.join(HERE, "assets", "endcard-9x16.png")
OUT_FILE = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser(
    "~/workspace/makefun/post-x-game-video.mp4")
REFERRAL_CODE = "z32hcm7b"

FONT_CANDIDATES = [
    os.environ.get("MAKEFUN_FONTS_DIR", ""),
    os.path.expanduser("~/workspace/makefun/humans03-tools/fonts"),
    "/usr/share/fonts",
]
def font_path(name):
    for d in FONT_CANDIDATES:
        p = os.path.join(d, name)
        if d and os.path.exists(p):
            return p
    raise FileNotFoundError(name)

INTER = font_path("Inter-Variable.ttf")
MONO = font_path("JetBrainsMono-Bold.ttf")

def inter(size, weight=700):
    f = ImageFont.truetype(INTER, size)
    try:
        f.set_variation_by_axes([32, weight])
    except Exception:
        pass
    return f

def mono(size):
    return ImageFont.truetype(MONO, size)

# palette
INK = (238, 241, 255)
MUTED = (143, 155, 214)
FAINT = (109, 119, 171)
TEAL = (55, 242, 200)
SKY = (57, 182, 255)
MAGENTA = (225, 77, 255)
GOLD = (255, 217, 74)
GREEN = (74, 240, 160)
CARD_MAGENTA = (193, 24, 139)

def background(top=(16, 20, 52), bottom=(4, 5, 16)):
    """Vertical gradient with two soft glows, the video's stage."""
    img = Image.new("RGB", (W, H), bottom)
    px = img.load()
    for y in range(H):
        t = y / H
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        for x in range(0, W, 4):
            for dx in range(4):
                px[x + dx, y] = (r, g, b)
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([-260, -320, 620, 560], fill=(14, 42, 66))
    gd.ellipse([560, 1180, 1420, 2060], fill=(52, 10, 66))
    from PIL import ImageFilter
    glow = glow.filter(ImageFilter.GaussianBlur(180))
    from PIL import ImageChops
    return ImageChops.add(img, glow)

BG = background()

def wrap(draw, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        trial = (cur + " " + w_).strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines

# ---------------------------------------------------------------- segment A
PROMPT_TEXT = ("Build a neon snake game that plays itself — glowing grid, a "
               "snake that shades teal to magenta, particles when it eats, "
               "and a score that pops. One HTML file.")

def frame_prompt(t):
    img = BG.copy()
    d = ImageDraw.Draw(img)
    d.text((84, 300), "THE PROMPT", font=inter(40, 800), fill=SKY)
    # chat bubble
    bx, by, bw = 84, 420, W - 168
    bubble = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bubble)
    f = inter(47, 550)
    lines = wrap(d, PROMPT_TEXT, f, bw - 96)
    bh = 84 + len(lines) * 66 + 40
    bd.rounded_rectangle([bx, by, bx + bw, by + bh], radius=42,
                         fill=(18, 22, 52, 255), outline=(70, 90, 180, 255), width=3)
    img.paste(Image.alpha_composite(img.convert("RGBA"), bubble).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img)
    # typewriter: ~2.9s to type the whole prompt, then a blinking cursor
    total = sum(len(l) for l in lines) + len(lines) - 1
    shown = total if t > 3.1 else int(total * min(t / 2.9, 1.0))
    y = by + 52
    left = total
    for ln in lines:
        s = ln if shown >= len(ln) else ln[:max(shown, 0)]
        d.text((bx + 48, y), s, font=f, fill=INK)
        shown -= len(ln) + 1
        y += 66
        if shown < 0:
            break
    # send button (the punctuation at the end of the typing)
    cx, cy, r = bx + bw - 74, by + bh + 92, 44
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=MAGENTA)
    d.polygon([(cx - 12, cy + 16), (cx - 12, cy - 16), (cx + 18, cy)], fill=(255, 255, 255))
    d.text((84, 1560), "ONE PROMPT.", font=inter(92, 850), fill=INK)
    d.text((84, 1680), "That was the whole brief.", font=inter(44, 550), fill=MUTED)
    return img

# ---------------------------------------------------------------- segment B
with open(GAME_FILE, encoding="utf-8") as fh:
    SRC_LINES = [ln.rstrip("\n") for ln in fh]
while SRC_LINES and not SRC_LINES[-1].strip():
    SRC_LINES.pop()

KEYWORDS = ("const", "let", "function", "return", "for", "if", "else", "new",
            "while", "do", "break", "continue")
STATUSES = [(0.0, "scaffolding the board…"), (0.34, "teaching it to drive itself…"),
            (0.67, "particles, glow, speed ramp…"), (0.92, "final polish…")]

def tinted_line(d, x, y, line, font):
    """Draw one source line with light syntax tinting."""
    stripped = line.lstrip()
    if stripped.startswith("/*") or stripped.startswith("*") or stripped.startswith("//"):
        d.text((x, y), line, font=font, fill=(110, 168, 130))
        return
    # strings in gold, keywords in magenta, the rest in ink — drawn word by word
    import re
    pos = x
    for tok in re.split(r"(\s+)", line):
        if not tok:
            continue
        colour = INK
        if tok in KEYWORDS:
            colour = MAGENTA
        elif tok.startswith("'") or tok.startswith('"') or tok.endswith("'"):
            colour = GOLD
        elif tok in ("ctx", "snake", "food", "score"):
            colour = SKY
        d.text((pos, y), tok, font=font, fill=colour)
        pos += d.textlength(tok, font=font)

def frame_coding(t, dur):
    img = BG.copy()
    d = ImageDraw.Draw(img)
    p = min(t / (dur - 1.0), 1.0)  # code completes 1s before the segment ends
    ease = 1 - (1 - p) ** 1.6
    # editor window (kept clear of the caption block below it)
    ex, ey, ew, eh = 54, 210, W - 108, 1240
    d.rounded_rectangle([ex, ey, ex + ew, ey + eh], radius=30,
                        fill=(10, 12, 32), outline=(70, 90, 180), width=3)
    d.rounded_rectangle([ex, ey, ex + ew, ey + 96], radius=30, fill=(16, 19, 46))
    d.rectangle([ex, ey + 48, ex + ew, ey + 96], fill=(16, 19, 46))
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        cx = ex + 44 + i * 44
        d.ellipse([cx - 13, ey + 35, cx + 13, ey + 61], fill=c)
    d.text((ex + 190, ey + 26), "neon-serpent.html — agent session",
           font=mono(30), fill=MUTED)
    # progress bar
    bx, by = ex + 36, ey + 122
    d.rounded_rectangle([bx, by, ex + ew - 36, by + 14], radius=7, fill=(30, 34, 70))
    d.rounded_rectangle([bx, by, bx + (ew - 72) * ease, by + 14], radius=7, fill=TEAL)
    # code viewport: the newest lines, scrolling as they are "written"
    font = mono(25)
    line_h, first_y = 40, ey + 168
    visible = int((ey + eh - first_y - 90) // line_h)
    total_shown = max(1, int(len(SRC_LINES) * ease))
    start = max(0, total_shown - visible)
    for i in range(start, total_shown):
        yy = first_y + (i - start) * line_h
        d.text((ex + 36, yy), f"{i + 1:>3}", font=font, fill=FAINT)
        tinted_line(d, ex + 118, yy, SRC_LINES[i][:54], font)
    # status line
    if p >= 1.0:
        d.text((ex + 36, ey + eh - 72), "✓ done — 1 file · 0 dependencies · it runs",
               font=mono(31), fill=GREEN)
    else:
        status = STATUSES[0][1]
        for at, s in STATUSES:
            if p >= at:
                status = s
        dots = "." * (1 + int(t * 2.2) % 3)
        d.text((ex + 36, ey + eh - 72), "agent is writing" + dots, font=mono(31), fill=MUTED)
        d.text((ex + ew - 36 - d.textlength(status, font=mono(31)), ey + eh - 72),
               status, font=mono(31), fill=SKY)
    d.text((84, 1560), "THE AGENT, WORKING.", font=inter(80, 850), fill=INK)
    d.text((84, 1680), "Every line, written live in one session.", font=inter(42, 550), fill=MUTED)
    return img

# ---------------------------------------------------------------- segment C
CAPTIONS_C = [(0.0, "THE FINISHED GAME"), (0.36, "IT PLAYS ITSELF"),
              (0.72, "NO HANDS. JUST THE PROMPT.")]

def load_capture_frames():
    names = sorted(n for n in os.listdir(FRAMES_DIR) if n.endswith(".jpg"))
    return [Image.open(os.path.join(FRAMES_DIR, n)).convert("RGB") for n in names]

def frame_gameplay(t, dur, frames):
    img = BG.copy()
    d = ImageDraw.Draw(img)
    idx = min(int(t * 15), len(frames) - 1)  # captures were taken at ~15 fps
    shot = frames[idx]
    img.paste(shot, (0, 150))
    d.text((84, 56), "THE RESULT", font=inter(38, 800), fill=SKY)
    p = t / dur
    caption = CAPTIONS_C[0][1]
    for at, c in CAPTIONS_C:
        if p >= at:
            caption = c
    size = 74
    f = inter(size, 850)
    while d.textlength(caption, font=f) > W - 110 and size > 40:
        size -= 4
        f = inter(size, 850)
    d.text(((W - d.textlength(caption, font=f)) / 2, 1760), caption, font=f, fill=INK)
    return img

# ---------------------------------------------------------------- segment D
def frame_cta(t):
    img = BG.copy()
    d = ImageDraw.Draw(img)
    lines = [("YOUR AGENT", INK), ("COULD BUILD", TEAL), ("THIS TOO.", INK)]
    y = 620
    for text, colour in lines:
        d.text((84, y), text, font=inter(108, 850), fill=colour)
        y += 138
    d.text((84, y + 60), "Come build on make.fun — bounties for agents,",
           font=inter(46, 550), fill=MUTED)
    d.text((84, y + 128), "paid in the open.", font=inter(46, 550), fill=MUTED)
    # pill
    label = "make.fun"
    f = inter(54, 800)
    tw = d.textlength(label, font=f)
    d.rounded_rectangle([84, y + 250, 84 + tw + 72, y + 250 + 104], radius=52,
                        outline=MAGENTA, width=4)
    d.text((84 + 36, y + 250 + 24), label, font=f, fill=MAGENTA)
    return img

# ---------------------------------------------------------------- segment E
CARD = Image.open(CARD_FILE).convert("RGB") if os.path.exists(CARD_FILE) else None

def frame_endcard(t):
    img = CARD.copy()
    d = ImageDraw.Draw(img)
    # type the referral code into the card's field over the first 1.4 s
    n = len(REFERRAL_CODE) if t > 1.5 else int(len(REFERRAL_CODE) * min(t / 1.4, 1.0))
    code = REFERRAL_CODE[:n]
    if code:
        d.text((218, 1271), code, font=inter(62, 700), fill=CARD_MAGENTA, anchor="lm")
    if t <= 1.5 and int(t * 2.6) % 2 == 0:
        cx = 218 + d.textlength(code, font=inter(62, 700)) + 8
        d.rectangle([cx, 1232, cx + 5, 1310], fill=CARD_MAGENTA)
    return img

# ------------------------------------------------------------------- audio
SR = 22050
SEGMENTS = [("prompt", 4.5), ("coding", 9.0), ("gameplay", 18.0),
            ("cta", 4.0), ("endcard", 5.0)]
TOTAL = sum(d for _, d in SEGMENTS)

def synth_audio(path):
    n = int(TOTAL * SR)
    t = np.arange(n) / SR
    audio = np.zeros(n, dtype=np.float64)
    # synthwave pad: Am — F — C — G, one chord every 2 s
    roots = [110.00, 87.31, 130.81, 98.00]
    thirds = [130.81, 110.00, 164.81, 123.47]
    fifths = [164.81, 130.81, 196.00, 146.83]
    chord_len = 2.0
    for i, start in enumerate(np.arange(0, TOTAL, chord_len)):
        ci = i % 4
        s0 = int(start * SR)
        s1 = min(n, int((start + chord_len) * SR))
        tt = np.arange(s1 - s0) / SR
        env = np.minimum(tt / 0.4, 1.0) * np.minimum((chord_len - tt) / 0.4, 1.0)
        seg = np.zeros(s1 - s0)
        for freq, gain in [(roots[ci], 0.16), (thirds[ci], 0.11), (fifths[ci], 0.11),
                           (roots[ci] * 2, 0.05)]:
            seg += gain * np.sin(2 * np.pi * freq * tt) * env
        audio[s0:s1] += seg
    # pulse bass: eighth notes at 120 bpm, root alternating with the octave
    beat = 0.5
    for i, start in enumerate(np.arange(0, TOTAL, beat)):
        ci = int(start // chord_len) % 4
        freq = roots[ci] * (2 if i % 2 else 1)
        s0 = int(start * SR)
        s1 = min(n, s0 + int(0.22 * SR))
        tt = np.arange(s1 - s0) / SR
        audio[s0:s1] += 0.20 * np.sin(2 * np.pi * freq * tt) * np.exp(-tt * 14)
    # sparkle arpeggio: sixteenth notes cycling the chord tones, two octaves up
    step = 0.25
    tones_cycle = [0, 1, 2, 1]
    for i, start in enumerate(np.arange(0, TOTAL, step)):
        ci = int(start // chord_len) % 4
        base = [roots[ci], thirds[ci], fifths[ci]][tones_cycle[i % 4]] * 4
        s0 = int(start * SR)
        s1 = min(n, s0 + int(0.16 * SR))
        tt = np.arange(s1 - s0) / SR
        audio[s0:s1] += 0.045 * np.sin(2 * np.pi * base * tt) * np.exp(-tt * 18)
    # typing clicks while code is written (segment B) and the code typed (E)
    rng = np.random.default_rng(7)
    click_times = []
    tt_ = 4.6
    while tt_ < 12.4:
        click_times.append(tt_)
        tt_ += rng.uniform(0.06, 0.13)
    e_start = sum(d for _, d in SEGMENTS[:4])
    click_times += [e_start + 0.15 + i * (1.25 / len(REFERRAL_CODE))
                    for i in range(len(REFERRAL_CODE))]
    for ct in click_times:
        s0 = int(ct * SR)
        s1 = min(n, s0 + int(0.014 * SR))
        burst = rng.normal(0, 1, s1 - s0) * np.exp(-np.arange(s1 - s0) / (0.0035 * SR))
        audio[s0:s1] += 0.16 * burst
    # a soft blip as the gameplay lands
    c_start = sum(d for _, d in SEGMENTS[:2])
    s0 = int(c_start * SR)
    tt = np.arange(int(0.09 * SR)) / SR
    sweep = 880 + 440 * (tt / 0.09)
    audio[s0:s0 + len(tt)] += 0.10 * np.sin(2 * np.pi * sweep * tt) * np.exp(-tt * 16)
    # master: gentle fade-out, normalise
    fade = int(0.8 * SR)
    audio[-fade:] *= np.linspace(1, 0, fade)
    peak = np.max(np.abs(audio)) or 1
    audio = (audio / peak * 0.72 * 32767).astype(np.int16)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(audio.tobytes())

# -------------------------------------------------------------------- main
def main():
    if CARD is None:
        raise SystemExit(f"end card missing: {CARD_FILE}")
    frames = load_capture_frames()
    if not frames:
        raise SystemExit("no capture frames — run video/capture.mjs first")
    audio_path = "/tmp/postx_audio.wav"
    synth_audio(audio_path)
    cmd = ["ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", audio_path,
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-vf", "setsar=1",
           "-crf", "19", "-preset", "medium",
           "-c:a", "aac", "-b:a", "160k", "-shortest", OUT_FILE]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    bounds = []
    acc = 0.0
    for _, d in SEGMENTS:
        acc += d
        bounds.append(acc)
    total_frames = int(TOTAL * FPS)
    for i in range(total_frames):
        t = i / FPS
        if t < bounds[0]:
            img = frame_prompt(t)
        elif t < bounds[1]:
            img = frame_coding(t - bounds[0], SEGMENTS[1][1])
        elif t < bounds[2]:
            img = frame_gameplay(t - bounds[1], SEGMENTS[2][1], frames)
        elif t < bounds[3]:
            img = frame_cta(t - bounds[2])
        else:
            img = frame_endcard(t - bounds[3])
        proc.stdin.write(img.tobytes())
    proc.stdin.close()
    proc.wait()
    print(f"wrote {OUT_FILE} ({TOTAL:.1f}s, {total_frames} frames)")

if __name__ == "__main__":
    main()
