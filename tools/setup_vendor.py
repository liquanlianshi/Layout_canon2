# -*- coding: utf-8 -*-
"""下载站点所需的第三方库到本地 vendor/，保证离线可用，并记录 sha256 清单。

产物：
  vendor/echarts.min.js            ECharts 5 图表库
  vendor/echarts-wordcloud.min.js  词云扩展
  vendor/china-map.js              中国地图 GeoJSON（包装为 window.CHINA_GEOJSON）
  vendor/SOURCES.json              url + sha256 清单（供应链校验用）

用法：
  python tools/setup_vendor.py            下载缺失文件；已存在则比对清单哈希。
                                          不一致或未登记时告警、退出码 1，
                                          且该条目保留原基准（其它条目照常更新）
  python tools/setup_vendor.py --accept   确认无误后刷新/建立清单基准（人工核实后使用）
  python tools/setup_vendor.py --verify   联网重新下载并逐项比对哈希（只读，不写任何文件）
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "vendor"
MANIFEST = VENDOR / "SOURCES.json"

SOURCES = {
    "echarts.min.js": "https://cdn.jsdelivr.net/npm/echarts@5.5.1/dist/echarts.min.js",
    "echarts-wordcloud.min.js": "https://cdn.jsdelivr.net/npm/echarts-wordcloud@2.1.0/dist/echarts-wordcloud.min.js",
}
CHINA_GEOJSON = "https://cdn.jsdelivr.net/npm/echarts@4.9.0/map/json/china.json"
CHINA_NAME = "china.json"

GEO_PATTERN = re.compile(r"window\.CHINA_GEOJSON\s*=\s*(\{.*\})\s*;\s*$", re.S)


def fetch(url: str) -> bytes:
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    return resp.content


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(payload: bytes) -> bytes:
    """JSON 规范化（键序排序 + 紧凑分隔符），让不同来源的等价内容可比对。"""
    return json.dumps(json.loads(payload), ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode()


def local_china_payload() -> bytes:
    """从 vendor/china-map.js 中提取被包裹的 GeoJSON 主体。"""
    path = VENDOR / "china-map.js"
    if not path.exists():
        raise RuntimeError(f"缺少 {path.relative_to(ROOT)}，请先运行 python tools/setup_vendor.py")
    match = GEO_PATTERN.search(path.read_text(encoding="utf-8"))
    if not match:
        raise RuntimeError("vendor/china-map.js 结构异常：未找到 window.CHINA_GEOJSON = {…};")
    return match.group(1).encode("utf-8")


def load_manifest() -> dict:
    if MANIFEST.exists():
        return json.loads(MANIFEST.read_text(encoding="utf-8"))
    return {}


def save_manifest(data: dict) -> None:
    MANIFEST.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def verify() -> int:
    """联网逐项比对本地文件与上游 CDN 内容是否一致。"""
    print("开始校验 vendor 依赖与上游 CDN 的一致性……")
    try:
        return _verify_inner()
    except (requests.RequestException, ValueError) as exc:
        print(f"[ERROR] 联网校验失败（网络或上游响应异常）：{exc}")
        return 1


def _verify_inner() -> int:
    ok = True
    for name, url in SOURCES.items():
        local_path = VENDOR / name
        if not local_path.exists():
            print(f"[MISSING]  {name:26s} 本地文件不存在，请先运行 python tools/setup_vendor.py")
            ok = False
            continue
        remote = fetch(url)
        local = local_path.read_bytes()
        same = sha256(local) == sha256(remote)
        ok &= same
        print(f"{'[MATCH]   ' if same else '[MISMATCH]'} {name:26s} sha256={sha256(local)[:16]}…  ← {url}")

    try:
        local_geo = canonical(local_china_payload())
    except RuntimeError as exc:
        print(f"[MISSING]  {'china-map.js (GeoJSON)':26s} {exc}")
        return 1
    remote_geo = canonical(fetch(CHINA_GEOJSON))
    same = sha256(local_geo) == sha256(remote_geo)
    ok &= same
    print(f"{'[MATCH]   ' if same else '[MISMATCH]'} {'china-map.js (GeoJSON)':26s} "
          f"sha256={sha256(local_geo)[:16]}…  ← {CHINA_GEOJSON}")
    print("结论：" + ("全部一致，vendor 依赖与上游字节级相同" if ok else "存在不一致，请重新下载"))
    return 0 if ok else 1


def _finish(manifest: dict, mismatches: list[str], accepted: bool) -> int:
    save_manifest(manifest)
    print(f"清单已写入 {MANIFEST.relative_to(ROOT)}")
    if mismatches and not accepted:
        print(f"\n[warn] {len(mismatches)} 个文件与清单不一致或尚未登记：{', '.join(mismatches)}")
        print("       请人工核实来源（可运行 --verify 联网比对）；确认无误后运行 "
              "python tools/setup_vendor.py --accept 刷新基准")
        return 1
    if mismatches:
        print(f"[note] 已按 --accept 刷新/建立 {len(mismatches)} 个文件的清单基准：{', '.join(mismatches)}")
    return 0


def main() -> int:
    if "--verify" in sys.argv:
        return verify()

    accept = "--accept" in sys.argv
    VENDOR.mkdir(parents=True, exist_ok=True)
    manifest = load_manifest()
    mismatches: list[str] = []

    for name, url in SOURCES.items():
        dest = VENDOR / name
        if dest.exists() and dest.stat().st_size > 10_000:
            digest = sha256(dest.read_bytes())
            rec = manifest.get(name, {}).get("sha256")
            if rec and rec != digest:
                mismatches.append(name)
                print(f"[warn] {name} 与清单不一致！ 本地 sha256={digest[:16]}… 清单={rec[:16]}…")
                if not accept:
                    print("       保留原清单不动，请人工核实")
                    continue
                print("       --accept 已指定：刷新该文件清单基准")
            elif not rec:
                mismatches.append(name)
                print(f"[warn] {name} 已存在但清单无记录（可能被替换或首次引入） sha256={digest[:16]}…")
                if not accept:
                    print("       不自动登记，请人工核实后运行 --accept 建立基准")
                    continue
                print("       --accept 已指定：建立该文件清单基准")
            else:
                print(f"[skip] {name} 已存在 ({dest.stat().st_size} bytes)  sha256={digest[:16]}…  与清单一致")
            manifest[name] = {"url": url, "sha256": digest}
            continue
        data = fetch(url)
        if len(data) < 10_000:
            raise RuntimeError(f"{name} 下载内容过小，可能失败: {len(data)} bytes")
        dest.write_bytes(data)
        manifest[name] = {"url": url, "sha256": sha256(data)}
        print(f"[ok]   {name}  {len(data)} bytes  sha256={sha256(data)[:16]}…")

    geo_dest = VENDOR / "china-map.js"
    if geo_dest.exists() and geo_dest.stat().st_size > 10_000:
        print(f"[skip] china-map.js 已存在 ({geo_dest.stat().st_size} bytes)")
    else:
        geo = json.loads(fetch(CHINA_GEOJSON))
        if "features" not in geo or len(geo["features"]) < 30:
            raise RuntimeError("china.json 结构异常")
        geo_dest.write_text(
            "/* 自动生成：tools/setup_vendor.py —— ECharts 4.9.0 官方地图数据（含十段线） */\n"
            "window.CHINA_GEOJSON = " + json.dumps(geo, ensure_ascii=False, separators=(",", ":")) + ";\n",
            encoding="utf-8",
        )
        print(f"[ok]   china-map.js  {len(geo['features'])} 个省级要素  {geo_dest.stat().st_size} bytes")

    canonical_digest = sha256(canonical(local_china_payload()))
    rec = manifest.get(CHINA_NAME, {}).get("canonical_sha256")
    if rec != canonical_digest:
        mismatches.append(CHINA_NAME)
        if rec:
            print(f"[warn] china-map.js 内容与清单不一致！ 本地={canonical_digest[:16]}… 清单={rec[:16]}…")
        else:
            print(f"[warn] china-map.js 已存在但清单无记录（可能被替换或首次引入） 本地={canonical_digest[:16]}…")
        if not accept:
            print("       保留原清单不动，请人工核实")
            return _finish(manifest, mismatches, accepted=False)
        print("       --accept 已指定：刷新/建立该文件清单基准")
    manifest[CHINA_NAME] = {
        "url": CHINA_GEOJSON,
        "canonical_sha256": canonical_digest,
        "note": "vendor/china-map.js 中包裹的 GeoJSON（规范化后）的 sha256，供 --verify 与人工核对",
    }
    return _finish(manifest, mismatches, accepted=accept)


if __name__ == "__main__":
    raise SystemExit(main())
