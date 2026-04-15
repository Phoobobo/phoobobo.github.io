---
title: 别装错tailscale！Moshi远控Copilot终端的血泪踩坑记
date: 2026-04-11 14:55:00
updated: 2026-04-11 14:55:00
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

## 配图

![tailscale社区版安装命令](/uploads/tailscale-install.png)

![Moshi连接成功界面](/uploads/moshi-success.png)

## 参考链接

- [官方教程：Mac Remote Endless Agent Setup](https://getmoshi.app/articles/mac-remote-endless-agent-setup)
- [tailscale 官方文档](https://tailscale.com/kb/)

祝你少踩坑，随时随地 vibe coding！
