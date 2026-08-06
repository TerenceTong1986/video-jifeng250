# 📺 TVBox 整合影视源

精选优质 TVBox / 影视仓 配置源，每日自动更新可用性检测。

## 🚀 使用方式

### 方式一：多仓配置（推荐）

在 TVBox / 影视仓 的配置地址中输入以下链接：

```
https://raw.githubusercontent.com/你的用户名/tvbox-sources/main/urls.json
```

包含 12 个精选线路，一个失效自动切换。

### 方式二：单仓配置

```
https://raw.githubusercontent.com/你的用户名/tvbox-sources/main/tvbox.json
```

包含精选去重后的站点列表。

## 📋 包含的线路

| 名称 | 源地址 | 说明 |
|------|--------|------|
| ⭐小盒子4K | `http://xhztv.top/4k.json` | 4K 资源丰富 |
| ⭐老刘备 | `https://raw.liucn.cc/box/m.json` | 站点最全，57KB+ |
| ⭐小马 | `https://szyyds.cn/tv/x.json` | 稳定，内含爱优腾芒解析 |
| ⭐无名 | `https://6800.kstore.vip/fish.json` | 鱼系源，稳定可靠 |
| ⭐jinenge | `https://jinenge.us.kg/app/tvbox/tvbox.json` | 内置源，持续维护 |
| ⭐摸鱼儿 | `http://摸鱼儿.cc` | 经典老牌源 |
| ⭐肥猫 | `http://肥猫.net/` | 经典老牌源 |
| ⭐OK影视 | `https://cdn.jsdelivr.net/gh/2hacc/TVBox@main/oktv.json` | jsdelivr CDN 加速 |
| ⭐嗷呜 | `http://itv666.cc/aowu/config.webp` | 稳定可用 |
| ⭐VOX | `http://rihou.cc:88/demo.php` | 轻量稳定 |
| ⭐挺好分享多仓 | `https://ztha.top/TVBox/GYCK.json` | 多仓线路 |

## 🔄 自动更新

本项目通过 GitHub Actions **每天 UTC 00:00（北京时间 08:00）** 自动：

1. 拉取所有上游源的站点数据
2. 按 `key` 去重合并
3. 更新 `tvbox.json`（单仓配置）
4. 更新 `urls.json`（多仓配置）
5. 对多仓线路进行健康检查

也可手动触发更新：Actions → 每日自动更新 TVBox 源 → Run workflow

## 🛠️ 本地运行

```bash
pip install -r requirements.txt
python update.py
```

## ⚠️ 免责声明

- 本仓库仅收集互联网公开资源，不提供任何影视文件
- 所有资源仅供学习交流，请勿用于商业用途
- 如有侵权请联系删除

## 📄 许可

MIT