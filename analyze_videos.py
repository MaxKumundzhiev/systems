"""
Analyze video pairs: duration, FPS, pairwise diffs, prompt stats.
Uses ffprobe via subprocess — reads metadata without downloading full videos.
"""

import json
import subprocess
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed


def get_video_metadata(url: str) -> dict:
    cmd = [
        "ffprobe",
        "-v",
        "quiet",
        "-print_format",
        "json",
        "-show_streams",
        url,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        streams = json.loads(result.stdout).get("streams", [])
        video = next((s for s in streams if s["codec_type"] == "video"), None)
        if not video:
            return {
                "url": url,
                "duration_s": None,
                "fps": None,
                "error": "no video stream",
            }

        duration = float(video.get("duration") or 0)

        num, den = map(int, video.get("avg_frame_rate", "0/1").split("/"))
        fps = round(num / den, 4) if den else 0.0

        return {"url": url, "duration_s": round(duration, 4), "fps": fps, "error": None}

    except Exception as exc:
        return {"url": url, "duration_s": None, "fps": None, "error": str(exc)}


def analyze(pairs: list[dict]) -> dict:
    urls = [url for p in pairs for url in (p["video_a"], p["video_b"])]
    meta: dict[str, dict] = {}

    with ThreadPoolExecutor(max_workers=20) as pool:
        futures = {pool.submit(get_video_metadata, u): u for u in urls}
        for fut in as_completed(futures):
            meta[futures[fut]] = fut.result()

    all_durations = [
        m["duration_s"] for m in meta.values() if m["duration_s"] is not None
    ]
    all_fps = [m["fps"] for m in meta.values() if m["fps"] is not None]

    pairwise = []
    for p in pairs:
        ma, mb = meta[p["video_a"]], meta[p["video_b"]]
        da, db = ma["duration_s"], mb["duration_s"]
        fa, fb = ma["fps"], mb["fps"]
        pairwise.append(
            {
                "video_a": p["video_a"].split("/")[-1],
                "video_b": p["video_b"].split("/")[-1],
                "duration_a_s": da,
                "duration_b_s": db,
                "duration_diff_s": (
                    round(abs(da - db), 4)
                    if da is not None and db is not None
                    else None
                ),
                "fps_a": fa,
                "fps_b": fb,
                "fps_diff": (
                    round(abs(fa - fb), 4)
                    if fa is not None and fb is not None
                    else None
                ),
            }
        )

    unique_fps = sorted(set(all_fps))
    unique_durations = sorted(set(all_durations))

    return {
        "summary": {
            "total_videos": len(meta),
            "total_pairs": len(pairs),
            "avg_duration_s": (
                round(statistics.mean(all_durations), 4) if all_durations else None
            ),
            "avg_prompt_length_words": round(
                statistics.mean(len(p["prompt"].split()) for p in pairs), 2
            ),
            "fps_uniform": len(unique_fps) == 1,
            "unique_fps_values": unique_fps,
            "unique_duration_values_s": unique_durations,
            "pairs_with_duration_diff": sum(
                1 for p in pairwise if p["duration_diff_s"] and p["duration_diff_s"] > 0
            ),
            "pairs_with_fps_diff": sum(
                1 for p in pairwise if p["fps_diff"] and p["fps_diff"] > 0
            ),
        },
        "pairwise": pairwise,
    }


if __name__ == "__main__":
    d: list[dict] = []  # add the list of videos
    result = analyze(d)
    print(json.dumps(result, indent=2))
