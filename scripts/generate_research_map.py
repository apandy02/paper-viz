#!/usr/bin/env python3
import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from html import escape
from pathlib import Path
from urllib.parse import quote


PAPER_EXTENSIONS = {".pdf", ".md", ".txt"}

STATUS_LABELS = {
    "read": "Read",
    "unread": "Unread",
    "inprogress": "In Progress",
}

STATUS_CLASS = {
    "read": "read",
    "unread": "unread",
    "inprogress": "progress",
    "unclassified": "unclassified",
}

EXACT_TITLES = {
    "gr00t_humanoid_model": "GR00T Humanoid Model",
    "dreamerv3": "DreamerV3",
    "dreamerv4": "DreamerV4",
    "dreamer1": "Dreamer",
    "dreamerv2": "DreamerV2",
    "robotic_world_models": "Robotic World Models",
    "deep_mimic": "DeepMimic",
    "RoboEval": "RoboEval",
    "vfm_probing": "VFM Probing",
    "ViTs": "Vision Transformers",
    "dinov2": "DINOv2",
    "dinov3": "DINOv3",
    "clip": "CLIP",
    "dino": "DINO",
    "space_time_attention": "Space-Time Attention",
    "RoPE": "RoPE",
    "Genie": "Genie",
    "vpt": "VPT",
    "ai_validity_stanford_hai": "AI Validity",
    "slow_death_of_scaling": "The Slow Death of Scaling",
    "double_descent": "Double Descent",
    "integrated_gradients": "Integrated Gradients",
    "parking_model_macbook": "Parking Model",
    "DiT": "Diffusion Transformers",
    "vq_gan": "VQ-GAN",
    "VQ-VAEs": "VQ-VAEs",
    "MaskGIT": "MaskGIT",
    "Canaries_BrynjolfssonChandarChen": "Canaries",
    "behavior_cloning_from_observation": "Behavior Cloning from Observation",
    "phasic_policy_gradients": "Phasic Policy Gradients",
    "ctrl_world": "CTRL-World",
    "iris_world_models": "IRIS World Models",
    "offline_reinforcement_learning": "Offline Reinforcement Learning",
    "world_models": "World Models",
    "curiosity_icm": "Curiosity and ICM",
    "siglip": "SigLIP",
    "factor_decomposition_vits": "Factor Decomposition in ViTs",
    "sam": "SAM",
    "sam2": "SAM 2",
    "sam3": "SAM 3",
    "viga": "ViGA",
    "EfficientNet": "EfficientNet",
    "sim_clr": "SimCLR",
    "free_transformer": "Free Transformer",
    "DRoPE": "DRoPE",
    "speculative_decoding": "Speculative Decoding",
    "autoeval_robot_evaluation": "AutoEval for Robot Evaluation",
    "active_inference_robots": "Active Inference for Robots",
    "Diffusion_LLMs": "Diffusion LLMs",
    "cpumemory": "CPU and Memory",
    "dreamdojo_world_model": "DreamDojo World Model",
    "lingobot_world": "LingoBot World",
    "VideoAgentTrek": "VideoAgentTrek",
    "diffusion_for_world_modeling": "Diffusion for World Modeling",
    "emergent_temporal_reasoning": "Emergent Temporal Reasoning",
    "v_jepa": "V-JEPA",
    "v_jepa_2": "V-JEPA 2",
    "continuous_thought_machines": "Continuous Thought Machines",
    "autoregressive_video_modelling_encodes_effective_reprs": "Autoregressive Video Modeling Encodes Effective Representations",
    "cosmos_world_simulation": "Cosmos World Simulation",
    "egocentric_task_assistance": "Egocentric Task Assistance",
    "deep_delta_learning": "Deep Delta Learning",
    "MuP": "muP",
    "bogacz_free_energy_tutorial": "Free Energy Tutorial",
    "fantastic_optimizers": "Fantastic Optimizers",
    "dall_e": "DALL-E",
    "Diffusion_Policy": "Diffusion Policy",
}

ACRONYMS = {
    "ai": "AI",
    "rl": "RL",
    "llm": "LLM",
    "vfm": "VFM",
    "vit": "ViT",
    "vits": "ViTs",
    "dino": "DINO",
    "clip": "CLIP",
    "siglip": "SigLIP",
    "sam": "SAM",
    "rope": "RoPE",
    "drope": "DRoPE",
    "dit": "DiT",
    "vq": "VQ",
    "vae": "VAE",
    "vaes": "VAEs",
    "gan": "GAN",
    "maskgit": "MaskGIT",
    "cpu": "CPU",
    "jepa": "JEPA",
    "mup": "muP",
    "icm": "ICM",
}

THEME_RULES = [
    (
        "World Models & Model-Based RL",
        [
            "dreamer",
            "world model",
            "world_models",
            "robotic_world",
            "iris",
            "ctrl_world",
            "cosmos",
            "dreamdojo",
            "lingobot",
            "genie",
            "world simulation",
        ],
    ),
    (
        "Reinforcement Learning & Control",
        [
            "reinforcement",
            "policy gradient",
            "policy_gradients",
            "behavior cloning",
            "offline",
            "curiosity",
            "icm",
            "deep mimic",
            "deep_mimic",
            "active inference",
            "control",
        ],
    ),
    (
        "Robotics & Embodied Agents",
        [
            "robot",
            "robotic",
            "robotics",
            "humanoid",
            "gr00t",
            "autoeval",
            "roboeval",
            "parking",
            "egocentric",
            "embodied",
        ],
    ),
    (
        "Vision Foundation Models",
        [
            "vision",
            "vit",
            "vits",
            "dino",
            "clip",
            "siglip",
            "sam",
            "vfm",
            "efficientnet",
            "simclr",
            "sim_clr",
            "viga",
            "factor decomposition",
        ],
    ),
    (
        "Video & Temporal Reasoning",
        [
            "video",
            "temporal",
            "space time",
            "space_time",
            "vpt",
            "v-jepa",
            "v_jepa",
            "retrieval and execution",
            "continuous thought",
            "autoregressive video",
            "egocentric task",
        ],
    ),
    (
        "Transformers & Attention",
        [
            "transformer",
            "attention",
            "rope",
            "drope",
            "speculative decoding",
            "space time attention",
        ],
    ),
    (
        "Generative Models",
        [
            "diffusion",
            "vq",
            "vae",
            "gan",
            "maskgit",
            "dall",
            "generative",
            "dit",
        ],
    ),
    (
        "Theory, Scaling & Optimization",
        [
            "scaling",
            "double descent",
            "delta learning",
            "optimizer",
            "mup",
            "free energy",
            "integrated gradients",
            "validity",
        ],
    ),
    (
        "Evaluation, Validity & Policy",
        [
            "evaluation",
            "validity",
            "policy",
            "ethics",
            "canaries",
            "autoeval",
            "roboeval",
            "ai-first",
        ],
    ),
    (
        "Systems & Computer Architecture",
        [
            "cpu",
            "memory",
            "computer science",
        ],
    ),
]

THEME_BLURBS = {
    "World Models & Model-Based RL": "model-based agents, latent dynamics, and simulation as a substrate for control",
    "Reinforcement Learning & Control": "learning policies, imitation, offline RL, and curiosity-driven control",
    "Robotics & Embodied Agents": "embodied evaluation, robot policies, and physical-world agents",
    "Vision Foundation Models": "visual representation learning through transformers, contrastive models, and segmentation systems",
    "Video & Temporal Reasoning": "temporal abstraction, video representations, and agents that reason over sequences",
    "Transformers & Attention": "attention mechanisms, positional structure, and efficient decoding",
    "Generative Models": "tokenized generation, diffusion, and image/video generative modeling",
    "Theory, Scaling & Optimization": "learning dynamics, scaling behavior, optimization, and attribution",
    "Evaluation, Validity & Policy": "measurement, validity, evaluation, and societal implications",
    "Systems & Computer Architecture": "lower-level computing foundations that support ML systems work",
}


def normalize_component(value):
    return re.sub(r"[\s_-]+", "", value.lower())


def display_topic(value):
    if not value:
        return "General"
    return value.replace("_", " ").replace("-", " ").strip().title()


def pretty_title(stem):
    if stem in EXACT_TITLES:
        return EXACT_TITLES[stem]
    if re.fullmatch(r"\d{4}\.\d+(v\d+)?", stem):
        return "arXiv " + stem

    text = stem.replace("_", " ").replace("-", " ").replace(" _ ", " ")
    text = re.sub(r"\s+", " ", text).strip()
    words = []
    for word in text.split(" "):
        key = word.lower().strip()
        if key in ACRONYMS:
            words.append(ACRONYMS[key])
        elif re.fullmatch(r"\d+", word):
            words.append(word)
        else:
            words.append(word[:1].upper() + word[1:])
    return " ".join(words) if words else stem


def file_url(path):
    return "file://" + quote(str(path), safe="/:")


def paper_id(path):
    raw = path.stem.lower()
    raw = re.sub(r"[^a-z0-9]+", "-", raw).strip("-")
    return raw or "paper"


def status_and_topic(path, root):
    relative = path.relative_to(root)
    folders = list(relative.parts[:-1])
    status_key = "unclassified"
    status_index = None
    for index, folder in enumerate(folders):
        key = normalize_component(folder)
        if key in STATUS_LABELS:
            status_key = key
            status_index = index
            break

    if status_index is None:
        return status_key, "Unsorted", ""

    topic_parts = folders[status_index + 1 :]
    topic = display_topic(topic_parts[0]) if topic_parts else "General"
    topic_path = " / ".join(topic_parts)
    return status_key, topic, topic_path


def infer_themes(title, topic, path):
    haystack = " ".join([title, topic, path.stem, str(path.parent)]).lower()
    themes = []
    for theme, keywords in THEME_RULES:
        if any(keyword in haystack for keyword in keywords):
            themes.append(theme)
    if not themes and topic not in {"General", "Unsorted"}:
        themes.append(topic)
    if not themes:
        themes.append("General ML")
    return themes


def scan_papers(root):
    papers = []
    seen_ids = Counter()
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.name.startswith("."):
            continue
        if path.suffix.lower() not in PAPER_EXTENSIONS:
            continue
        status_key, topic, topic_path = status_and_topic(path, root)
        base_id = paper_id(path)
        seen_ids[base_id] += 1
        unique_id = base_id if seen_ids[base_id] == 1 else f"{base_id}-{seen_ids[base_id]}"
        title = pretty_title(path.stem)
        themes = infer_themes(title, topic, path)
        papers.append(
            {
                "id": unique_id,
                "title": title,
                "filename": path.name,
                "extension": path.suffix.lower(),
                "status": status_key,
                "status_label": STATUS_LABELS.get(status_key, "Unclassified"),
                "status_class": STATUS_CLASS.get(status_key, "unclassified"),
                "topic": topic,
                "topic_path": topic_path,
                "themes": themes,
                "primary_theme": themes[0],
                "relative_path": str(path.relative_to(root)),
                "absolute_path": str(path),
                "url": file_url(path),
            }
        )
    return papers


def status_counts(papers):
    counts = Counter(p["status"] for p in papers)
    ordered = {
        "read": counts.get("read", 0),
        "inprogress": counts.get("inprogress", 0),
        "unread": counts.get("unread", 0),
        "unclassified": counts.get("unclassified", 0),
    }
    return ordered


def theme_status_counts(papers):
    result = defaultdict(lambda: Counter())
    for paper in papers:
        for theme in paper["themes"]:
            result[theme][paper["status"]] += 1
    return dict(result)


def top_titles(papers, limit=5):
    return [paper["title"] for paper in papers[:limit]]


def support_line(titles):
    if not titles:
        return ""
    if len(titles) == 1:
        return titles[0]
    return ", ".join(titles[:-1]) + ", and " + titles[-1]


def papers_for_theme(papers, theme, status=None):
    matches = [p for p in papers if theme in p["themes"] and (status is None or p["status"] == status)]
    return sorted(matches, key=lambda p: (p["topic"], p["title"]))


def build_insights(papers):
    counts_by_theme = theme_status_counts(papers)
    read_themes = []
    active_threads = []
    future_gaps = []
    bridges = []

    for theme, counts in counts_by_theme.items():
        read_count = counts.get("read", 0)
        progress_count = counts.get("inprogress", 0)
        unread_count = counts.get("unread", 0)
        blurb = THEME_BLURBS.get(theme, theme.lower())

        if read_count:
            sample = top_titles(papers_for_theme(papers, theme, "read"), 4)
            read_themes.append(
                {
                    "theme": theme,
                    "count": read_count,
                    "body": f"Your read set suggests exposure to {blurb}.",
                    "support": support_line(sample),
                }
            )

        if progress_count:
            sample = top_titles(papers_for_theme(papers, theme, "inprogress"), 4)
            active_threads.append(
                {
                    "theme": theme,
                    "count": progress_count,
                    "body": f"This is an active consolidation thread, anchored by {support_line(sample)}.",
                    "support": support_line(sample),
                }
            )

        if unread_count and unread_count >= max(2, read_count + progress_count):
            sample = top_titles(papers_for_theme(papers, theme, "unread"), 5)
            if read_count == 0 and progress_count == 0:
                body = "This looks like a future frontier rather than an established area in the current read set."
            else:
                body = "This area has a larger planned shelf than demonstrated read coverage, so it is a likely expansion zone."
            future_gaps.append(
                {
                    "theme": theme,
                    "count": unread_count,
                    "body": body,
                    "support": support_line(sample),
                    "score": unread_count - read_count - progress_count,
                }
            )

        if read_count and unread_count:
            read_sample = support_line(top_titles(papers_for_theme(papers, theme, "read"), 2))
            unread_sample = support_line(top_titles(papers_for_theme(papers, theme, "unread"), 2))
            bridges.append(
                {
                    "theme": theme,
                    "body": f"Extend from {read_sample} toward {unread_sample}.",
                    "score": read_count + unread_count + progress_count,
                }
            )

    read_themes.sort(key=lambda item: (-item["count"], item["theme"]))
    active_threads.sort(key=lambda item: (-item["count"], item["theme"]))
    future_gaps.sort(key=lambda item: (-item["score"], item["theme"]))
    bridges.sort(key=lambda item: (-item["score"], item["theme"]))

    return {
        "knowledge": read_themes[:6],
        "active": active_threads[:5],
        "gaps": future_gaps[:6],
        "bridges": bridges[:6],
    }


def topic_rows(papers):
    rows = {}
    for paper in papers:
        key = paper["topic"]
        rows.setdefault(key, Counter())
        rows[key][paper["status"]] += 1
    sortable = []
    for topic, counts in rows.items():
        total = sum(counts.values())
        sortable.append(
            {
                "topic": topic,
                "read": counts.get("read", 0),
                "inprogress": counts.get("inprogress", 0),
                "unread": counts.get("unread", 0),
                "unclassified": counts.get("unclassified", 0),
                "total": total,
            }
        )
    return sorted(sortable, key=lambda row: (-row["total"], row["topic"]))


def theme_rows(papers):
    rows = []
    for theme, counts in theme_status_counts(papers).items():
        total = sum(counts.values())
        rows.append(
            {
                "theme": theme,
                "read": counts.get("read", 0),
                "inprogress": counts.get("inprogress", 0),
                "unread": counts.get("unread", 0),
                "unclassified": counts.get("unclassified", 0),
                "total": total,
            }
        )
    return sorted(rows, key=lambda row: (-row["total"], row["theme"]))


def recommend_next_reads(papers):
    theme_counts = theme_status_counts(papers)
    topic_counts = defaultdict(Counter)
    for paper in papers:
        topic_counts[paper["topic"]][paper["status"]] += 1

    recommendations = []
    for paper in papers:
        if paper["status"] != "unread":
            continue
        score = 0.0
        reasons = []
        for theme in paper["themes"]:
            counts = theme_counts[theme]
            if counts.get("inprogress", 0):
                score += 3
                reasons.append(f"connects to your active {theme} thread")
            if counts.get("read", 0):
                score += 2
                reasons.append(f"builds on read coverage in {theme}")
            if counts.get("read", 0) == 0 and counts.get("inprogress", 0) == 0:
                score += 0.5
                reasons.append(f"opens a newer shelf in {theme}")

        if topic_counts[paper["topic"]].get("read", 0):
            score += 1.5
            reasons.append(f"continues the {paper['topic']} folder")

        title_lower = paper["title"].lower()
        if "dreamer" in title_lower or "world model" in title_lower:
            score += 1.5
        if "sam" in title_lower or "jepa" in title_lower:
            score += 1.0
        if "diffusion policy" in title_lower:
            score += 1.0

        deduped = []
        for reason in reasons:
            if reason not in deduped:
                deduped.append(reason)

        recommendations.append(
            {
                "paper": paper,
                "score": score,
                "reasons": deduped[:3] or ["adds breadth to the unread shelf"],
            }
        )

    recommendations.sort(key=lambda item: (-item["score"], item["paper"]["topic"], item["paper"]["title"]))
    return recommendations[:10]


def center_of_gravity(papers):
    rows = theme_rows(papers)
    status = status_counts(papers)
    read_focus = [row["theme"] for row in rows if row["read"]][:3]
    future_focus = [row["theme"] for row in rows if row["unread"] and row["unread"] >= row["read"]][:3]
    active_focus = [row["theme"] for row in rows if row["inprogress"]][:3]

    if read_focus:
        read_sentence = "Your read base is strongest in " + human_join(read_focus) + "."
    else:
        read_sentence = "The read shelf is not yet large enough to infer a stable knowledge base."

    if active_focus:
        active_sentence = "Current reading is pulling attention toward " + human_join(active_focus) + "."
    else:
        active_sentence = "No in-progress papers were found, so the current thread is not explicit."

    if future_focus:
        future_sentence = "The unread shelf expands most toward " + human_join(future_focus) + "."
    else:
        future_sentence = "The unread shelf is small relative to the read set."

    return {
        "headline": "A compact map of your paper library",
        "body": f"{read_sentence} {active_sentence} {future_sentence}",
        "counts": status,
    }


def human_join(items):
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return items[0] + " and " + items[1]
    return ", ".join(items[:-1]) + ", and " + items[-1]


def metric_card(label, value, hint):
    return f"""
    <section class="metric">
      <div class="metric-value">{escape(str(value))}</div>
      <div class="metric-label">{escape(label)}</div>
      <p>{escape(hint)}</p>
    </section>
    """


def insight_card(item):
    return f"""
    <article class="insight-card">
      <h3>{escape(item["theme"])}</h3>
      <p>{escape(item["body"])}</p>
      <div class="support">Evidence: {escape(item["support"])}</div>
    </article>
    """


def empty_state(text):
    return f'<p class="empty">{escape(text)}</p>'


def bar_row(row, label_key):
    total = max(row["total"], 1)
    read = row["read"] / total * 100
    progress = row["inprogress"] / total * 100
    unread = row["unread"] / total * 100
    unclassified = row["unclassified"] / total * 100
    return f"""
    <div class="coverage-row">
      <div class="coverage-label">
        <strong>{escape(row[label_key])}</strong>
        <span>{row["total"]} papers</span>
      </div>
      <div class="stacked-bar" aria-label="{escape(row[label_key])} coverage">
        <span class="bar-read" style="width:{read:.2f}%"></span>
        <span class="bar-progress" style="width:{progress:.2f}%"></span>
        <span class="bar-unread" style="width:{unread:.2f}%"></span>
        <span class="bar-unclassified" style="width:{unclassified:.2f}%"></span>
      </div>
      <div class="coverage-counts">
        <span>{row["read"]} read</span>
        <span>{row["inprogress"]} active</span>
        <span>{row["unread"]} unread</span>
      </div>
    </div>
    """


def recommendation_card(item, index):
    paper = item["paper"]
    reasons = "; ".join(item["reasons"])
    return f"""
    <article class="recommendation">
      <div class="rank">{index}</div>
      <div>
        <h3><a href="{escape(paper["url"])}">{escape(paper["title"])}</a></h3>
        <p>{escape(reasons)}.</p>
        <div class="support">{escape(paper["topic"])} - {escape(", ".join(paper["themes"]))}</div>
      </div>
    </article>
    """


def bridge_card(item):
    return f"""
    <article class="bridge">
      <h3>{escape(item["theme"])}</h3>
      <p>{escape(item["body"])}</p>
    </article>
    """


def paper_row(paper):
    themes = ", ".join(paper["themes"])
    return f"""
    <tr data-status="{escape(paper["status"])}" data-topic="{escape(paper["topic"])}" data-search="{escape((paper["title"] + " " + paper["topic"] + " " + themes).lower())}">
      <td><a href="{escape(paper["url"])}">{escape(paper["title"])}</a></td>
      <td><span class="pill {escape(paper["status_class"])}">{escape(paper["status_label"])}</span></td>
      <td>{escape(paper["topic"])}</td>
      <td>{escape(themes)}</td>
    </tr>
    """


def build_svg(theme_data):
    top = theme_data[:8]
    if not top:
        return ""
    width = 900
    height = 360
    center_x = width / 2
    center_y = height / 2
    radius = 130
    nodes = []
    links = []
    max_total = max(row["total"] for row in top)
    for index, row in enumerate(top):
        angle = (index / len(top)) * 6.28318530718 - 1.5708
        x = center_x + radius * __import__("math").cos(angle)
        y = center_y + radius * __import__("math").sin(angle)
        size = 28 + (row["total"] / max_total) * 32
        links.append(f'<line x1="{center_x:.1f}" y1="{center_y:.1f}" x2="{x:.1f}" y2="{y:.1f}" />')
        nodes.append(
            f"""
            <g>
              <circle cx="{x:.1f}" cy="{y:.1f}" r="{size / 2:.1f}" />
              <text x="{x:.1f}" y="{y + size / 2 + 18:.1f}" text-anchor="middle">{escape(short_theme(row["theme"]))}</text>
            </g>
            """
        )
    return f"""
    <svg class="map-svg" viewBox="0 0 {width} {height}" role="img" aria-label="Theme map">
      <g class="links">{''.join(links)}</g>
      <circle class="map-core" cx="{center_x:.1f}" cy="{center_y:.1f}" r="48" />
      <text class="core-text" x="{center_x:.1f}" y="{center_y - 4:.1f}" text-anchor="middle">Paper</text>
      <text class="core-text" x="{center_x:.1f}" y="{center_y + 16:.1f}" text-anchor="middle">Library</text>
      <g class="nodes">{''.join(nodes)}</g>
    </svg>
    """


def short_theme(theme):
    replacements = {
        "World Models & Model-Based RL": "World Models",
        "Reinforcement Learning & Control": "RL & Control",
        "Robotics & Embodied Agents": "Robotics",
        "Vision Foundation Models": "Vision FMs",
        "Video & Temporal Reasoning": "Video/Time",
        "Transformers & Attention": "Attention",
        "Theory, Scaling & Optimization": "Theory",
        "Evaluation, Validity & Policy": "Evaluation",
        "Systems & Computer Architecture": "Systems",
    }
    return replacements.get(theme, theme)


def write_outputs(root, output_dir, papers):
    output_dir.mkdir(parents=True, exist_ok=True)
    counts = status_counts(papers)
    insights = build_insights(papers)
    recommendations = recommend_next_reads(papers)
    topics = topic_rows(papers)
    themes = theme_rows(papers)
    center = center_of_gravity(papers)
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    data = {
        "source": str(root),
        "generated_at": generated_at,
        "counts": counts,
        "center": center,
        "topics": topics,
        "themes": themes,
        "insights": insights,
        "recommendations": [
            {"paper": item["paper"], "score": item["score"], "reasons": item["reasons"]}
            for item in recommendations
        ],
        "papers": papers,
    }
    (output_dir / "research-map-data.json").write_text(json.dumps(data, indent=2), encoding="utf-8")

    metrics = "\n".join(
        [
            metric_card("Total papers", len(papers), "Local files included in this scan."),
            metric_card("Read", counts["read"], "Evidence for likely knowledge areas."),
            metric_card("In progress", counts["inprogress"], "Your active consolidation layer."),
            metric_card("Unread", counts["unread"], "Planned coverage and future gaps."),
        ]
    )

    knowledge_html = "\n".join(insight_card(item) for item in insights["knowledge"]) or empty_state("No read papers found.")
    active_html = "\n".join(insight_card(item) for item in insights["active"]) or empty_state("No in-progress papers found.")
    gaps_html = "\n".join(insight_card(item) for item in insights["gaps"]) or empty_state("No major unread gaps detected.")
    topic_html = "\n".join(bar_row(row, "topic") for row in topics)
    theme_html = "\n".join(bar_row(row, "theme") for row in themes)
    rec_html = "\n".join(recommendation_card(item, index + 1) for index, item in enumerate(recommendations)) or empty_state("No unread papers found.")
    bridge_html = "\n".join(bridge_card(item) for item in insights["bridges"]) or empty_state("No read-to-unread bridges detected.")
    table_rows = "\n".join(paper_row(paper) for paper in papers)
    svg = build_svg(themes)

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Research Reading Map</title>
  <style>
    :root {{
      --ink: #18201f;
      --muted: #62706f;
      --paper: #fbfaf7;
      --panel: #ffffff;
      --line: #dde3df;
      --read: #197278;
      --progress: #c05621;
      --unread: #596f9f;
      --unclassified: #8b8f97;
      --accent: #8a4f7d;
      --soft: #eef4f2;
      --shadow: 0 10px 30px rgba(24, 32, 31, 0.08);
    }}

    * {{ box-sizing: border-box; }}

    body {{
      margin: 0;
      background: var(--paper);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.45;
    }}

    a {{ color: inherit; }}

    .shell {{
      width: min(1180px, calc(100vw - 32px));
      margin: 0 auto;
      padding: 28px 0 44px;
    }}

    header {{
      display: grid;
      grid-template-columns: minmax(0, 1.4fr) minmax(280px, 0.8fr);
      gap: 24px;
      align-items: stretch;
      padding: 12px 0 18px;
    }}

    .intro {{
      padding: 26px;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: var(--shadow);
    }}

    h1 {{
      margin: 0;
      font-size: 42px;
      line-height: 1.02;
      letter-spacing: 0;
    }}

    .intro p {{
      max-width: 780px;
      margin: 14px 0 0;
      color: var(--muted);
      font-size: 16px;
    }}

    .source {{
      margin-top: 18px;
      color: var(--muted);
      font-size: 13px;
      overflow-wrap: anywhere;
    }}

    .legend {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 18px;
    }}

    .legend span, .pill {{
      display: inline-flex;
      align-items: center;
      min-height: 26px;
      padding: 4px 9px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 700;
      white-space: nowrap;
    }}

    .read {{ background: #dff1ee; color: #0f5558; }}
    .progress {{ background: #f6dfcf; color: #8f3f12; }}
    .unread {{ background: #e7ecf8; color: #354f8d; }}
    .unclassified {{ background: #eceef1; color: #5f6670; }}

    .map-panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: var(--shadow);
      padding: 14px;
      min-height: 330px;
    }}

    .map-svg {{
      width: 100%;
      height: 100%;
      min-height: 300px;
      display: block;
    }}

    .map-svg line {{
      stroke: #c6d3ce;
      stroke-width: 2;
    }}

    .map-core {{
      fill: #18201f;
    }}

    .core-text {{
      fill: #ffffff;
      font-size: 14px;
      font-weight: 800;
    }}

    .nodes circle {{
      fill: #fff7eb;
      stroke: var(--accent);
      stroke-width: 3;
    }}

    .nodes text {{
      fill: var(--ink);
      font-size: 13px;
      font-weight: 800;
    }}

    .metrics {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin: 8px 0 28px;
    }}

    .metric, .insight-card, .recommendation, .bridge, .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: var(--shadow);
    }}

    .metric {{
      padding: 18px;
      min-height: 126px;
    }}

    .metric-value {{
      font-size: 34px;
      font-weight: 850;
      line-height: 1;
    }}

    .metric-label {{
      margin-top: 8px;
      font-weight: 800;
    }}

    .metric p {{
      margin: 8px 0 0;
      color: var(--muted);
      font-size: 13px;
    }}

    .grid-2 {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 18px;
      margin-bottom: 18px;
    }}

    .panel {{
      padding: 20px;
      min-width: 0;
    }}

    .panel h2 {{
      margin: 0 0 14px;
      font-size: 21px;
      letter-spacing: 0;
    }}

    .panel-note {{
      margin: -4px 0 16px;
      color: var(--muted);
      font-size: 14px;
    }}

    .insight-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }}

    .insight-card, .bridge {{
      padding: 15px;
      box-shadow: none;
      background: #fffefd;
    }}

    .insight-card h3, .bridge h3, .recommendation h3 {{
      margin: 0;
      font-size: 15px;
      line-height: 1.25;
    }}

    .insight-card p, .bridge p, .recommendation p {{
      margin: 8px 0 0;
      color: var(--muted);
      font-size: 14px;
    }}

    .support {{
      margin-top: 10px;
      color: #44504e;
      font-size: 12px;
      font-weight: 700;
    }}

    .coverage-row {{
      display: grid;
      grid-template-columns: minmax(180px, 0.9fr) minmax(160px, 1fr) minmax(190px, 0.7fr);
      gap: 12px;
      align-items: center;
      padding: 10px 0;
      border-top: 1px solid var(--line);
    }}

    .coverage-row:first-child {{ border-top: 0; }}

    .coverage-label strong {{
      display: block;
      font-size: 14px;
    }}

    .coverage-label span, .coverage-counts {{
      color: var(--muted);
      font-size: 12px;
    }}

    .coverage-counts {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      justify-content: flex-end;
    }}

    .stacked-bar {{
      display: flex;
      height: 12px;
      overflow: hidden;
      border-radius: 999px;
      background: #edf0ee;
    }}

    .stacked-bar span {{ min-width: 0; }}
    .bar-read {{ background: var(--read); }}
    .bar-progress {{ background: var(--progress); }}
    .bar-unread {{ background: var(--unread); }}
    .bar-unclassified {{ background: var(--unclassified); }}

    .recommendations {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }}

    .recommendation {{
      display: grid;
      grid-template-columns: 38px minmax(0, 1fr);
      gap: 12px;
      padding: 15px;
      box-shadow: none;
    }}

    .rank {{
      width: 32px;
      height: 32px;
      display: grid;
      place-items: center;
      border-radius: 50%;
      color: white;
      background: var(--ink);
      font-weight: 850;
    }}

    .toolbar {{
      display: grid;
      grid-template-columns: minmax(220px, 1fr) 180px 180px;
      gap: 10px;
      margin-bottom: 12px;
    }}

    input, select {{
      width: 100%;
      min-height: 40px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
      color: var(--ink);
      padding: 8px 10px;
      font: inherit;
    }}

    .table-wrap {{
      overflow-x: auto;
      border: 1px solid var(--line);
      border-radius: 8px;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      min-width: 760px;
      background: #fff;
    }}

    th, td {{
      padding: 11px 12px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
      font-size: 14px;
    }}

    th {{
      color: #3b4745;
      background: var(--soft);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0;
    }}

    tr:last-child td {{ border-bottom: 0; }}

    .empty {{
      color: var(--muted);
      margin: 0;
    }}

    footer {{
      margin-top: 18px;
      color: var(--muted);
      font-size: 12px;
      text-align: center;
    }}

    @media (max-width: 920px) {{
      header, .grid-2, .metrics, .insight-grid, .recommendations {{
        grid-template-columns: 1fr;
      }}

      h1 {{ font-size: 34px; }}

      .coverage-row {{
        grid-template-columns: 1fr;
      }}

      .coverage-counts {{
        justify-content: flex-start;
      }}

      .toolbar {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <main class="shell">
    <header>
      <section class="intro">
        <h1>{escape(center["headline"])}</h1>
        <p>{escape(center["body"])}</p>
        <div class="source">Source: {escape(str(root))}<br>Generated: {escape(generated_at)}</div>
        <div class="legend" aria-label="Status legend">
          <span class="read">Read</span>
          <span class="progress">In Progress</span>
          <span class="unread">Unread</span>
          <span class="unclassified">Unclassified</span>
        </div>
      </section>
      <section class="map-panel">
        {svg}
      </section>
    </header>

    <section class="metrics">
      {metrics}
    </section>

    <section class="grid-2">
      <section class="panel">
        <h2>Likely Knowledge Areas</h2>
        <p class="panel-note">Inferred from papers already in the read shelf. These are exposure signals, not claims of mastery.</p>
        <div class="insight-grid">{knowledge_html}</div>
      </section>

      <section class="panel">
        <h2>Active Threads</h2>
        <p class="panel-note">The in-progress shelf shows what is currently being consolidated.</p>
        <div class="insight-grid">{active_html}</div>
      </section>
    </section>

    <section class="grid-2">
      <section class="panel">
        <h2>Future Gaps</h2>
        <p class="panel-note">Areas where the unread shelf is larger than the existing read base.</p>
        <div class="insight-grid">{gaps_html}</div>
      </section>

      <section class="panel">
        <h2>Read-To-Unread Bridges</h2>
        <p class="panel-note">Natural paths from things already read into planned papers.</p>
        <div class="insight-grid">{bridge_html}</div>
      </section>
    </section>

    <section class="panel">
      <h2>Recommended Next Reads</h2>
      <p class="panel-note">Ranked by connection to read and in-progress material, with a small boost for recurring themes.</p>
      <div class="recommendations">{rec_html}</div>
    </section>

    <section class="grid-2" style="margin-top:18px;">
      <section class="panel">
        <h2>Topic Coverage</h2>
        {topic_html}
      </section>
      <section class="panel">
        <h2>Theme Coverage</h2>
        {theme_html}
      </section>
    </section>

    <section class="panel">
      <h2>Paper Library</h2>
      <div class="toolbar">
        <input id="search" type="search" placeholder="Search papers, topics, or themes" aria-label="Search papers">
        <select id="statusFilter" aria-label="Filter by status">
          <option value="">All statuses</option>
          <option value="read">Read</option>
          <option value="inprogress">In Progress</option>
          <option value="unread">Unread</option>
          <option value="unclassified">Unclassified</option>
        </select>
        <select id="topicFilter" aria-label="Filter by topic">
          <option value="">All topics</option>
          {"".join(f'<option value="{escape(row["topic"])}">{escape(row["topic"])}</option>' for row in topics)}
        </select>
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Paper</th>
              <th>Status</th>
              <th>Topic</th>
              <th>Themes</th>
            </tr>
          </thead>
          <tbody id="paperRows">
            {table_rows}
          </tbody>
        </table>
      </div>
    </section>

    <footer>
      Built from local filenames and folder structure. Add PDF extraction later for deeper abstracts and author metadata.
    </footer>
  </main>
  <script>
    const search = document.getElementById('search');
    const statusFilter = document.getElementById('statusFilter');
    const topicFilter = document.getElementById('topicFilter');
    const rows = Array.from(document.querySelectorAll('#paperRows tr'));

    function applyFilters() {{
      const query = search.value.trim().toLowerCase();
      const status = statusFilter.value;
      const topic = topicFilter.value;
      rows.forEach((row) => {{
        const matchesQuery = !query || row.dataset.search.includes(query);
        const matchesStatus = !status || row.dataset.status === status;
        const matchesTopic = !topic || row.dataset.topic === topic;
        row.style.display = matchesQuery && matchesStatus && matchesTopic ? '' : 'none';
      }});
    }}

    search.addEventListener('input', applyFilters);
    statusFilter.addEventListener('change', applyFilters);
    topicFilter.addEventListener('change', applyFilters);
  </script>
</body>
</html>
"""
    (output_dir / "index.html").write_text(html, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Generate a static research reading map from a local paper directory.")
    parser.add_argument("target_dir", help="Directory containing read/unread/in-progress paper folders.")
    parser.add_argument("--output", default="site", help="Output directory for index.html and JSON data.")
    args = parser.parse_args()

    root = Path(args.target_dir).expanduser().resolve()
    output_dir = Path(args.output).expanduser().resolve()

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Target directory does not exist: {root}")

    papers = scan_papers(root)
    if not papers:
        raise SystemExit(f"No paper files found in: {root}")

    write_outputs(root, output_dir, papers)
    counts = status_counts(papers)
    print(f"Generated {output_dir / 'index.html'}")
    print(f"Scanned {len(papers)} papers: {counts['read']} read, {counts['inprogress']} in progress, {counts['unread']} unread, {counts['unclassified']} unclassified")


if __name__ == "__main__":
    main()
