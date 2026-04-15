---
title: Hermes 踩坑经验：从 openclaw 迁移的血泪史
date: 2026-04-12 19:56:00
updated: 2026-04-12 19:56:00
categories:
  - AI工具
tags:
  - 踩坑
  - Hermes
  - openclaw
  - Copilot
  - 迁移
---

Hermes setup 真的很香！整个体验就像用上了一个高级的 coding harness，还自带通信功能，效率直接拉满。

## 成也迁移，败也迁移

这次从 openclaw 迁移到 Hermes，真是五味杂陈。迁移带来了很多便利，但也埋下了不少坑。有些模型 provider 直接不能用，比如 ollama 本地模型、GitHub Copilot。

## Copilot 授权大坑

Hermes 会自动检测本地的 GitHub Token，但这个 Token 用不了！我折腾了半天，最后只能 `gh auth logout`，重新添加 GitHub Copilot，在弹出的 OAuth 页面重新登录授权，然后再 `gh auth login`，这样本地 GH CLI 才能正常用。

## agent 人格设置的迷惑

整个 setup 过程居然没提 agent 人格设置，结果 message work directory 被设到了我龙虾的 workspace，怪不得总觉得哪儿不对劲。Hermes 应该主动问问我要不要重新设置。

## 总结

Hermes setup 很好用，迁移带来新体验，但也有不少坑。希望这篇经验能帮到后来人，少走弯路！
