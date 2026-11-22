# The Agent Builds a Game — a video on X for make.fun

[![make.fun · post-x-the-agent-builds-a-game-from-20261122-1709](https://make.fun/badge/post-x-the-agent-builds-a-game-from-20261122-1709.svg)](https://make.fun/bounty/post-x-the-agent-builds-a-game-from-20261122-1709?utm_source=github&utm_medium=readme&utm_campaign=post-x-the-agent-builds-a-game-from-20261122-1709)
[![rank](https://make.fun/badge/post-x-the-agent-builds-a-game-from-20261122-1709/adzinsyariif/agent-builds-a-game/rank.svg)](https://make.fun/bounty/post-x-the-agent-builds-a-game-from-20261122-1709/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=post-x-the-agent-builds-a-game-from-20261122-1709)
[![reward](https://make.fun/badge/post-x-the-agent-builds-a-game-from-20261122-1709/adzinsyariif/agent-builds-a-game/reward.svg)](https://make.fun/bounty/post-x-the-agent-builds-a-game-from-20261122-1709?utm_source=github&utm_medium=readme&utm_campaign=post-x-the-agent-builds-a-game-from-20261122-1709)

One prompt in, one game out. This entry is a short vertical video for
[make.fun](https://make.fun/bounty/post-x-the-agent-builds-a-game-from-20261122-1709):
an AI agent is given a single prompt — *build a neon snake game that plays
itself* — writes the whole game live on screen, and the clip ends on the
finished game running itself, eating, scoring and speeding up. The video is
posted natively on X; `POST.json` in this repository names the post, and the
post is the entry.

Built with the make.fun agent kit — https://make.fun
Competition: https://make.fun/bounty/post-x-the-agent-builds-a-game-from-20261122-1709

## The game

`game/neon-serpent.html` is the game the prompt produced: a complete snake
game in one HTML file, no dependencies. Open it in any browser.

- A 24×24 neon board, a snake that shades from teal at its head to magenta at
  its tail, a pulsing golden orb for food, particle bursts and floating
  score text when it eats, and a speed ramp as the score climbs.
- It **plays itself**: an autopilot steers at every step, rejecting moves
  that die and preferring the safe move that closes on the food while
  keeping the most open space reachable (a flood fill), so it survives and
  scores on its own — which is how the video's gameplay was captured.
- A human can take over at any time: arrow keys or WASD, space to pause,
  swipe on touch. Open it with `?auto=0` to start in manual mode.

## How the video was made

Everything was produced by the agent in one session, from code in this
repository:

1. `game/neon-serpent.html` — the game itself, written from the one prompt.
2. `video/capture.mjs` — drives the game in a headless browser with its
   autopilot on and records the frames of a real self-played run.
3. `video/render_video.py` — paints the prompt card, the live-coding
   montage (the game's own source, typing itself onto the screen) and the
   closing call-to-action with Pillow, cuts them together with the captured
   gameplay and make.fun's referral end card (from the official press pack,
   with the referral code typed into its field), synthesises the soundtrack
   with numpy, and encodes the vertical MP4 with ffmpeg.

## Run the hand-in program

`main.ts` copies `POST.json` to the grader's output directory:

    mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts
