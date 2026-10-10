# -*- coding: utf-8 -*-
"""生成网站调色板：统一 S/L、只变化色相的「鲜艳但低饱和度」配色。

产物（自动生成，不要手改）：
  assets/css/palette.css   -> CSS 变量 --c1..--c8 及 soft/deep 变体
  assets/js/palette.js     -> window.PALETTE，供 ECharts 图表使用

设计约束（可被 tests/test_site.py 自动校验）：
  * 所有彩色 S <= 60%（低饱和）        -> 观察上柔和、不刺眼
  * 8 个色相在色环上跨越 >= 300°        -> 观察上依然「多彩、鲜艳」
  * 每个色相统一用同一组 (S, L)         -> 视觉协调、专业
"""
from __future__ import annotations

import colorsys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# 色相环上均匀铺开的 8 个色相（玫瑰粉→珊瑚橙→琥珀金→薄荷绿→湖蓝→靛蓝→薰衣草→紫罗兰）
HUES = [352, 22, 36, 168, 197, 225, 265, 292]
NAMES = ["玫瑰粉", "珊瑚橙", "琥珀金", "薄荷绿", "湖蓝", "靛蓝", "薰衣草", "紫罗兰"]

MAIN = (0.52, 0.63)   # 主色：中等明度，白底可读、图形填充柔和
SOFT = (0.58, 0.92)   # 浅色：卡片底、面积图填充
DEEP = (0.48, 0.42)   # 深色：文字、描边、强调

# 中性色（背景/文字/线条），与彩色的低饱和度气质保持统一
NEUTRALS = {
    "--bg": "#F7F8FA",
    "--bg-warm": "#FBF9F7",
    "--card": "#FFFFFF",
    "--ink": "#323A4D",
    "--ink-2": "#6B7280",
    "--ink-3": "#9CA3AF",
    "--line": "#E8EAF0",
    "--shadow": "0 10px 30px rgba(50, 58, 77, .07)",
}


def hsl_hex(h_deg: float, s: float, l: float) -> str:
    r, g, b = colorsys.hls_to_rgb(h_deg / 360.0, l, s)
    return "#%02X%02X%02X" % (round(r * 255), round(g * 255), round(b * 255))


def build() -> tuple[str, str]:
    series, soft, deep, hsl_tokens = [], [], [], []
    for i, h in enumerate(HUES, start=1):
        series.append(hsl_hex(h, *MAIN))
        soft.append(hsl_hex(h, *SOFT))
        deep.append(hsl_hex(h, *DEEP))
        hsl_tokens.append(
            f"  --c{i}-hsl: {h} {int(MAIN[0] * 100)}% {int(MAIN[1] * 100)}%;"
        )

    lines = [
        "/* 自动生成：tools/make_palette.py —— 请勿手改 */",
        ":root {",
        "  /* 多彩低饱和主色（统一 S=52% L=63%，仅色相变化） */",
    ]
    for i, (name, c, s, d) in enumerate(zip(NAMES, series, soft, deep), start=1):
        lines.append(f"  --c{i}: {c};        /* {name} */")
        lines.append(f"  --c{i}-soft: {s};")
        lines.append(f"  --c{i}-deep: {d};")
    lines += ["", "  /* 主色 HSL 分量，便于插图用 hsl() 微调透明度 */"]
    lines += hsl_tokens
    lines += ["", "  /* 中性色 */"]
    lines += [f"  {k}: {v};" for k, v in NEUTRALS.items()]
    lines.append("}")
    css = "\n".join(lines) + "\n"

    js = (
        "/* 自动生成：tools/make_palette.py —— 请勿手改 */\n"
        "window.PALETTE = "
        + json.dumps(
            {
                "names": NAMES,
                "series": series,
                "soft": soft,
                "deep": deep,
                "hues": HUES,
                "mainSL": {"s": int(MAIN[0] * 100), "l": int(MAIN[1] * 100)},
            },
            ensure_ascii=False,
            indent=2,
        )
        + ";\n"
    )
    return css, js


def main() -> None:
    css, js = build()
    (ROOT / "assets" / "css").mkdir(parents=True, exist_ok=True)
    (ROOT / "assets" / "js").mkdir(parents=True, exist_ok=True)
    (ROOT / "assets" / "css" / "palette.css").write_text(css, encoding="utf-8")
    (ROOT / "assets" / "js" / "palette.js").write_text(js, encoding="utf-8")

    print("palette.css / palette.js 已生成")
    for h, name in zip(HUES, NAMES):
        print(f"  {name:4s} H={h:3d}  main={hsl_hex(h, *MAIN)}  soft={hsl_hex(h, *SOFT)}  deep={hsl_hex(h, *DEEP)}")


if __name__ == "__main__":
    main()
