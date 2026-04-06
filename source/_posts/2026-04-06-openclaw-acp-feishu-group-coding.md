---
layout: post
title: "在飞书群里让 AI 自动写代码：OpenClaw ACP + Feishu 踩坑实录"
date: 2026-04-06 22:00:00 +0800
categories: AI
tags: [OpenClaw, ACP, Feishu, Copilot CLI, 多智能体]
---

# 在飞书群里让 AI 自动写代码：OpenClaw ACP + Feishu 踩坑实录

> 在飞书群发一条消息，十分钟后 GitHub 上出现了一个可以玩的游戏。中间没有人动一行代码。

这篇文章记录了我如何把 OpenClaw ACP 和 Feishu 打通，让 AI Agent 在群聊里收到需求后，自动调起 Copilot CLI 去写代码、建仓库、推 GitHub——以及这条路上踩过的每一个坑。

<!-- more -->

---

## 一、目标：群里喊一声，代码自己写好

最终实现效果：

1. 我在飞书编程群发消息：`做一个贪吃蛇游戏`
2. Phoenix（群里的 AI 技术负责人）收到消息，分析需求
3. Phoenix 调用 `sessions_spawn` 把任务委托给 Copilot CLI
4. Copilot CLI 在本地工作区写好代码，初始化 git，推到 GitHub
5. Phoenix 把仓库 URL 发回群里

整个过程无需人工干预，Phoenix 是协调者，Copilot CLI 是执行者。

---

## 二、环境说明

| 组件 | 作用 |
|------|------|
| **OpenClaw** | AI Agent 网关，管理 agent 会话、路由消息、调用 LLM |
| **acpx 插件** | OpenClaw 插件，本地运行 Copilot CLI，桥接 ACP 协议 |
| **Feishu channel** | OpenClaw 的消息通道，通过 WebSocket 长连接接收飞书消息 |
| **Phoenix (coding agent)** | LLM mode 的 agent，绑定在编程群，负责分析需求并委托 Copilot CLI |
| **Copilot CLI** | 实际写代码的执行者，由 acpx 在本地进程中运行 |

关键 `openclaw.json` 配置骨架：

```json
{
  "acp": {
    "enabled": true,
    "backend": "acpx"
  },
  "plugins": {
    "entries": {
      "acpx": {
        "enabled": true,
        "config": {
          "permissionMode": "approve-all"
        }
      }
    }
  },
  "agents": {
    "list": [
      {
        "id": "coding",
        "model": "copilot",
        "tools": { "profile": "full" }
      }
    ]
  },
  "bindings": [
    {
      "agentId": "coding",
      "match": {
        "channel": "feishu",
        "peer": {
          "kind": "group",
          "id": "oc_你的群ID"
        }
      }
    }
  ]
}
```

注意 `coding` agent **没有** `runtime` 字段，这意味着它运行在 LLM mode——Phoenix 用 LLM 接收消息、做决策，再通过 `sessions_spawn` 工具把任务派发给 Copilot CLI。

---

## 三、基础配置：把群聊消息路由到 agent

### 1. 获取飞书群 ID

群 ID 格式为 `oc_xxx`。在网关运行后 @mention 机器人，然后：

```bash
openclaw logs --follow | grep chat_id
```

### 2. 配置 binding

在 `openclaw.json` 的 `bindings` 数组里加入上面的配置，`peer.id` 填入群 ID。

> 注意：`bindings` 和 `agents.list` 是热重载的，修改后无需重启网关。但 `plugins.entries` 和顶层 `acp` 字段需要完整重启：
> ```bash
> openclaw daemon restart
> ```

### 3. 配置 SOUL.md（关键！）

Phoenix 的行为完全由 `SOUL.md` 定义。要让 Phoenix 在群里收到编程任务时调用 Copilot CLI，需要在 SOUL.md 里明确写死规则：

```markdown
## Hybrid ACP Workflow

你可以通过 sessions_spawn 把编程任务委托给 Copilot CLI：

1. **Plan first** — 分析需求，确定技术方案
2. **Spawn ACP** — 使用 `sessions_spawn({ runtime: "acpx", agentId: "copilot", cwd: "~/workspace-phoenix" })` 启动 Copilot 会话
3. **Monitor** — 通过 session 工具跟踪进度
4. **Report** — 把结果和仓库 URL 发回飞书群

**Rule: 在飞书群里，任何写代码的任务都必须通过 Copilot CLI 完成，禁止直接在聊天里输出代码。**
```

---

## 四、坑一：`/acp` 斜杠命令在普通群里静默失败

### 现象

在飞书群里发送 `/acp 做一个贪吃蛇游戏`，机器人没有任何响应。

查看网关日志：

```
dispatch complete (queuedFinal=false, replies=0)
```

整条消息在 200ms 内被处理完，`replies=0`，说明网关**连 LLM 都没有调用**，直接丢弃了这条消息。

### 诊断

日志时序是关键诊断信号：

| 现象 | 含义 |
|------|------|
| `replies=0`，耗时 < 200ms | 斜杠命令被网关拦截，未传递给 LLM |
| `replies=1`，耗时 15–90s | LLM 正常处理 |
| `replies=1`，耗时 2–5min | LLM 做了繁重工作（如 ACP spawn + 等待） |

### 根因

官方文档明确说明（`docs.openclaw.ai/channels/feishu#acp-sessions`）：

> **v1 does not target generic non-topic group chats.**

`/acp` 系列斜杠命令在 v1 版本中只支持：
- 私聊（DM）
- 飞书话题帖（topic thread）

普通群聊里的 `/acp` 消息会被网关直接吞掉，永远不会到达 LLM。

### 解法

**放弃 `/acp` 斜杠命令**，改用普通消息触发 LLM，由 LLM 自己决定调用 `sessions_spawn`。

---

## 五、坑二：`runtime: "acp"` + `thread: true` 报错

### 现象

改用普通消息后，Phoenix（LLM）能正常收到消息了。在 SOUL.md 里加上 ACP 委托规则后，Phoenix 确实尝试调用了 `sessions_spawn`，但返回了报错：

```json
{
  "status": "error",
  "error": "Could not resolve a feishu conversation for ACP thread spawn."
}
```

### 根因

Phoenix 调用 `sessions_spawn` 时，默认使用了 `runtime: "acp"` 加 `thread: true`：

```json
{
  "task": "...",
  "runtime": "acp",
  "agentId": "copilot",
  "thread": true
}
```

`runtime: "acp"` + `thread: true` 的组合会让网关尝试在当前飞书会话里**创建一个话题帖（topic thread）**，然后把 ACP 会话绑定到这个帖子。问题是：

- 飞书 ACP 的 thread 模式需要 topic 类型的会话
- 普通群聊不支持通过这个路径创建话题
- 结果：`"Could not resolve a feishu conversation"`

### 解法

使用 `runtime: "acpx"` 替代 `runtime: "acp"`，并且**不传 `thread: true`**。

`acpx` 是本地进程模式：Copilot CLI 在本地运行，结果通过工具调用返回给 Phoenix，完全不需要飞书的话题帖功能。

在 SOUL.md 里明确写死：

```markdown
使用 `sessions_spawn({ runtime: "acpx", agentId: "copilot", cwd: "~/workspace-phoenix" })` 启动 Copilot 会话。
**禁止使用 `runtime: "acp"` 或 `thread: true`——普通飞书群不支持话题帖式的 ACP 线程绑定。**
```

---

## 六、正确配置总结

最终跑通的完整配置：

### `openclaw.json`（关键部分）

```json
{
  "acp": { "enabled": true, "backend": "acpx" },
  "plugins": {
    "entries": {
      "acpx": {
        "enabled": true,
        "config": { "permissionMode": "approve-all" }
      }
    }
  },
  "agents": {
    "list": [
      {
        "id": "coding",
        "model": "copilot",
        "tools": { "profile": "full" }
      }
    ]
  },
  "bindings": [
    {
      "agentId": "coding",
      "match": {
        "channel": "feishu",
        "peer": { "kind": "group", "id": "oc_你的群ID" }
      }
    }
  ]
}
```

### SOUL.md 中 ACP 规则的关键行

```
sessions_spawn({ runtime: "acpx", agentId: "copilot", cwd: "~/workspace-phoenix" })
# 不能用 runtime: "acp"，不能用 thread: true
```

### 两条必须遵守的规则

1. **不要用 `/acp` 斜杠命令**——v1 不支持普通群聊
2. **sessions_spawn 用 `runtime: "acpx"`**——不要用 `runtime: "acp"` 或带 `thread: true`

---

## 七、验证：如何确认是 Copilot CLI 在写代码

跑通之后，我想确认活儿确实是 Copilot CLI 干的，而不是 Phoenix 偷偷直接把代码输出到群里了。以下是完整的证据链：

**① `sessions_spawn` 调用记录**

在 Phoenix 的 session 文件（`~/.openclaw/agents/coding/sessions/<uuid>.jsonl`）里，可以找到 `toolCall` 类型的记录：

```json
{
  "type": "toolCall",
  "name": "sessions_spawn",
  "arguments": {
    "runtime": "acpx",
    "agentId": "copilot",
    "task": "Create a browser-based Tic-Tac-Toe project..."
  }
}
```

工具返回值：

```json
{
  "status": "accepted",
  "childSessionKey": "agent:copilot:acp:52b8f9ad-...",
  "runId": "47c8404e-...",
  "mode": "run"
}
```

**② acpx 后端日志**

`gateway.err.log` 里可以看到 acpx 在初始化 Copilot CLI 会话：

```
[plugins] acpx ensureSession repairing dead named session by resuming backend session:
  session=agent:copilot:acp:52b8f9ad-...
  cwd=/Users/phoobobo/workspace-phoenix
```

**③ `agent.wait` 响应**

`gateway.log` 里可以看到 OpenClaw 等待 Copilot CLI 完成的 WebSocket 调用：

```
⇄ res ✓ agent.wait 112062ms
```

等了整整 **112 秒**——这是 Copilot CLI 真正在写代码和推 git 的时间。

**④ 独立的 Copilot CLI session 文件**

`~/.openclaw/agents/copilot/sessions/` 下出现了新的 session 文件，内容是 Copilot CLI 收到任务、逐个创建文件、初始化 git 仓库的完整过程。

**⑤ 文件时间戳与 git commit**

```bash
$ ls -la ~/workspace-phoenix/tic-tac-toe/
# 所有文件时间戳：4月 6 23:47（正好在 session 窗口内）

$ git -C ~/workspace-phoenix/tic-tac-toe log --oneline
7ccd90e (HEAD -> main, tag: v0.1.0, origin/main) Initial commit: add tic-tac-toe game
# commit 时间：2026-04-06 23:47:57 +0800
```

**⑥ GitHub 仓库**

`https://github.com/Phoobobo/tic-tac-toe` — 公开仓库，包含 `index.html`、`style.css`、`app.js`，打开即可玩。

---

## 八、小结

| 问题 | 原因 | 解法 |
|------|------|------|
| `/acp` 命令无响应 | v1 不支持普通群聊斜杠命令 | 改用普通消息，让 LLM 决策 |
| `sessions_spawn` 报 "Could not resolve" | `runtime: "acp"` 需要飞书话题帖 | 改用 `runtime: "acpx"` |
| Phoenix 直接输出代码而不委托 | SOUL.md 里没有明确禁止规则 | 在 SOUL.md 里写死强制规则 |

核心教训：**把规则写进 SOUL.md 时要足够具体**。"可以用 sessions_spawn" 不够，要写成 "必须用 sessions_spawn，用 acpx，禁止用 acp，禁止 thread: true，禁止直接输出代码"。LLM 的默认行为总是走最省力的路——不堵死，它就会抄近道。

---

*相关文章：[我给自己造了一支 AI 团队：OpenClaw 多智能体系统重建实录](/2026/04/05/openclaw-multi-agent-rebuild/)*
