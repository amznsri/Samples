import os
import io
import json
import time
import base64
import tempfile
import requests
import streamlit as st
from PIL import Image
import cv2

st.set_page_config(page_title="E-commerce Video Quality Checker", layout="wide")

DEFAULT_MODEL = ""

SYSTEM_PROMPT = """
You are a professional video generation quality comparison system.
Check the video that is created as per the prompt and use below guidelines to provide dimension-wise preference judgments..
---
## 【1】Structure Preservation (structure_preservation)
Evaluate whether the video preserves subject identity and structural integrity.
1. subject_consistency
- Subject appearance, texture, logo, and identity remain consistent
- No deformation, melting, abnormal changes, or identity drift
2. text_consistency
- Text on subject (logos, product text) remains clear and stable
- No sudden disappearance or distortion
3. structure_reasonability
- Human/object proportions follow visual norms and physics
- No collapse, distortion, penetration, or abnormal deformation
---
##【2】Instruction Following (instruction_following)
Evaluate how well the video follows the text prompt instructions.
1. subject_action_consistency
- Correct subject performs the required actions
- No wrong subject moving while intended subject stays static
2. object_action_consistency
- Object identity remains consistent throughout the video
- Correct object performs the required actions
- No wrong object moving while intended object stays static
3. camera_motion_consistency
- Camera movements (pan, zoom, tracking, dolly, rotation) match the prompt
- No missing or contradictory camera motion
4. degree_adverb_consistency
- Degree adverbs (slowly, rapidly, slightly, dramatically) are respected
- Motion speed and intensity match the description
5. environment_scene_consistency
- Scene, background, lighting, and atmosphere match the prompt
- Scene changes and transitions are correctly reflected
6. temporal_order_consistency
- Multi-step instructions are executed in the correct temporal order
- No step skipping, reversal, or merging
---
## 【3】Motion Performance (motion_performance)
Evaluate motion quality itself (NOT whether it follows the prompt).
1. motion_amplitude
- Motion scale is appropriate for the scene
- Static ≠ disadvantage, motion ≠ advantage
2. motion_physical
- Motion follows physics and context
- No floating, teleportation, clipping, or sudden disappearance
3. motion_liveliness
- Motion is smooth and natural
- No stiff, robotic, or mechanical movement

You must return a compact JSON with keys structure_preservation, instruction_following, motion_performance.
For each key, include overall with fields score (0-5) and explanation, and include sub-keys with score (0-5) and explanation for each item listed above.
Keep explanations concise for a single frame.
"""

def to_data_url(image_bytes: bytes, fmt: str = "jpeg") -> str:
    b64 = base64.b64encode(image_bytes).decode("ascii")
    return f"data:image/{fmt};base64,{b64}"

def extract_frames(path: str, target_fps: int = 12, max_seconds: float | None = None, max_frames: int | None = None):
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    if not fps or fps <= 0:
        fps = 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if total_frames > 0 else 0
    if max_seconds is not None:
        duration = min(duration, max_seconds)
    interval = 1.0 / float(target_fps)
    frames = []
    idx = 0
    next_t = 0.0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        t = idx / fps
        if t > duration:
            break
        if t + 1e-6 >= next_t:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(rgb)
            buf = io.BytesIO()
            image.save(buf, format="JPEG", quality=90)
            frames.append((t, buf.getvalue()))
            next_t += interval
            if max_frames is not None and len(frames) >= max_frames:
                break
        idx += 1
    cap.release()
    return frames, duration

def call_vision_api(image_bytes: bytes, prompt: str, model: str, api_key: str, detail: str = "high"):
    url = "https://ark.ap-southeast.bytepluses.com/api/v3/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    user_text = f"Initial prompt: {prompt}. Evaluate this frame."
    payload = {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_text},
                    {"type": "image_url", "image_url": {"url": to_data_url(image_bytes, "jpeg"), "detail": detail}},
                ],
            },
        ],
        "model": model,
    }
    r = requests.post(url, json=payload, headers=headers, timeout=120)
    if r.status_code != 200:
        return {"error": True, "status": r.status_code, "body": r.text}
    data = r.json()
    content = (
        data.get("choices", [{}])[0]
        .get("message", {})
        .get("content", "")
    )
    try:
        parsed = json.loads(content)
        return {"error": False, "parsed": parsed, "raw": content}
    except Exception:
        return {"error": False, "parsed": None, "raw": content}

def safe_score(x):
    try:
        v = float(x)
        if v < 0:
            return 0.0
        if v > 5:
            return 5.0
        return v
    except Exception:
        return None

def collect_dimension_scores(parsed):
    dims = ["structure_preservation", "instruction_following", "motion_performance"]
    out = {}
    for d in dims:
        dv = parsed.get(d) if isinstance(parsed, dict) else None
        if not isinstance(dv, dict):
            out[d] = {"overall": {"score": None, "explanation": None}, "subs": {}}
            continue
        ov = dv.get("overall") if isinstance(dv.get("overall"), dict) else {}
        o_score = safe_score(ov.get("score")) if isinstance(ov, dict) else None
        o_expl = ov.get("explanation") if isinstance(ov, dict) else None
        subs = {}
        for k, v in dv.items():
            if k == "overall":
                continue
            if isinstance(v, dict):
                subs[k] = {"score": safe_score(v.get("score")), "explanation": v.get("explanation")}
        out[d] = {"overall": {"score": o_score, "explanation": o_expl}, "subs": subs}
    return out

def aggregate_results(items):
    dims = ["structure_preservation", "instruction_following", "motion_performance"]
    agg = {d: {"scores": [], "subs": {}} for d in dims}
    for it in items:
        dim_scores = collect_dimension_scores(it)
        for d in dims:
            ov = dim_scores[d]["overall"]["score"]
            if ov is not None:
                agg[d]["scores"].append(ov)
            for sk, sv in dim_scores[d]["subs"].items():
                if sk not in agg[d]["subs"]:
                    agg[d]["subs"][sk] = []
                if sv["score"] is not None:
                    agg[d]["subs"][sk].append(sv["score"])
    result = {}
    for d in dims:
        avg = sum(agg[d]["scores"]) / len(agg[d]["scores"]) if agg[d]["scores"] else None
        subs_avg = {k: (sum(v) / len(v) if v else None) for k, v in agg[d]["subs"].items()}
        result[d] = {"average": avg, "subs_average": subs_avg}
    overall_scores = [v["average"] for v in result.values() if v["average"] is not None]
    overall = sum(overall_scores) / len(overall_scores) if overall_scores else None
    return result, overall

with st.sidebar:
    st.header("API Configuration")
    api_key_input = st.text_input("BytePlus ModelArk API Key", value=os.getenv("ARK_API_KEY", ""), type="password")
    model_id = st.text_input("Model ID", value=DEFAULT_MODEL)
    st.header("Analysis Settings")
    target_fps = st.number_input("Extraction FPS", min_value=1, max_value=24, value=12)
    max_seconds = st.number_input("Max seconds to analyze", min_value=1, max_value=120, value=10)
    decision_threshold = st.slider("Pass threshold (0-5)", min_value=0.0, max_value=5.0, value=3.5, step=0.1)

st.title("E-commerce Product Video Quality Checker")
st.markdown("Upload an AI-generated product video and the original prompt to evaluate instruction following, structure preservation, and motion performance.")

video_file = st.file_uploader("Upload video", type=["mp4", "mov", "avi", "webm"])
user_prompt = st.text_area("Initial text prompt used to generate the video")

if st.button("Analyze Video", type="primary"):
    if not video_file or not user_prompt:
        st.error("Please upload a video and enter the initial prompt.")
    elif not api_key_input:
        st.error("Please provide the BytePlus ModelArk API key.")
    else:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        tmp.write(video_file.read())
        tmp.flush()
        frames, duration = extract_frames(tmp.name, target_fps=target_fps, max_seconds=float(max_seconds))
        st.info(f"Extracted {len(frames)} frames at {target_fps} fps from {min(duration, float(max_seconds)):.2f}s")
        cols = st.columns(6)
        for i, (t, b) in enumerate(frames[:12]):
            im = Image.open(io.BytesIO(b))
            cols[i % 6].image(im, caption=f"{t:.2f}s", use_container_width=True)
        st.subheader("Per-frame Analysis")
        per_frame_container = st.container()
        progress = st.progress(0.0)
        api_results = []
        errors = []
        for i, (t, b) in enumerate(frames):
            frame_box = per_frame_container.expander(f"Frame {i+1} • {t:.2f}s")
            frame_img = Image.open(io.BytesIO(b))
            frame_box.image(frame_img, caption=f"{t:.2f}s", use_container_width=True)
            resp = call_vision_api(b, user_prompt, model_id, api_key_input, detail="high")
            if resp.get("error"):
                errors.append(resp)
                frame_box.error(f"API error {resp.get('status')}")
                frame_box.text(resp.get("body"))
            else:
                parsed = resp.get("parsed")
                api_results.append(parsed if parsed else {"raw": resp.get("raw")})
                if parsed:
                    ds = collect_dimension_scores(parsed)
                    c1, c2, c3 = frame_box.columns(3)
                    sp = ds["structure_preservation"]["overall"]["score"]
                    if sp is not None:
                        c1.metric("Structure Preservation", f"{sp:.2f}")
                    else:
                        c1.metric("Structure Preservation", "N/A")
                    inf = ds["instruction_following"]["overall"]["score"]
                    if inf is not None:
                        c2.metric("Instruction Following", f"{inf:.2f}")
                    else:
                        c2.metric("Instruction Following", "N/A")
                    mp = ds["motion_performance"]["overall"]["score"]
                    if mp is not None:
                        c3.metric("Motion Performance", f"{mp:.2f}")
                    else:
                        c3.metric("Motion Performance", "N/A")
                    frame_box.json(parsed)
                else:
                    frame_box.write("Non-JSON response")
                    frame_box.write(resp.get("raw"))
            progress.progress((i + 1) / max(1, len(frames)))
            time.sleep(0.05)
        if errors:
            st.error(f"API errors encountered: {len(errors)}. Example: {errors[0].get('body')}")
        if not api_results:
            st.warning("No results returned from the model.")
        else:
            parsed_only = [r for r in api_results if isinstance(r, dict) and "raw" not in r]
            agg, overall = aggregate_results(parsed_only)
            st.subheader("Aggregate Scores")
            c1, c2, c3 = st.columns(3)
            c1.metric("Structure Preservation", f"{agg['structure_preservation']['average']:.2f}" if agg['structure_preservation']['average'] is not None else "N/A")
            c2.metric("Instruction Following", f"{agg['instruction_following']['average']:.2f}" if agg['instruction_following']['average'] is not None else "N/A")
            c3.metric("Motion Performance", f"{agg['motion_performance']['average']:.2f}" if agg['motion_performance']['average'] is not None else "N/A")
            st.metric("Overall", f"{overall:.2f}" if overall is not None else "N/A")
            if overall is not None and overall >= decision_threshold:
                st.success("The video meets the prompt-based quality criteria.")
            else:
                st.warning("The video may not meet the quality criteria.")
            with st.expander("Detailed Dimension Analysis"):
                for dim, data in agg.items():
                    st.write(dim)
                    st.write({"average": data["average"], "subs_average": data["subs_average"]})
        os.unlink(tmp.name)
