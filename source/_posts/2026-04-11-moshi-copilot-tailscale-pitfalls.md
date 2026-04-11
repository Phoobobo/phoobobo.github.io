---
layout: post
title: "别装错tailscale！Moshi远控Copilot终端的血泪踩坑记"
date: 2026-04-11 14:55:00 +0800
categories: 工具
tags: [moshi, copilot, tailscale, 远程开发, 踩坑]
---

> 面向Agentic coding重度用户，随时随地vibe coding的你。

最近想用手机随时远程操控Copilot终端，选了Moshi + Tailscale这套方案，结果一顿操作猛如虎，差点被坑到怀疑人生。这里总结下关键坑点，帮你避雷。

## 1. tailscale一定要装社区版！

别问，问就是`brew install --formula tailscale`。装错App Store版，Moshi根本连不上，白忙活一小时。

## 2. tailscale服务一定要先启动

`sudo brew services start tailscale`，不启动服务，ssh连不上，Moshi只会报错。

## 3. 先启动tailscale，再用ssh连接

顺序不能错！先`sudo tailscale up`，再在Moshi里用ssh连，不然会莫名其妙连不上。

## 4. Moshi配置没问题，关键在tailscale

Moshi配置很简单，坑全在tailscale。只要tailscale社区版+服务启动+顺序对，Moshi就能愉快vibe coding。

## 配图

![tailscale社区版安装命令](uploads/tailscale-install.png)

![Moshi连接成功界面](uploads/moshi-success.png)

## 参考链接

- [官方教程：Mac Remote Endless Agent Setup](https://getmoshi.app/articles/mac-remote-endless-agent-setup)
- [tailscale官方文档](https://tailscale.com/kb/)

祝你少踩坑，随时随地vibe coding！
