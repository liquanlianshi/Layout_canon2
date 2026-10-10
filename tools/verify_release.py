# -*- coding: utf-8 -*-
"""交付验收：把源码压缩包解压到干净目录，核对清单、内容一致性与安全性。

用途：模拟「老师收到 zip → 解压 → 使用」的完整路径，证明交付包：
  1) 自包含（含 vendor 依赖、测试与工具，无需工作目录残留文件）；
  2) 与工作区源码逐字节一致（sha256，防同名替换/内容篡改）；
  3) 应包含集合与实际包含集合完全一致（防漏打/多打）；
  4) 不含 .reasonix / .pytest_cache / __pycache__ / 压缩包自身。

用法：
  python tools/verify_release.py     # 解压到 .reasonix/scratch/acceptance 并核对
  # 随后在解压目录中独立验收：
  #   cd .reasonix/scratch/acceptance
  #   python -m pytest tests/ -q
  #   python tools/check_pages.py
"""
from __future__ import annotations

import hashlib
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZIP_PATH = ROOT / "AI-新质生产力-网站源码.zip"
DEST = ROOT / ".reasonix" / "scratch" / "acceptance"

FORBIDDEN_PARTS = {".reasonix", ".pytest_cache", "__pycache__"}

# 关键文件：即使集合比对通过，也要求它们必须存在（失败信息更直白）
REQUIRED = [
    "index.html", "scale.html", "industry.html", "labor.html", "future.html", "social.html",
    "README.md",
    "assets/css/main.css", "assets/css/palette.css",
    "assets/js/site.js", "assets/js/palette.js", "assets/js/hero-network.js",
    "assets/js/charts-home.js", "assets/js/charts-scale.js",
    "assets/js/charts-industry.js", "assets/js/charts-labor.js",
    "assets/js/charts-future.js", "assets/js/charts-social.js",
    "vendor/echarts.min.js", "vendor/echarts-wordcloud.min.js",
    "vendor/china-map.js", "vendor/SOURCES.json",
    "tests/test_site.py",
    "tools/check_pages.py", "tools/setup_vendor.py", "tools/package.py",
    "tools/make_palette.py", "tools/audit_colors.py", "tools/verify_release.py",
    "tools/preview.py", "tools/make_report.py",
    "docs/screenshots/index.jpg", "docs/screenshots/scale.jpg",
    "docs/screenshots/industry.jpg", "docs/screenshots/labor.jpg",
    "docs/screenshots/future.jpg", "docs/screenshots/social.jpg",
    "docs/亮点说明.pdf", "docs/亮点说明.html",
]


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def member_is_safe(name: str) -> bool:
    """拒绝绝对路径 / 盘符 / 反斜杠 / 上跳成员名（zip-slip 防护，不依赖库的私有行为）。"""
    if not name:
        return False
    if name.startswith(("/", "\\")) or ":" in name or "\\" in name:
        return False
    return ".." not in name.split("/")


def expected_entries() -> set[str] | None:
    """复用打包脚本的白名单，得出「应包含文件集合」；导入失败时返回 None。"""
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        import package  # noqa: PLC0415

        return {arcname for _path, arcname in package.iter_files()}
    except Exception as exc:  # noqa: BLE001
        print(f"[warn] 无法导入打包脚本（{type(exc).__name__}: {exc}），将跳过「应包含集合」比对")
        return None


def main() -> int:
    if not ZIP_PATH.exists():
        print(f"缺少压缩包：{ZIP_PATH.name}（请先运行 python tools/package.py）")
        return 1

    # ---- 目录安全：验收目录必须位于仓库内，且是普通目录 ----
    if not DEST.resolve().is_relative_to(ROOT):
        print(f"[FAIL] 验收目录越出项目范围：{DEST}")
        return 1
    if DEST.exists():
        if DEST.is_symlink() or not DEST.is_dir():
            print(f"[FAIL] 验收目录不是普通目录：{DEST}")
            return 1
        try:
            shutil.rmtree(DEST)
        except OSError as exc:
            print(f"[FAIL] 无法清空验收目录（可能被占用）：{exc}")
            return 1
    try:
        DEST.mkdir(parents=True)
    except OSError as exc:
        print(f"[FAIL] 无法创建验收目录：{exc}")
        return 1

    # ---- 解压前先校验成员名，再解压 ----
    with zipfile.ZipFile(ZIP_PATH) as zf:
        bad = zf.testzip()
        if bad:
            print(f"[FAIL] 压缩包内文件损坏：{bad}")
            return 1
        unsafe = [name for name in zf.namelist() if not member_is_safe(name)]
        if unsafe:
            print(f"[FAIL] 压缩包含不安全成员名（绝对路径/上跳/盘符）：{unsafe[:5]}")
            return 1
        zf.extractall(DEST)

    files = [p for p in DEST.rglob("*") if p.is_file()]
    print(f"解压完成：{len(files)} 个文件 → {DEST.relative_to(ROOT)}")

    # ---- 1) 关键文件存在 ----
    missing = [name for name in REQUIRED if not (DEST / name).is_file()]
    if missing:
        print(f"[FAIL] 缺少必需文件：{missing}")
        return 1

    # ---- 2) 无不该交付的内容 ----
    leaked = [p.relative_to(DEST).as_posix() for p in files
              if FORBIDDEN_PARTS & set(p.relative_to(DEST).parts)
              or p.suffix.lower() == ".zip"]
    if leaked:
        print(f"[FAIL] 包内混入不该交付的内容：{leaked}")
        return 1

    # ---- 3) 应包含集合与实际包含集合一致（防漏打/多打） ----
    expected = expected_entries()
    actual = {p.relative_to(DEST).as_posix() for p in files}
    if expected is not None and expected != actual:
        only_zip = sorted(expected - actual)
        only_work = sorted(actual - expected)
        print("[FAIL] 打包集合与工作区白名单不一致：")
        print(f"      包内缺少: {only_zip[:8]}")
        print(f"      包内多出: {only_work[:8]}")
        return 1

    # ---- 4) 逐字节一致性（防同名替换 / 内容篡改） ----
    drift = []
    for p in files:
        rel = p.relative_to(DEST)
        src = ROOT / rel
        if not src.is_file() or sha256_of(src) != sha256_of(p):
            drift.append(rel.as_posix())
    if drift:
        print(f"[FAIL] 以下文件与工作区源码不一致（可能被打包后替换）：{drift}")
        return 1
    print(f"内容一致性：{len(files)} 个文件全部与工作区源码逐字节相同（sha256）")

    print("下一步（在解压目录中独立验收）：")
    print(f"  cd {DEST.relative_to(ROOT)}")
    print("  python -m pytest tests/ -q     # 结构 / 资源 / 图表绑定 / 配色规范")
    print("  python tools/check_pages.py    # 浏览器逐页渲染（需 playwright）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
