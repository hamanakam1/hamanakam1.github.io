# Software Factory animation maintenance

The current overview is `assets/factory-process-v3.gif`: eight featured project loops from the 39-project illustrated gallery. Every selected project also has its own six-second GIF in `assets/factory-stories/` and an original generated PNG. Forks and the client-specific workspace are excluded.

Private-project concepts use only previously published atlas descriptions. They do not disclose private source or represent screenshots of private software. Public-project concepts cite pinned README sources. The factory process and the moving work packets are explanatory animation, not evidence of a live integrated run.

Build the per-project loops with `python3 scripts/build_project_animations.py`, then the previews, overview and gallery with `python3 scripts/build_factory_stories.py --encode`. The image-generation prompts are in `assets/factory-stories/prompts.json`; source, frame, duration and hash receipts are in `stories.json` and `motion.json` beside them. FFmpeg and cwebp perform format encoding; Pillow checks decoding and frame movement.

The overview must stay below 4 MB; each project loop must stay below 1 MB. These budgets are checked locally and in CI. Verify the actual rendered GitHub image-proxy URL after publishing: a successful direct Pages download is not sufficient.

The old screenshot reel at `assets/factory-tour.gif` remains as a compatible URL for the existing profile. Its compression repair preserves 75 frames and approximately 37.57 seconds at 768×492. `assets/work/reel.json` retains the original source hash and current delivery hash. Its seven original captures and storyboard remain available separately. The legacy screenshot builder must not overwrite the new illustrated overview.
