# 📺 TVBox 整合影视源

精选优质 TVBox / 影视仓 配置源，每日自动更新可用性检测。

## 🚀 使用方式

### 方式一：多仓配置（推荐）

在 TVBox / 影视仓 的配置地址中输入以下链接：

```
https://gh-proxy.com/https://raw.githubusercontent.com/jifeng250/tvbox-sources/main/urls.json
```

包含 21 条精选线路 + 3 条 GitHub 镜像，自动按健康度排序，失效自动切换。

### 方式二：单仓配置

```
https://gh-proxy.com/https://raw.githubusercontent.com/jifeng250/tvbox-sources/main/tvbox.json
```

包含精选去重后的站点列表。

## 📋 包含的线路

| 名称 | 源地址 | 说明 |
|------|--------|------|
| ⭐⭐⭐小盒子多仓 | `http://xhztv.top/dc` | 小盒子系列多仓 |
| ⭐⭐⭐小盒子单仓 | `http://xhztv.top/xhz/` | 小盒子单仓（54站） |
| ⭐⭐⭐小盒子4K | `http://xhztv.top/4k.json` | 4K 资源丰富（53站） |
| ⭐⭐⭐老刘备 | `https://raw.liucn.cc/box/m.json` | 站点最全（228站） |
| ⭐⭐⭐OK影视 | `https://cdn.jsdelivr.net/gh/2hacc/TVBox@main/oktv.json` | jsdelivr CDN 加速（41站） |
| ⭐⭐⭐高天流云 | `https://fastly.jsdelivr.net/gh/gaotianliuyun/gao@master/js.json` | 站点最丰富（297站） |
| ⭐⭐道长 | `https://gitlab.com/duomv/dzhipy/-/raw/main/index.json` | 站点最多（435站） |
| ⭐⭐拾光多仓 | `http://xmbjm.fh4u.org/dc.txt` | 多仓线路 |
| ⭐⭐王二小 | `https://9280.kstore.vip/newwex.json` | 鱼系源（87站） |
| ⭐⭐FM影视 | `http://fmys.top/fmys.json` | 82站 |
| ⭐⭐无名 | `https://6800.kstore.vip/fish.json` | 鱼系源（99站） |
| ⭐⭐俊佬 | `http://home.jundie.top:81/top98.json` | 24站 |
| ⭐肥猫 | `http://肥猫.net/` | 经典老牌源（40KB+） |
| ⭐jinenge | `https://jinenge.us.kg/app/tvbox/tvbox.json` | 持续维护（42站） |
| ⭐小马 | `https://szyyds.cn/tv/x.json` | 内含爱优腾芒解析（60站） |
| ⭐嗷呜 | `http://itv666.cc/aowu/config.webp` | 稳定可用 |
| ⭐挺好分享多仓 | `https://ztha.top/TVBox/GYCK.json` | 多仓线路 |
| ⭐饭太硬(ftygit) | `https://cdn09022024.gitlink.org.cn/api/v1/repos/xxooo/in/raw/in.bmp` | 图片内嵌配置 |
| ⚠️饭太硬(官方) | `http://www.饭太硬.net/tv` | 官方线路（波动时自动降级） |
| 🪞OK影视镜像1 | `https://fastly.jsdelivr.net/gh/2hacc/TVBox@main/oktv.json` | 备用镜像 |
| 🪞王二小镜像1 | `https://9280.kstore.vip/wex.json` | 备用镜像 |
| 🪞饭太硬(官方)镜像1 | `http://fty.xxooo.cf/tv` | 备用镜像 |
| 🪞GitHub镜像(kgithub) | `https://raw.kkgithub.com/jifeng250/tvbox-sources/main/tvbox.json` | 本仓镜像 |
| 🪞GitHub镜像(jsdelivr) | `https://fastly.jsdelivr.net/gh/jifeng250/tvbox-sources@main/tvbox.json` | 本仓镜像（CDN加速） |

## 🔄 自动更新

本项目通过 GitHub Actions **每天 UTC 00:00（北京时间 08:00）** 自动：

1. 拉取所有上游源的站点数据（13 个上游源）
2. 按 `key` 去重合并（优先级：靠前的主源胜出）
3. 更新 `tvbox.json`（单仓配置）
4. 更新 `urls.json`（多仓配置，按星级排序）
5. 对多仓线路进行健康检查 + 测速，连续失败 3 次自动移除

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
