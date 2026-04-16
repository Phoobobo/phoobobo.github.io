---
title: 别装错tailscale！Moshi远控Copilot终端的血泪踩坑记
date: 2026-04-11 14:55:00
updated: 2026-04-16 02:30:00
categories:
  - AI工具
tags:
  - 踩坑
  - moshi
  - copilot
  - tailscale
  - 远程开发
---

面向 Agentic coding 重度用户，随时随地 vibe coding 的你。

最近想用手机随时远程操控 Copilot 终端，选了 Moshi + Tailscale 这套方案，结果一顿操作猛如虎，差点被坑到怀疑人生。这里总结下关键坑点，帮你避雷。

<!--more-->

## 0. 先看官方文档

建议先通读官方教程，再来看这篇踩坑记录：

**[Mac Remote Endless Agent Setup](https://getmoshi.app/articles/mac-remote-endless-agent-setup)**

**[tailscale 官方文档](https://tailscale.com/kb/)**

官方文档讲了 what，本篇讲的是 why 和坑。

## 1. tailscale 一定要装社区版！

别问，问就是 `brew install --formula tailscale`。装错 App Store 版，Moshi 根本连不上，白忙活一小时。

## 2. tailscale 服务一定要先启动

`sudo brew services start tailscale`，不启动服务，ssh 连不上，Moshi 只会报错。

## 3. 先启动 tailscale，再用 ssh 连接

顺序不能错！先 `sudo tailscale up --ssh`，再在 Moshi 里用 ssh 连，不然会莫名其妙连不上。

## 4. Moshi 配置没问题，关键在 tailscale

Moshi 配置很简单，坑全在 tailscale。只要 tailscale 社区版+服务启动+顺序对，Moshi 就能愉快 vibe coding。

## 5. 让手机也能科学上网：Tailscale Exit Node

如果你电脑上同时用着别的 VPN 和 tailscale，而手机只能连一个 VPN，但又想让手机和电脑一样科学上网，可以把电脑的 tailscale 设置成 exit node，然后让手机 tailscale 连它，这样手机的流量就都走电脑了，和电脑体验一致。

### 操作细节

1. 在电脑上运行：

```bash
sudo tailscale up --advertise-exit-node --ssh
```

这样电脑会作为 exit node 并支持 ssh。

2. 打开 tailscale admin 控制台，找到你的电脑节点，点击"Edit route settings"，允许其作为 exit node。

3. 在手机端 tailscale 选择电脑节点作为 exit-node，手机流量即可全部走电脑。

设置方法可参考 tailscale 官方文档：[Exit Nodes](https://tailscale.com/kb/1103/exit-nodes/)

## 6. 为什么最终选择了 Moshi 付费订阅？

免费试用期间只能用 ssh 连接，用着用着发现 ssh 断联是家常便饭——电梯里晃一下断了，等地铁时断了，信号不好时断了。每次都要重新连接、重新进入 tmux session，体验碎成渣。

于是对比了其他终端 app：

| App | 价格 | 界面 | Mosh | 我的选择 |
|-----|------|------|------|---------|
| **Moshi** | $8/月起 | 简洁现代 | ✅ | ✅ |
| Blink | $10/月起 | 功能多但复杂 | ✅ | ❌ |
| Terminus | $10/月起 | 老派土气 | ✅ | ❌ |

Blink 和 Terminus 虽然也有 mosh，但要么界面太复杂，要么 UI 太丑。最关键的是：**Moshi 最便宜**。

订阅之后，mosh 连接 + tmux sessions 自动发现，体验直接起飞：
- **永不断联**：地铁、电梯、信号差的角落，统统不掉线
- **tmux 自动恢复**：切回来时 session 还在，terminal 状态完美保留
- **Copilot 随时在线**：随时掏手机 vibe coding

付费 Moshi + Tailscale，是目前移动 Copilot coding 的最优解。

## 配图

![tailscale社区版安装命令](/uploads/tailscale-install.png)

![Moshi连接成功界面](/uploads/moshi-success.png)

祝你少踩坑，随时随地 vibe coding！
