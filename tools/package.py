# -*- coding: utf-8 -*-
"""生成交付物：docs/screenshots（文档配图）+ 源码压缩包。

用法：python tools/package.py
前置：先运行 python tools/check_pages.py --shots 生成整页截图
"""
from __future__ import annotations

import zipfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SHOTS = ROOT / ".reasonix" / "scratch" / "screenshots"
DOCS = ROOT / "docs" / "screenshots"
ZIP_PATH = ROOT / "AI-新质生产力-网站源码.zip"

INCLUDE_DIRS = ["assets", "vendor", "tools", "tests", "docs"]
INCLUDE_FILES = ["index.html", "scale.html", "industry.html", "labor.html", "future.html", "social.html", "README.md"]
EXCLUDE_DIRS = {"__pycache__", ".reasonix", ".pytest_cache"}
SHOT_WHITELIST = {"index.png", "scale.png", "industry.png", "labor.png", "future.png", "social.png"}
SHOT_STEMS = {Path(name).stem for name in SHOT_WHITELIST}


def export_shots() -> None:
    if not SHOTS.exists():
        raise SystemExit(
            "[FAIL] 缺少截图目录 .reasonix/scratch/screenshots\n"
            "       请先运行：python tools/check_pages.py --shots"
        )
    # 先确认截图齐全再动既有配图（否则会在报错前破坏 docs/screenshots）
    absent = sorted(SHOT_WHITELIST - {p.name for p in SHOTS.glob("*.png")})
    if absent:
        raise SystemExit(
            f"[FAIL] 整页截图不完整，缺少：{absent}\n"
            "       请重新运行：python tools/check_pages.py --shots"
        )

    DOCS.mkdir(parents=True, exist_ok=True)
    for old in DOCS.glob("*.jpg"):          # 先清理本站历史配图，避免旧图被打进交付包
        if old.stem not in SHOT_STEMS:
            continue
        try:
            old.unlink()
        except OSError:
            pass
    for png in sorted(SHOTS.glob("*.png")):
        if png.name not in SHOT_WHITELIST:
            print(f"跳过非站点截图: {png.name}")
            continue
        im = Image.open(png).convert("RGB")
        w, h = im.size
        if w > 1200:
            im = im.resize((1200, int(h * 1200 / w)), Image.Resampling.LANCZOS)
        out = DOCS / (png.stem + ".jpg")
        im.save(out, quality=80, optimize=True)
        print(f"配图 -> docs/screenshots/{out.name}  ({out.stat().st_size // 1024} KB)")


def iter_files():
    for name in INCLUDE_FILES:
        p = ROOT / name
        if p.exists():
            yield p, p.name
    for d in INCLUDE_DIRS:
        base = ROOT / d
        if not base.exists():
            continue
        for p in sorted(base.rglob("*")):
            if not p.is_file():
                continue
            if any(part in EXCLUDE_DIRS for part in p.parts):
                continue
            yield p, p.relative_to(ROOT).as_posix()


def make_zip() -> None:
    files = list(iter_files())
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path, arcname in files:
            zf.write(path, arcname)
    total = ZIP_PATH.stat().st_size
    print(f"\n压缩包 -> {ZIP_PATH.name}")
    print(f"  包含 {len(files)} 个文件，{total / 1024 / 1024:.2f} MB")
    print(f"  解压后打开 index.html 即可离线浏览")


def main() -> None:
    export_shots()
    make_zip()


if __name__ == "__main__":
    main()
