---
layout: post
title: "我给自己造了一支 AI 团队：OpenClaw 多智能体系统重建实录"
date: 2026-04-05 15:00:00 +0800
categories: AI
tags: [OpenClaw, AI Agent, 多智能体, 自动化, LLM]
---

# 我给自己造了一支 AI 团队：OpenClaw 多智能体系统重建实录

> 五个 AI Agent，各司其职，全天候自动运转——这是我用一个下午完成的事情。

---

## 一、背景：为什么要搞多智能体？

我一直在用 [OpenClaw](https://github.com/nicepkg/openclaw) 跑 AI Agent。最初只是把几个 Agent 挂在飞书群里聊天用，但用着用着发现一个问题：**它们太"被动"了**。

Agent 只会回复消息，不会主动做事。没有工作流，没有定时任务，没有收入产出。它们更像是几个等待投喂的聊天机器人，而不是真正的"团队成员"。

于是我决定做一次彻底重建——不是调调参数，而是从身份定义、模型策略、自动化调度、到收入管线，全部推倒重来。

---

## 二、团队阵容

重建后的五人阵容：

| Agent | 代号 | 角色 | 语言 |
|-------|------|------|------|
| **Judy 💖** | main | 总调度 / 管家 | 中英双语 |
| **Phoenix 🦅** | coding | 全栈开发 / 开源 | English |
| **Mike ⚙️** | devops | 运维 / 基础设施 | English |
| **Shirly ✍️** | momo | 内容创作 / 自媒体 | 中文 |
| **xueqin 📜** | litterature | 小说写作导师 | 中文 |

每个 Agent 都有完整的 `SOUL.md`（身份定义）、`IDENTITY.md`（自我认知）、`USER.md`（对我的了解）和 `HEARTBEAT.md`（自主工作指令）。

---

## 三、四大子项目

整个重建拆成了四个子项目，按依赖顺序执行。

### SP1: 基础重建（Foundation Rebuild）

**核心改动：**

- **模型策略统一**：所有 Agent 统一使用 `github-copilot/gpt-5-mini` 作为主模型，配合 OpenRouter（免费额度）和 Ollama 本地模型作为降级方案
- **身份体系重写**：五个 Agent 的 SOUL/IDENTITY/USER 全部重写，明确性格、能力边界、语言偏好
- **配置清理**：API Key 迁移到环境变量，移除硬编码密钥，per-agent `models.json` 精简为连接信息
- **Token 上限**：`maxTokens` 从默认值提升到 16384

**模型降级链：**

```
gpt-5-mini (Copilot) → stepfun/step-3.5-flash (OpenRouter免费) → qwen3.5:35b (Ollama本地) → gemma4:e4b (Ollama本地)
```

这样即使 Copilot API 出问题，Agent 也不会完全停摆。

### SP2: 自动化引擎（Automation Engine）

之前只有一个孤零零的 DevOps 日报 cron job。重建后变成了 **Judy 主导的三段式调度**：

| 时间 | 任务 | 说明 |
|------|------|------|
| 08:00 | 晨间派发 | Judy 检查 Apple Reminders，扫描各 Agent 状态，分派任务 |
| 14:00 | 午间巡检 | 检查进度，催促无产出的 Agent，协调阻塞 |
| 22:00 | 夜间总结 | 生成日报，通过飞书私信发给我 |

每个 Agent 的 `HEARTBEAT.md` 也从空文件变成了具体的自主工作指令——Agent 被唤醒时知道该做什么，而不是等着被告知。

### SP3: 内容管线（Revenue: Content Pipeline）

Shirly 从"聊天机器人"升级为**自媒体内容引擎**：

- **目标平台**：小红书 + 微信公众号
- **内容存储**：`~/shirley-content/`，包含 queue（待发布）、published（已发布）、archive（归档）
- **模板系统**：JSON 格式的平台模板（标题字数限制、标签规则、封面规格等）
- **浏览器自动化**：基于 Playwright + Edge 的发布脚本，支持 cookie 会话管理
- **日常流程**：调研选题 → 撰写内容 → 生成封面 → 自动发布

```
~/shirley-content/
├── queue/          # 待发布内容（JSON 格式）
├── published/      # 已发布归档
├── archive/        # 历史内容
├── templates/      # 平台模板（xiaohongshu.json, weixin.json）
├── scripts/        # Playwright 发布脚本
└── .sessions/      # 平台 cookie 会话
```

### SP4: 编码管线（Revenue: Coding Pipeline）

Phoenix 的定位是**自主开源开发者**：

- **项目管线**：`~/workspace-phoenix/pipeline/` — ideas → active → shipped
- **收入模式**：开源项目 + GitHub Sponsors + 产品化
- **工作流程**：发现趋势 → 评估可行性 → 原型开发 → 迭代打磨 → 发布到 GitHub
- **完全自主**：无需我审批，Phoenix 自行决定做什么项目

---

## 四、踩过的坑

### 坑 1：配置校验比想象中严格

OpenClaw 的 `openclaw.json` 有严格的 schema 校验。我们在 `agents.defaults.model` 里加了 `fallback` 数组：

```json
{
  "primary": "github-copilot/gpt-5-mini",
  "fallback": ["openrouter/stepfun/step-3.5-flash:free", "ollama/qwen3.5:35b"]
}
```

结果 gateway 直接拒绝启动：`agents.defaults.model: Invalid input`。

正确做法是 `model` 只接受 `{"primary": "<alias>"}` 的格式，模型列表在 `models` 字段定义。降级逻辑由 OpenClaw 框架根据 `models` 里的可用模型自动处理。

### 坑 2：Per-Agent compaction 不被支持

想给 coding 和 litterature 两个 Agent 设置 `compaction: auto`（因为它们上下文消耗大），结果：

```
agents.list.1: Unrecognized key: "compaction"
```

`compaction` 只能放在 `agents.defaults` 级别，不能放在单个 Agent 的配置里。所有 Agent 共享同一个 compaction 策略。

### 坑 3：Playwright 的浏览器选择

默认 Playwright 会下载 Chromium，但我的 Mac 上主力浏览器是 Edge。需要在脚本里显式指定：

```javascript
const browser = await chromium.launch({ channel: 'msedge' });
```

这样可以复用已有的 Edge 安装和 cookie，不需要额外下载几百 MB 的 Chromium。

---

## 五、架构全景

```
~/.openclaw/
├── openclaw.json           # 中央配置（模型、Agent、工具、通道）
├── .env                    # 环境变量（API Key）
├── cron/jobs.json          # 4 个定时任务
├── agents/                 # 5 个 Agent 的运行时配置
│   ├── main/               # Judy
│   ├── coding/             # Phoenix
│   ├── devops/             # Mike
│   ├── momo/               # Shirly
│   └── litterature/        # xueqin
├── workspace*/             # 各 Agent 的工作空间
│   ├── SOUL.md             # 身份定义
│   ├── IDENTITY.md         # 自我认知
│   ├── USER.md             # 用户画像
│   ├── HEARTBEAT.md        # 自主工作指令
│   └── memory/             # 持久化记忆
└── docs/superpowers/       # 设计文档和实施计划
    ├── specs/              # 4 份设计规格
    └── plans/              # 4 份实施计划

~/shirley-content/          # Shirly 的内容管线（独立于 openclaw）
~/workspace-phoenix/        # Phoenix 的项目管线
```

---

## 六、效果与展望

重建完成后，运行 `openclaw gateway restart`，整个系统立即生效：

- ✅ Judy 每天三次自动巡检和调度
- ✅ Phoenix 自主探索开源项目机会
- ✅ Shirly 进入内容创作工作流
- ✅ Mike 按时提交运维日报
- ✅ xueqin 持续小说写作辅导

**下一步计划：**

1. 观察运行数据，调整 cron 频率和 heartbeat 策略
2. 小红书和公众号开通后，验证 Playwright 自动发布流程
3. 为 Phoenix 的项目配置 GitHub Sponsors
4. 考虑加入数据库替代 Markdown 做指标追踪
5. 扩展 Shirly 到抖音/微博等更多平台

---

## 七、写在最后

搭建这套系统的过程本身就很有趣——我用 AI Agent（GitHub Copilot）来设计和实现另一组 AI Agent 的工作流。这种"AI 造 AI"的体验让我意识到：

**多智能体系统的核心不是技术，而是组织设计。**

模型选哪个、参数调多少，这些都是战术问题。真正关键的是：每个 Agent 的职责边界在哪里？它们之间怎么协作？谁来做决策？谁来兜底？

这跟管理一个真实的团队没什么两样。

---

*本文撰写于 2026 年 4 月 5 日。整个重建过程在一个下午内完成，包括设计、实施、调试和验证。*
