#!/usr/bin/env python3
"""云端自动打包 TVBox 精选源本地包（在 GitHub Actions 中运行）

逻辑与本地 tools/update_tvbox_local_pack.py 一致，但 SRC=当前工作目录，
用于云端每次源/直播更新后自动生成 tvbox-sources-YYYYMMDD.zip + version.json，
并存回仓库根，使 PWA 下载页始终显示最新包。

打包内容：curated.json + curated-local.json + 3 个 jar + 直播源 + 台标/EPG 配置等
排除：.git / __pycache__ / 其它 tvbox-sources-*.zip / version.json
"""
import zipfile, os, sys, json, shutil
from datetime import datetime

SRC = os.getcwd()  # GitHub Actions checkout 目录
# apk/.github 不打进配置包（apk 在网页「影视软件」区块单独下载，避免包膨胀到~100MB）
EXCLUDE_DIRS = {'.git', '__pycache__', 'apk', '.github'}
REQUIRED = ['curated.json', 'fan.jar', 'custom_spider.jar', 'pg.jar', 'tvfan/Cloud-drive.txt']


def make_local_config():
    """生成 curated-local.json：jar/js 字段指向包内相对路径"""
    src = os.path.join(SRC, 'curated.json')
    dst = os.path.join(SRC, 'curated-local.json')
    cfg = json.load(open(src, encoding='utf-8'))
    cfg['spider'] = './fan.jar'
    for s in cfg.get('sites', []):
        if 'jar' in s:
            for jn in ['custom_spider.jar', 'pg.jar', 'fan.jar']:
                if jn in s['jar']:
                    s['jar'] = './' + jn
                    break
        # js 源(drpy2/drpy): api=引擎js, ext=规则js, 都重写为包内相对路径
        if s.get('type') == 3 and s.get('api', '').endswith('.js'):
            jsname = s['api'].split('/')[-1]
            s['api'] = './js/' + jsname
            if s.get('ext', '').endswith('.js'):
                extname = s['ext'].split('/')[-1]
                s['ext'] = './js/' + extname
    cfg['updateTime'] = datetime.now().strftime('%Y-%m-%d %H:%M')
    cfg['warningText'] = '精选单仓·本地版：jar 走本地文件，断网可用。若源加载不出目录，把 jar 改为 file:///绝对路径（见 README）'
    with open(dst, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, ensure_ascii=False, indent=1)
    return dst


def main():
    # 前置校验：关键文件存在
    missing = [r for r in REQUIRED if not os.path.exists(os.path.join(SRC, r))]
    if missing:
        print(f"❌ 缺少关键文件: {', '.join(missing)}，拒绝打包")
        sys.exit(1)

    make_local_config()
    print("已生成本地版配置: curated-local.json")

    date_str = datetime.now().strftime("%Y%m%d")
    dst = os.path.join(SRC, f"tvbox-sources-{date_str}.zip")

    # 清理旧 zip（保留当天最新一份）
    for old in os.listdir(SRC):
        if old.startswith("tvbox-sources-") and old.endswith(".zip") and old != os.path.basename(dst):
            try:
                os.remove(os.path.join(SRC, old))
                print(f"  清理旧包: {old}")
            except OSError:
                pass

    count = 0
    with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for root, dirs, files in os.walk(SRC):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            for f in files:
                if f.endswith('.zip') or f == 'version.json':
                    continue
                full = os.path.join(root, f)
                arc = os.path.join('tvbox-sources', os.path.relpath(full, SRC))
                z.write(full, arc)
                count += 1

    size_kb = os.path.getsize(dst) / 1024
    print(f"OK: {count} files, {size_kb:.1f} KB")
    print(f"新包: {dst}")

    # 生成 version.json（PWA 页面读取）
    cfg = json.load(open(os.path.join(SRC, 'curated.json'), encoding='utf-8'))
    filename = os.path.basename(dst)
    raw = f"https://raw.githubusercontent.com/jifeng250/tvbox-sources/main/{filename}"
    urls = [
        f"https://ghfast.top/{raw}",
        f"https://gh-proxy.com/{raw}",
        f"https://ghproxy.net/{raw}",
        f"https://cdn.jsdelivr.net/gh/jifeng250/tvbox-sources@main/{filename}",
        f"https://fastly.jsdelivr.net/gh/jifeng250/tvbox-sources@main/{filename}",
        f"https://gcore.jsdelivr.net/gh/jifeng250/tvbox-sources@main/{filename}",
        raw,
    ]
    ver = {
        "version": date_str,
        "date": datetime.now().strftime('%Y-%m-%d %H:%M'),
        "size": f"{size_kb / 1024:.2f} MB",
        "sites": len(cfg.get('sites', [])),
        "url": urls[0],
        "urls": urls,
    }
    with open(os.path.join(SRC, 'version.json'), 'w', encoding='utf-8') as f:
        json.dump(ver, f, ensure_ascii=False, indent=2)
    print(f"已生成 version.json (sites={ver['sites']})")


if __name__ == "__main__":
    main()
