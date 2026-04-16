---
title: 手机远程Coding Agent：Tailscale + Moshi 打造随身开发环境
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
  - Coding Agent
---

面向 Coding Agent 重度用户，随时随地 vibe coding 的你。

现在的 Coding Agent 越来越多：Claude、Copilot、OpenCode、Codex、Trae……它们大多活在终端里，SSH 远程连接变得前所未有的重要。

而如果能搭配 typeless 之类的智能语音输入法，效率直接飙升——手机打字也能像电脑一样流畅，掏出来就能继续 vibe coding。

这套方案的核心组合：**Tailscale + Moshi**。

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

## 5. 不影响手机科学上网：Tailscale Exit Node

如果手机只能连一个 VPN，但想让手机和电脑一样科学上网，可以把电脑的 tailscale 设置成 exit node，让手机 tailscale 连它，这样手机的流量就都走电脑了，不影响手机的科学上网。

### 操作细节

1. 在电脑上运行：

```bash
sudo tailscale up --advertise-exit-node --ssh
```

这样电脑会作为 exit node 并支持 ssh。

2. 打开 tailscale admin 控制台，找到你的电脑节点，点击"Edit route settings"，允许其作为 exit node。

3. 在手机端 tailscale 选择电脑节点作为 exit-node，手机流量即可全部走电脑。

设置方法可参考 tailscale 官方文档：[Exit Nodes](https://tailscale.com/kb/1103/exit-nodes/)

## 6. 为什么最终选择了 Moshi？

免费的 mosh 连接次数用完之后，对比了 blink 和 terminus：blink 界面太复杂，terminus UI 太老气。Moshi 界面简洁颜值高，再加上 mosh 永不断联和 tmux sessions 自动发现，决定付费。

## 配图

![tailscale社区版安装命令](/uploads/tailscale-install.png)

![Moshi连接成功界面](/uploads/moshi-success.png)

祝你少踩坑，随时随地 vibe coding！

## Q&A

**Q: 为什么不选 OpenClaw + ACP 组合进行远程控制 Coding Harness？**

A: OpenClaw + ACP 的方案有两个问题：
1. 需要关联 channel 会话和 ACP 会话，容易混淆
2. 无法面对"电脑终端开多个 coding harness 干活，又想在手机上继续"的场景

相比之下，Tailscale + Moshi 直接接管终端 session，不存在会话映射的问题，电脑上开几个 tmux session，手机上都能看到、切换、继续。
