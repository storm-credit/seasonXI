"""
SeasonXI: 자동 영상 렌더링

Usage:
    # 메시 2011-12 렌더링
    python scripts/render_video.py messi_2011_12

    # 전체 ready 상태 렌더링
    python scripts/render_video.py --all

    # 특정 선수만
    python scripts/render_video.py --player messi
"""

import subprocess
import json
import sys
from pathlib import Path

PROJECT = Path(__file__).parent.parent
REMOTION_DIR = PROJECT / "remotion"
DATA_DIR = REMOTION_DIR / "public" / "data"
OUTPUT_DIR = PROJECT / "outputs" / "videos"


def render_one(json_name: str):
    """JSON 파일 하나로 영상 렌더링"""
    json_path = DATA_DIR / f"{json_name}.json"
    if not json_path.exists():
        print(f"  SKIP  {json_name}: JSON not found")
        return False

    data = json.loads(json_path.read_text(encoding="utf-8"))

    # 이미지 있는지 확인
    main_img = data.get("assets", {}).get("image_main", "")
    if not main_img:
        print(f"  SKIP  {json_name}: no image_main (generate in nanobanana first)")
        return False

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / f"{json_name}.mp4"

    print(f"  RENDER  {json_name} → {out_path.name}")

    # Remotion render with props
    props = json.dumps({"data": {"src": f"{json_name}.json"}})
    cmd = [
        "npx", "remotion", "render", "SeasonCard",
        f"--output={out_path}",
        f"--props={props}",
    ]

    result = subprocess.run(cmd, cwd=REMOTION_DIR, capture_output=True, text=True)

    if result.returncode == 0:
        size_mb = out_path.stat().st_size / 1024 / 1024
        print(f"  OK    {out_path.name} ({size_mb:.1f} MB)")
        return True
    else:
        print(f"  ERR   {json_name}: {result.stderr[-200:]}")
        return False


def main():
    args = sys.argv[1:]

    if not args:
        print("Usage:")
        print("  python scripts/render_video.py messi_2011_12")
        print("  python scripts/render_video.py --all")
        print("  python scripts/render_video.py --player messi")
        return

    if args[0] == "--all":
        jsons = sorted(DATA_DIR.glob("*.json"))
        print(f"Found {len(jsons)} JSON files\n")
        ok = 0
        for j in jsons:
            if render_one(j.stem):
                ok += 1
        print(f"\nRendered: {ok}/{len(jsons)}")

    elif args[0] == "--player":
        player = args[1]
        jsons = sorted(DATA_DIR.glob(f"{player}_*.json"))
        print(f"Found {len(jsons)} JSON files for {player}\n")
        for j in jsons:
            render_one(j.stem)

    else:
        render_one(args[0])


if __name__ == "__main__":
    main()
