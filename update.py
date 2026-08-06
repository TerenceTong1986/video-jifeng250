#!/usr/bin/env python3
"""
TVBox 整合源自动更新脚本
每天自动拉取上游源，去重合并，自动移除失效线路，同步国内镜像
"""

import json
import os
import re
import urllib.request
import urllib.error
import ssl
from datetime import datetime
from urllib.parse import urlparse, urlunparse

# 忽略 SSL 证书验证
ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
HEALTH_FILE = os.path.join(SCRIPT_DIR, "health_state.json")
MAX_FAILURES = 3


def encode_url(url):
    """将中文域名转为 IDNA punycode 编码，解决 urllib 无法处理中文域名的问题"""
    parsed = urlparse(url)
    if parsed.hostname and not parsed.hostname.isascii():
        encoded_host = parsed.hostname.encode("idna").decode("ascii")
        return urlunparse((parsed.scheme, encoded_host, parsed.path,
                           parsed.params, parsed.query, parsed.fragment))
    return url


def fetch_json(url, timeout=15):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    url = encode_url(url)
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ssl_ctx) as resp:
            raw = resp.read()
            data = raw.decode("utf-8", errors="ignore")
            if data.startswith("\ufeff"):
                data = data[1:]
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                lines = data.split("\n")
                clean_lines = [l for l in lines if not l.strip().startswith("//")]
                clean_data = "\n".join(clean_lines)
                try:
                    return json.loads(clean_data)
                except json.JSONDecodeError:
                    clean_data = re.sub(r'[\x00-\x1f\x7f]', '', clean_data)
                    return json.loads(clean_data)
    except Exception as e:
        print(f"  ⚠️  获取失败: {e}")
        return None


def fetch_bmp_json(url, timeout=15):
    """从 BMP 图片中提取内嵌的 base64 JSON 配置（饭太硬格式）"""
    import base64
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    url = encode_url(url)
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ssl_ctx) as resp:
            raw = resp.read()
        text = raw.decode("latin-1")
        match = re.search(r"[A-Za-z0-9+/=]{500,}", text)
        if not match:
            return None
        decoded = base64.b64decode(match.group())
        json_str = decoded.decode("utf-8", errors="ignore")
        start = json_str.find("{")
        end = json_str.rfind("}")
        if start < 0 or end <= start:
            return None
        return json.loads(json_str[start:end+1])
    except Exception as e:
        print(f"  ⚠️  获取失败: {e}")
        return None


def deduplicate_sites(sites):
    seen = {}
    for site in sites:
        key = site.get("key", "")
        if key:
            seen[key] = site
    return list(seen.values())


def load_health_state():
    try:
        with open(HEALTH_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_health_state(state):
    with open(HEALTH_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def check_source_health(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    url = encode_url(url)
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15, context=ssl_ctx) as resp:
            return resp.status == 200
    except urllib.error.HTTPError as e:
        if e.code in (301, 302, 303, 307, 308):
            return True
        return False
    except Exception:
        return False


# 线路定义：(名称, 主地址, [镜像地址列表])
LINES = [
    ("小盒子4K", "http://xhztv.top/4k.json", []),
    ("小盒子单仓", "http://xhztv.top/xhz/", []),
    ("老刘备", "https://raw.liucn.cc/box/m.json", []),
    ("小马", "https://szyyds.cn/tv/x.json", []),
    ("无名", "https://6800.kstore.vip/fish.json", []),
    ("jinenge", "https://jinenge.us.kg/app/tvbox/tvbox.json", []),
    ("摸鱼儿", "http://摸鱼儿.cc", []),
    ("肥猫", "http://肥猫.net/", []),
    ("OK影视", "https://cdn.jsdelivr.net/gh/2hacc/TVBox@main/oktv.json", [
        "https://fastly.jsdelivr.net/gh/2hacc/TVBox@main/oktv.json",
    ]),
    ("嗷呜", "http://itv666.cc/aowu/config.webp", []),
    ("VOX", "http://rihou.cc:88/demo.php", []),
    ("挺好分享多仓", "https://ztha.top/TVBox/GYCK.json", []),
    ("饭太硬(ftygit)", "https://cdn09022024.gitlink.org.cn/api/v1/repos/xxooo/in/raw/in.bmp", []),
    ("饭太硬(官方)", "http://www.饭太硬.cc/tv", []),
    ("王二小", "http://new.王二小放牛娃.top", []),
    ("小盒子多仓", "http://xhztv.top/dc", []),
    ("拾光多仓", "http://xmbjm.fh4u.org/dc.txt", []),
]

# 上游数据源（从中拉取 sites）
UPSTREAM_SOURCES = [
    ("老刘备", "https://raw.liucn.cc/box/m.json"),
    ("小马", "https://szyyds.cn/tv/x.json"),
    ("无名", "https://6800.kstore.vip/fish.json"),
    ("jinenge", "https://jinenge.us.kg/app/tvbox/tvbox.json"),
    ("小盒子4K", "http://xhztv.top/4k.json"),
    ("小盒子单仓", "http://xhztv.top/xhz/"),
    ("OK影视", "https://cdn.jsdelivr.net/gh/2hacc/TVBox@main/oktv.json"),
    ("VOX", "http://rihou.cc:88/demo.php"),
    ("饭太硬", "https://cdn09022024.gitlink.org.cn/api/v1/repos/xxooo/in/raw/in.bmp"),
]


def main():
    print("=" * 50)
    print("📺 TVBox 源自动更新工具")
    print(f"⏰ 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    # 1. 健康检查 + 自动移除
    print(f"\n🔍 健康检查（连续{MAX_FAILURES}次失败自动移除）...")
    health_state = load_health_state()
    active_lines = []
    removed_lines = []

    for name, url, mirrors in LINES:
        ok = check_source_health(url)
        if ok:
            print(f"  ✅ {name} — 正常")
            health_state[url] = 0
            active_lines.append((name, url, mirrors))
        else:
            fail_count = health_state.get(url, 0) + 1
            health_state[url] = fail_count
            if fail_count >= MAX_FAILURES:
                print(f"  ❌ {name} — 连续 {fail_count} 次失败，已移除")
                removed_lines.append(name)
            else:
                print(f"  ⚠️  {name} — 第 {fail_count}/{MAX_FAILURES} 次失败，保留")
                active_lines.append((name, url, mirrors))

    save_health_state(health_state)
    if removed_lines:
        print(f"\n  🗑️  本次移除: {', '.join(removed_lines)}")
    print(f"  📊 活跃线路: {len(active_lines)} 个")

    # 2. 生成 urls.json（主地址 + 镜像地址）
    print("\n📋 生成多仓配置 (urls.json)...")
    urls = []
    for name, url, mirrors in active_lines:
        urls.append({"name": f"⭐{name}", "url": url})
        for i, mirror in enumerate(mirrors):
            urls.append({"name": f"🪞{name}镜像{i+1}", "url": mirror})

    # 通用国内镜像入口
    urls.append({"name": "🪞GitHub镜像(kgithub)", "url": "https://raw.kkgithub.com/jifeng250/tvbox-sources/main/tvbox.json"})
    urls.append({"name": "🪞GitHub镜像(jsdelivr)", "url": "https://fastly.jsdelivr.net/gh/jifeng250/tvbox-sources@main/tvbox.json"})

    urls_data = {"urls": urls}
    urls_path = os.path.join(SCRIPT_DIR, "urls.json")
    with open(urls_path, "w", encoding="utf-8") as f:
        json.dump(urls_data, f, ensure_ascii=False, indent=2)
    print(f"   ✅ 已生成 {len(urls)} 个线路（含镜像）")

    # 3. 拉取上游站点数据
    print("\n🔄 从上游源拉取站点数据...")
    all_sites = []
    total_sites = 0
    success_count = 0

    for name, url in UPSTREAM_SOURCES:
        print(f"  📥 正在获取 {name}...", end=" ")
        data = fetch_json(url)
        if data is None and "bmp" in url:
            print("重试 BMP 解析...", end=" ")
            data = fetch_bmp_json(url)
        if data and "sites" in data:
            sites = data["sites"]
            all_sites.extend(sites)
            total_sites += len(sites)
            success_count += 1
            print(f"✅ 获取 {len(sites)} 个站点")
        else:
            print("❌ 失败")

    print(f"\n  📊 共获取 {total_sites} 个站点（来自 {success_count}/{len(UPSTREAM_SOURCES)} 个源）")

    # 4. 去重
    deduped = deduplicate_sites(all_sites)
    print(f"  📊 去重后剩余 {len(deduped)} 个站点")

    # 5. 生成 tvbox.json
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tvbox_data = {
        "spider": "",
        "wallpaper": "https://raw.githubusercontent.com/jifeng250/tvbox-sources/main/wallpaper.jpg",
        "updateTime": now,
        "warningText": "资源来自网络，仅供学习交流使用，请勿用于商业用途。",
        "sites": deduped,
    }

    tvbox_path = os.path.join(SCRIPT_DIR, "tvbox.json")
    with open(tvbox_path, "w", encoding="utf-8") as f:
        json.dump(tvbox_data, f, ensure_ascii=False, indent=2)
    print(f"\n  ✅ 已生成 tvbox.json（{len(deduped)} 个站点）")

    print("\n" + "=" * 50)
    print("✅ 更新完成！")
    print("=" * 50)


if __name__ == "__main__":
    main()