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

2. Infer research structure.
   - Cluster papers by folder topic and recurring title keywords.
   - Separate observed exposure from certainty. Say "your read set suggests exposure to..." rather than "you know...".
   - Use `read` papers as evidence for likely knowledge areas.
   - Use `in-progress` papers as evidence for active consolidation.
   - Use `unread` papers as evidence for planned coverage and gaps.

3. Produce synthesis.
   - Summarize the current center of gravity.
   - Identify likely knowledge areas backed by read papers.
   - Identify active threads backed by in-progress papers.
   - Identify gaps where unread papers outnumber read papers.
   - Recommend a small next-read queue, with reasons tied to existing read or in-progress material.
   - Cite supporting local paper titles for every nontrivial insight.

4. Generate the website.
   - Keep it static and portable: plain HTML/CSS/JS is preferred.
   - Make the first screen the actual dashboard, not a landing page.
   - Keep the design simple, scannable, and informative.
   - Include:
     - status counts
     - topic/theme coverage
     - likely knowledge areas
     - active reading threads
     - future gaps
     - recommended next reads
     - searchable paper table
   - Link back to local files when possible.

5. Validate.
   - Confirm the generated page exists.
   - Confirm counts match the scanned library.
   - Confirm every insight is grounded in specific local papers.
   - If the site uses JavaScript, make sure it still renders meaningful content without a build step.

## Helper Script

This skill includes `scripts/generate_research_map.py`, a dependency-free baseline generator. Use it when the user wants a quick local dashboard:

```bash
python3 scripts/generate_research_map.py "<target_dir>" --output site
```

The script is intentionally heuristic. If the user later wants deeper summaries from paper contents, add an optional PDF extraction path rather than replacing the folder/filename fallback.
