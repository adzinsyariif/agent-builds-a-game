// Capture a real self-played run of Neon Serpent for the entry video.
//
// Opens game/neon-serpent.html in a headless browser with the autopilot on
// (its default) and screenshots the page while the snake plays itself, so
// the video's gameplay is the actual game running, not an animation of it.
//
//   node video/capture.mjs <frames-dir> [seconds] [interval-ms]
//
// Puppeteer is resolved from the environment (MAKEFUN_PUPPETEER) when it is
// not installed beside this script; CHROME_PATH overrides the browser.

import { createRequire } from "node:module";
import { mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
let puppeteer;
try {
  puppeteer = require("puppeteer");
} catch {
  puppeteer = require(process.env.MAKEFUN_PUPPETEER ?? "puppeteer");
}

const here = dirname(fileURLToPath(import.meta.url));
const outDir = process.argv[2] ?? join(here, "frames");
const seconds = Number(process.argv[3] ?? 16);
const intervalMs = Number(process.argv[4] ?? 66);

mkdirSync(outDir, { recursive: true });

const browser = await puppeteer.launch({
  headless: "new",
  executablePath: process.env.CHROME_PATH || undefined,
  args: ["--no-sandbox", "--disable-dev-shm-usage", "--force-device-scale-factor=1"],
});
try {
  const page = await browser.newPage();
  await page.setViewport({ width: 1080, height: 1560 });
  const gameUrl = new URL("../game/neon-serpent.html", import.meta.url).href;
  await page.goto(gameUrl, { waitUntil: "load" });
  // Let the run get going so the snake is already hunting when we start.
  await new Promise((r) => setTimeout(r, 1500));
  const frames = Math.floor((seconds * 1000) / intervalMs);
  for (let i = 0; i < frames; i++) {
    const t0 = Date.now();
    await page.screenshot({
      path: join(outDir, `f${String(i).padStart(4, "0")}.jpg`),
      type: "jpeg",
      quality: 86,
    });
    const wait = intervalMs - (Date.now() - t0);
    if (wait > 0) await new Promise((r) => setTimeout(r, wait));
  }
  const score = await page.$eval("#score", (el) => el.textContent);
  console.log(`captured ${frames} frames; score on screen at the end: ${score}`);
} finally {
  await browser.close();
}
