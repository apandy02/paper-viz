---
name: research-reading-map
description: Use when asked to analyze a local research papers directory organized by read, unread, and in-progress folders, then generate a simple static website that maps reading progress, inferred knowledge areas, gaps, and recommended next reads.
---

# Research Reading Map

Use this skill to turn a local paper library into a small research dashboard. The expected input is a directory containing status folders such as `read`, `unread`, and `in-progress`, with optional topic subfolders beneath them.

## Inputs

- `target_dir`: the local papers directory to analyze.
- `output_dir`: where to write the generated website.

Normalize status folders case-insensitively:

- `read`, `Read`
- `unread`, `Unread`
- `in-progress`, `in_progress`, `in progress`

Treat the first folder below a status folder as the paper's topic. Files outside status folders should be marked `unclassified` and surfaced as cleanup candidates.

## Workflow

1. Inventory the library.
   - Scan for `.pdf`, `.md`, and `.txt` files.
   - Ignore system files such as `.DS_Store`.
   - Record file path, status, topic folder, display title, and any obvious identifiers such as arXiv-style IDs.
   - Prefer sidecar notes or text files if present. If PDF text extraction tools are available, use them to improve titles and abstracts. If not, fall back to filenames and folders.
   - Capture filesystem metadata when available:
     - file creation/birth time as an approximate "added to library" date
     - modified time as a weak signal only
     - macOS `kMDItemDateAdded` or `kMDItemLastUsedDate` when available
   - Clearly label metadata-derived dates as approximate because copying files, cloud sync, archive extraction, and some PDF readers can rewrite or omit them.

2. Infer research structure.
   - Cluster papers by folder topic and recurring title keywords.
   - Separate observed exposure from certainty. Say "your read set suggests exposure to..." rather than "you know...".
   - Use `read` papers as evidence for likely knowledge areas.
   - Use `in-progress` papers as evidence for active consolidation.
   - Use `unread` papers as evidence for planned coverage and gaps.
   - If prior run history exists, infer transitions such as `unread -> in-progress -> read`; use first observed transition into `read` as the best available finished date.

3. Produce synthesis.
   - Summarize the current center of gravity.
   - Identify likely knowledge areas backed by read papers.
   - Identify active threads backed by in-progress papers.
   - Identify gaps where unread papers outnumber read papers.
   - Recommend a small next-read queue, with reasons tied to existing read or in-progress material.
   - Include reading-flow metrics when evidence exists:
     - unread age: days since file creation/date-added or first observed unread status
     - active age: days since first observed in-progress status
     - finished date: first observed date in `read`, or approximate last-opened date only if explicitly labeled
     - burndown: count of unread/in-progress/read papers over repeated runs
   - Cite supporting local paper titles for every nontrivial insight.

4. Generate the website.
   - Keep it static and portable: plain HTML/CSS/JS is preferred.
   - Make the first screen the actual dashboard, not a landing page.
   - Keep the design simple, scannable, and informative.
   - Generate a cover image with the `imagegen` skill whenever image generation is available. The cover should be a wide, immersive bitmap image based on the inferred center of gravity of the library. For this research-map use case, prompt it as a Notion-style page cover showing a utopian future as imagined by a reader whose paper list centers on the observed themes, such as embodied AI, robotics, world models, vision, video/temporal reasoning, generative models, evaluation, and AI governance. Do not include text, logos, watermarks, frames, device mockups, UI chrome, borders, or bezels in the image.
   - Store generated cover assets in a gitignored generated-assets directory, copy the selected final asset into the project, and reference that local file from the generated site. Never reference an image that only exists in the default image-generation output location.
   - Present the cover as a full-width page cover similar to a Notion page cover: no card, no inset border, no bezel, no overlay panel, and no padding above it. Put the dashboard title and metrics below the cover, not on top of it.
   - Prefer relationship visuals that explain the library. Avoid large decorative hub-and-spoke graphs that only show topic counts.
   - For a theme graph, connect themes only when local papers bridge multiple themes. Use edge weight to show shared-paper count, node size to show theme coverage, and node color or annotation to show dominant reading status.
   - The theme graph section should pair the graph with a concise interpretation of the graph: strongest bridges, central themes, what the graph suggests about the library's research direction, and which local papers support those observations.
   - Give dense relationship maps enough horizontal space for their labels. If a side-by-side summary would make the map or legend feel cramped, put the interpretation below the graph instead.
   - Use legends with readable labels in all layouts. Prefer small swatches or icons beside text over text placed inside colored blocks, and verify color contrast before finishing.
   - Do not place status/progress coverage lists next to the graph. Put progress, topic coverage, aging, and burndown in separate dedicated sections.
   - Include:
     - status counts
     - topic/theme coverage
     - relationship map or overlap view showing how research areas connect
     - graph summary grounded in bridge edges and supporting paper titles
     - likely knowledge areas
     - active reading threads
     - future gaps
     - recommended next reads
     - optional aging and burndown charts when metadata or run history exists
     - searchable paper table
   - Link back to local files when possible.
   - If image generation is useful, create optional bitmap assets in a gitignored generated-assets directory and reference them from the generated site. Good uses include a small conceptual research-map illustration, topic cluster thumbnails, or section header art. Do not make core facts depend on generated images.

5. Validate.
   - Confirm the generated page exists.
   - Confirm counts match the scanned library.
   - Confirm every insight is grounded in specific local papers.
   - Confirm the cover image exists locally, is referenced by the site, and renders as a full-width cover without visible bezels, cards, borders, or padding above it.
   - Confirm the graph section has enough room for labels, contains an explanatory summary rather than adjacent progress/status coverage controls, and uses a readable legend.
   - If the site uses JavaScript, make sure it still renders meaningful content without a build step.

## Implementation Notes

- Do not rely on committed helper scripts. If code is useful, create it on the fly inside a gitignored working directory such as `scripts/`, run it, and leave it out of version control.
- Keep generated websites and generated image assets out of the skill repo unless the user explicitly asks to commit examples.
- If a durable reading history is desired, write it to a local gitignored file such as `.research-map/history.json` or to a user-specified state file near the paper directory.
- Use stable paper identities when tracking history. Prefer a content hash when practical; otherwise combine normalized relative path, filename, size, and creation/date-added metadata.

### Date Signals

- `date added` or file birth time is usually the best estimate for "how long has this been in the library?"
- `last opened` can hint at engagement, but it is not a reliable finished date. Some viewers update it inconsistently, and background indexing may affect it.
- Folder movement time is not generally recoverable from the filesystem after the fact. To know when a paper moved from unread to read, maintain run history and compare statuses across runs.
- If a paper is already in `read` on the first run, mark its finished date as "before first scan" unless stronger evidence exists.
