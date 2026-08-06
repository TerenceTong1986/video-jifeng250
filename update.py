#!/usr/bin/env python3
"""
TVBox 整合源自动更新脚本
每天自动拉取上游源，去重合并，生成最新的 tvbox.json 和 urls.json
"""

import json
import hashlib
import os
import sys
import urllib.request
import urllib.error
import ssl
from datetime import datetime

# 忽略 SSL 证书验证（某些源可能是自签名证书）
ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def fetch_json(url, timeout=15):
    """获取远程 JSON 数据"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ssl_ctx) as resp:
            data = resp.read().decode("utf-8", errors="ignore")
            # 去除 BOM 和 JS 注释
            if data.startswith("\ufeff"):
                data = data[1:]
            # 尝试解析 JSON
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                # 有些源在 JSON 前面有 JS 注释行，尝试去掉
                lines = data.split("\n")
                clean_lines = [
                    l for l in lines if not l.strip().startswith("//")
                ]
                clean_data = "\n".join(clean_lines)
                try:
                    return json.loads(clean_data)
                except json.JSONDecodeError:
                    # 移除控制字符后再试
                    import re
                    clean_data = re.sub(r'[\x00-\x1f\x7f]', '', clean_data)
                    return json.loads(clean_data)
    except Exception as e:
        print(f"  ⚠️  获取失败: {e}")
        return None


def fetch_text(url, timeout=15):
    """获取远程文本数据"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ssl_ctx) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"  ⚠️  获取失败: {e}")
        return None


def deduplicate_sites(sites):
    """按 key 去重，保留最后出现的"""
    seen = {}
    for site in sites:
        key = site.get("key", "")
        if key:
            seen[key] = site
    return list(seen.values())


def generate_urls_json():
    """生成多仓配置"""
    urls = [
        {"name": "⭐小盒子4K", "url": "http://xhztv.top/4k.json"},
        {"name": "⭐小盒子单仓", "url": "http://xhztv.top/xhz/"},
        {"name": "⭐老刘备", "url": "https://raw.liucn.cc/box/m.json"},
        {"name": "⭐小马", "url": "https://szyyds.cn/tv/x.json"},
        {"name": "⭐无名", "url": "https://6800.kstore.vip/fish.json"},
        {"name": "⭐jinenge", "url": "https://jinenge.us.kg/app/tvbox/tvbox.json"},
        {"name": "⭐摸鱼儿", "url": "http://摸鱼儿.cc"},
        {"name": "⭐肥猫", "url": "http://肥猫.net/"},
        {"name": "⭐OK影视", "url": "https://cdn.jsdelivr.net/gh/2hacc/TVBox@main/oktv.json"},
        {"name": "⭐嗷呜", "url": "http://itv666.cc/aowu/config.webp"},
        {"name": "⭐VOX", "url": "http://rihou.cc:88/demo.php"},
        {"name": "⭐挺好分享多仓", "url": "https://ztha.top/TVBox/GYCK.json"},
    ]
    return {"urls": urls}


def check_source_health(url):
    """检查源是否可用（使用 GET 请求，有些服务器不支持 HEAD）"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10, context=ssl_ctx) as resp:
            return resp.status == 200
    except urllib.error.HTTPError as e:
        # 301/302 重定向也算正常
        return e.code in (301, 302, 303, 307, 308)
    except Exception:
        return False


def main():
    print("=" * 50)
    print("📺 TVBox 源自动更新工具")
    print(f"⏰ 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    # 1. 更新 urls.json
    print("\n📋 更新多仓配置 (urls.json)...")
    urls_data = generate_urls_json()
    urls_path = os.path.join(SCRIPT_DIR, "urls.json")
    with open(urls_path, "w", encoding="utf-8") as f:
        json.dump(urls_data, f, ensure_ascii=False, indent=2)
    print(f"   ✅ 已生成 {len(urls_data['urls'])} 个多仓线路")

    # 2. 从各个源拉取数据并合并
    print("\n🔄 从上游源拉取站点数据...")
    source_urls = [
        ("老刘备", "https://raw.liucn.cc/box/m.json"),
        ("小马", "https://szyyds.cn/tv/x.json"),
        ("无名", "https://6800.kstore.vip/fish.json"),
        ("jinenge", "https://jinenge.us.kg/app/tvbox/tvbox.json"),
        ("小盒子4K", "http://xhztv.top/4k.json"),
        ("小盒子单仓", "http://xhztv.top/xhz/"),
    ]

    all_sites = []
    total_sites = 0
    for name, url in source_urls:
        print(f"  📥 正在获取 {name}...", end=" ")
        data = fetch_json(url)
        if data and "sites" in data:
            sites = data["sites"]
            all_sites.extend(sites)
            total_sites += len(sites)
            print(f"✅ 获取 {len(sites)} 个站点")
        else:
            print("❌ 失败")

    print(f"\n  📊 共获取 {total_sites} 个站点（去重前）")

    # 3. 去重
    deduped = deduplicate_sites(all_sites)
    print(f"  📊 去重后剩余 {len(deduped)} 个站点")

    # 4. 生成 tvbox.json
    tvbox_data = {
        "spider": "",
        "wallpaper": "https://raw.githubusercontent.com/jifeng250/tvbox-sources/main/wallpaper.jpg",
        "warningText": "资源来自网络，仅供学习交流使用，请勿用于商业用途。",
        "sites": deduped,
    }

    tvbox_path = os.path.join(SCRIPT_DIR, "tvbox.json")
    with open(tvbox_path, "w", encoding="utf-8") as f:
        json.dump(tvbox_data, f, ensure_ascii=False, indent=2)
    print(f"\n  ✅ 已生成 tvbox.json（{len(deduped)} 个站点）")

    # 5. 健康检查
    print("\n🔍 对多仓线路进行健康检查...")
    healthy = 0
    unhealthy = 0
    for entry in urls_data["urls"]:
        url = entry["url"]
        print(f"  📡 {entry['name']}...", end=" ")
        ok = check_source_health(url)
        if ok:
            print("✅ 正常")
            healthy += 1
        else:
            print("❌ 不可达")
            unhealthy += 1
    print(f"\n  📊 健康检查: {healthy} 正常, {unhealthy} 异常")

    print("\n" + "=" * 50)
    print("✅ 更新完成！")
    print("=" * 50)


if __name__ == "__main__":
    main()