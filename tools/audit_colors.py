# -*- coding: utf-8 -*-
"""渲染结果配色审计：统计截图中「有色像素」的饱和度分布。

用途：
  1. 验证成品页面确实是「多彩（有色像素占比不为 0）且低饱和度（高饱和像素占比极低）」；
  2. 可与其他参考图对比（如用户提供的设计截图），量化风格差异。

用法：python tools/audit_colors.py 图片或目录 [更多路径...]
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image

MAX_SIDE = 900  # 采样缩放上限，保证速度


def audit(path: Path, bands: int = 0) -> dict:
    im = Image.open(path).convert("RGB")
    w, h = im.size
    if max(w, h) > MAX_SIDE:
        scale = MAX_SIDE / max(w, h)
        im = im.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.Resampling.LANCZOS)
    arr = np.asarray(im).astype(np.float32) / 255.0
    mx, mn = arr.max(axis=2), arr.min(axis=2)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0.0)

    tinted = sat > 0.05            # 有色彩倾向的像素（含浅粉彩底）
    chromatic = sat > 0.10         # 明显「有色」的像素
    vivid = sat > 0.60             # 高饱和像素（应尽量少）
    if chromatic.any():
        # 有色像素的色相覆盖
        hues = []
        import colorsys
        ys, xs = np.where(chromatic)
        step = max(1, len(ys) // 4000)
        for y, x in zip(ys[::step], xs[::step]):
            r, g, b = arr[y, x]
            hues.append(colorsys.rgb_to_hsv(float(r), float(g), float(b))[0] * 360)
        hues = np.array(hues)
        hist, _ = np.histogram(hues, bins=12, range=(0, 360))
        occupied = int((hist > len(hues) * 0.01).sum())
    else:
        occupied = 0

    band_info: list[float] = []
    if bands > 0:
        for i in range(bands):
            y0, y1 = int(i * sat.shape[0] / bands), int((i + 1) * sat.shape[0] / bands)
            band_info.append(float((sat[y0:y1] > 0.05).mean()))

    return {
        "path": path,
        "size": (w, h),
        "tinted_ratio": float(tinted.mean()),
        "chromatic_ratio": float(chromatic.mean()),
        "median_sat_chromatic": float(np.median(sat[chromatic])) if chromatic.any() else 0.0,
        "vivid_ratio": float(vivid.mean()),
        "hue_bins_occupied": occupied,
        "bands": band_info,
    }


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2

    args = sys.argv[1:]
    bands = 0
    if "--bands" in args:
        idx = args.index("--bands")
        bands = int(args[idx + 1])
        del args[idx:idx + 2]

    targets: list[Path] = []
    for arg in args:
        p = Path(arg)
        if p.is_dir():
            targets += sorted(p.glob("*.png")) + sorted(p.glob("*.jpg"))
        else:
            targets.append(p)

    print(f"{'文件':<20}{'尺寸':<13}{'有色倾向(>0.05)':<16}{'明显有色(>0.10)':<16}"
          f"{'有色中位饱和':<13}{'高饱和(>0.6)':<12}{'色相覆盖/12'}")
    print("-" * 104)
    for t in targets:
        if not t.exists():
            print(f"{t.name:<20}不存在")
            continue
        r = audit(t, bands=bands)
        print(f"{t.name:<20}{str(r['size']):<13}{r['tinted_ratio']:>9.1%}       "
              f"{r['chromatic_ratio']:>9.1%}       {r['median_sat_chromatic']:>8.3f}     "
              f"{r['vivid_ratio']:>8.2%}    {r['hue_bins_occupied']:>2} 个")
        if r["bands"]:
            seg = "  ".join(f"{i + 1}:{b:.0%}" for i, b in enumerate(r["bands"]))
            print(f"{'':<20}分段有色占比 → {seg}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
