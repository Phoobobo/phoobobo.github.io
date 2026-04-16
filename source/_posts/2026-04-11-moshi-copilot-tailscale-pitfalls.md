---
title: 手机远程Coding Agent：Tailscale + Moshi + Typeless 打造随身开发环境
date: 2026-04-11 14:55:00
updated: 2026-04-16 02:30:00
categories:
  - AI工具
tags:
  - 踩坑
  - moshi
  - tailscale
  - 远程开发
  - Claude
  - Copilot
  - Cursor
  - Coding Agent
---

面向 Coding Agent 重度用户，随时随地 vibe coding 的你。

现在的 Coding Agent 越来越多：Claude、Copilot、OpenCode、Codex、Trae……它们大多活在终端里，SSH 远程连接变得前所未有的重要。

而如果能在手机上搭配 **Typeless 输入法**，效率直接飙升——手机打字也能像电脑一样流畅，掏出来就能继续 vibe coding。

这套方案的核心组合：**Tailscale + Moshi + Typeless**。

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
- **Coding Agent 随时在线**：随时掏手机 vibe coding

付费 Moshi + Tailscale，是目前移动 Coding Agent 的最优解。

## 7. Typeless：手机输入法的新选择

说到手机 SSH，不能不提输入法。普通手机输入法在终端里简直是噩梦——候选词弹窗、智能联想、滑动输入……全都在干扰输入。

**Typeless** 是一款专为终端/代码场景设计的输入法：
- **无候选框**：打字直接上屏，没有任何干扰
- **无智能联想**：终端里不需要预测
- **外接键盘友好**：配合蓝牙键盘，体验接近实体键盘

手机 + Typeless + Moshi + Tailscale = 随身 Coding Agent 工作站。

## 配图

![tailscale社区版安装命令](/uploads/tailscale-install.png)

![Moshi连接成功界面](/uploads/moshi-success.png)

祝你少踩坑，随时随地 vibe coding！
