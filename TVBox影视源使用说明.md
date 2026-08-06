# 📺 TVBox 整合影视源 - 使用说明

> 仓库地址：https://github.com/jifeng250/tvbox-sources
> 每日自动更新，精选 17 个线路（含镜像）、9 个上游源、539+ 个去重站点

---

## 目录

1. [快速开始](#1-快速开始)
2. [配置地址一览](#2-配置地址一览)
3. [TVBox 配置教程](#3-tvbox-配置教程)
4. [影视仓配置教程](#4-影视仓配置教程)
5. [包含的线路说明](#5-包含的线路说明)
6. [常见问题](#6-常见问题)
7. [更新说明](#7-更新说明)

---

## 1. 快速开始

### 第一步：下载 TVBox 或影视仓

| 应用 | 说明 | 下载地址 |
|------|------|---------|
| **TVBox** | 经典开源版 | https://github.com/FongMi/TV |
| **影视仓** | 多仓版，支持多线路切换 | GitHub 搜索 "tvbox" |
| **OK影视** | 功能丰富，有手机端 | https://2hacc.lanzoue.com/b00pzypv9g 密码:5d5i |

### 第二步：复制配置地址

```
https://raw.githubusercontent.com/jifeng250/tvbox-sources/main/urls.json
```

### 第三步：粘贴到软件中

打开软件 → 设置 → 配置地址 → 粘贴 → 确定 → 返回首页

---

## 2. 配置地址一览

### 多仓配置（推荐，17个线路含镜像，自动切换）

```
https://raw.githubusercontent.com/jifeng250/tvbox-sources/main/urls.json
```

### 单仓配置（539+ 个去重站点）

```
https://raw.githubusercontent.com/jifeng250/tvbox-sources/main/tvbox.json
```

### GitHub 加速镜像（国内访问更快）

如果 raw.githubusercontent.com 访问慢，可以用以下镜像：

```
https://raw.kkgithub.com/jifeng250/tvbox-sources/main/urls.json
https://fastly.jsdelivr.net/gh/jifeng250/tvbox-sources@main/urls.json
```

> ⚠️ 镜像站可能不定期失效，优先使用主地址

---

## 3. TVBox 配置教程

### 步骤

1. 打开 TVBox 应用
2. 进入 **设置**（一般在首页右上角或侧边栏）
3. 找到 **配置地址** 选项
4. 输入地址：
   ```
   https://raw.githubusercontent.com/jifeng250/tvbox-sources/main/urls.json
   ```
5. 点击 **确定**
6. 返回首页，等待加载完成

---

## 4. 影视仓配置教程

### 步骤

1. 打开影视仓应用
2. 进入 **设置**（首页左上角或侧边栏）
3. 找到 **配置地址** 或 **接口地址**
4. 输入地址（多仓，推荐）：
   ```
   https://raw.githubusercontent.com/jifeng250/tvbox-sources/main/urls.json
   ```
   或输入单仓地址：
   ```
   https://raw.githubusercontent.com/jifeng250/tvbox-sources/main/tvbox.json
   ```
5. 点击 **确定** 并返回首页
6. 如果加载失败，尝试切换线路

---

## 5. 包含的线路说明

| 线路名称 | 源地址 | 特点 |
|---------|--------|------|
| ⭐小盒子4K | xhztv.top/4k.json | 4K 资源丰富，响应快 |
| ⭐小盒子单仓 | xhztv.top/xhz/ | 小盒子单仓版 |
| ⭐老刘备 | raw.liucn.cc/box/m.json | 站点最全（234+站点，偶有波动） |
| ⭐小马 | szyyds.cn/tv/x.json | 稳定，含爱优腾芒解析 |
| ⭐无名 | 6800.kstore.vip/fish.json | 鱼系源，稳定可靠 |
| ⭐jinenge | jinenge.us.kg | 内置源，持续维护 |
| ⭐摸鱼儿 | 摸鱼儿.cc | 经典老牌源 |
| ⭐肥猫 | 肥猫.net/ | 经典老牌源 |
| ⭐OK影视 | jsdelivr CDN | 含动漫、体育、B站等 |
| ⭐嗷呜 | itv666.cc | 轻量稳定 |
| ⭐VOX | rihou.cc:88 | 含网盘、秒播、盘搜等 |
| ⭐挺好分享多仓 | ztha.top | 多仓线路丰富 |
| ⭐饭太硬(ftygit) | gitlink BMP | 经典饭太硬源，49个站点 |
| ⭐饭太硬(官方) | 饭太硬.cc | 饭太硬官方导航 |
| 🪞GitHub镜像(kgithub) | raw.kkgithub.com | 国内加速镜像 |
| 🪞GitHub镜像(jsdelivr) | fastly.jsdelivr.net | CDN 加速镜像 |

---

## 6. 常见问题

### Q: 配置后加载不出内容？

A: 尝试以下方法：
- 切换到其他线路（多仓配置自动包含多个线路）
- 检查网络连接，尝试使用加速镜像
- 清除软件数据后重新配置
- 更新 TVBox/影视仓 到最新版本

### Q: 有些源看不了？

A: 不同源的资源覆盖范围不同，切换线路即可。多仓配置包含多个线路，总有一个能看。

### Q: 需要梯子吗？

A: 大部分源国内可直接访问，无需梯子。部分源（如摸鱼儿、肥猫、饭太硬官方）使用中文域名，部分网络环境可能需要梯子。

### Q: 配置地址会失效吗？

A: 本项目每天自动检测线路可用性，连续 3 次检测失败的线路会自动从配置中移除。你也可以关注 GitHub 仓库获取最新状态。

### Q: 如何反馈问题？

A: 在 GitHub 仓库提交 Issue：https://github.com/jifeng250/tvbox-sources/issues

---

## 7. 更新说明

本项目通过 GitHub Actions **每天 UTC 00:00（北京时间 08:00）** 自动更新：

1. 拉取所有上游源的站点数据（含饭太硬 BMP 解码）
2. 按 key 去重合并
3. 更新 tvbox.json（单仓配置）
4. 更新 urls.json（多仓配置，含国内镜像）
5. 对多仓线路进行健康检查，连续 3 次失败自动移除

你无需手动操作，每次打开软件会自动加载最新配置。

---

> 最后更新：2026-08-06
> 资源来自网络，仅供学习交流使用，请勿用于商业用途。