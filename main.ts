// Entry program for the make.fun bounty "The agent builds a game from one prompt".
//
// The entry itself is a post on X: a short video of an AI agent building the
// Neon Serpent browser game in this repository from a single prompt. This
// program has one job — hand the post's address to the grader. It reads
// POST.json at the repository root and writes it, unchanged, to POST.json in
// the output directory, where the house's gate picks it up and reads the post.
//
// Locally the grader's mounts are stood in for by two environment variables:
//   mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, existsSync, mkdirSync } from "node:fs";
import { join } from "node:path";

const botDir = process.env.MAKEFUN_BOT_DIR ?? "/bot";
const outputDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";

const source = join(botDir, "POST.json");
if (!existsSync(source)) {
  console.error(`no POST.json at ${source} — nothing to hand in`);
  process.exit(1);
}

mkdirSync(outputDir, { recursive: true });
copyFileSync(source, join(outputDir, "POST.json"));
