# Software Factory animation maintenance

The current overview is `assets/factory-process-v3.gif`: featured factory workflows followed by independent experiments from the 39-project illustrated gallery. Every selected project has its own GIF and original generated PNG in `assets/factory-stories/`. Ordinary projects use six-second, 180-frame loops. AI Dashboard uses a 16-second, 480-frame sequence with four illustrated chapters. The profile preview runs at twice the gallery pace and links to the full walkthrough. Forks and the client-specific workspace are excluded.

Private-project concepts use only previously published atlas descriptions. They do not disclose private source or represent screenshots of private software. Public-project concepts cite pinned README sources. The factory process and the moving project-specific objects are explanatory animation, not evidence of a live integrated run.

Build the per-project loops with `python3 scripts/build_project_animations.py`, then the previews, overview and gallery with `python3 scripts/build_factory_stories.py --encode`. The image-generation prompts are in `assets/factory-stories/prompts.json`; source, frame, duration and hash receipts are in `stories.json` and `motion.json` beside them. FFmpeg and cwebp perform format encoding; Pillow checks decoding and frame movement.

The overview must stay below 4 MB; ordinary project loops must stay below 1 MB, and the expanded AI Dashboard loop must stay below 3 MB. These budgets are checked locally and in CI. Verify the actual rendered GitHub image-proxy URL after publishing: a successful direct Pages download is not sufficient.

The old screenshot reel at `assets/factory-tour.gif` remains as a compatible URL for the existing profile. Its compression repair preserves 75 frames and approximately 37.57 seconds at 768×492. `assets/work/reel.json` retains the original source hash and current delivery hash. Its seven original captures and storyboard remain available separately. The legacy screenshot builder must not overwrite the new illustrated overview.
