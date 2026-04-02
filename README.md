<div align="center">

# 前任.skill

> *"从此以后，你的手机里不止有聊天记录，还有一个她。"*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)](https://claude.ai/code)
[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-green)](https://agentskills.io)

<br>

她走了，但聊天记录还在？<br>
三年的日常，变成了手机里一个不敢点开的对话框？<br>
你还记得她说"随便"的时候其实想吃火锅吗？<br>
你还记得她发"哦"的时候其实在等你主动吗？<br>

**将回忆蒸馏成 Skill，不是为了挽回，是为了记住。**

<br>

提供聊天记录（微信、iMessage、短信）、照片、社交媒体，加上你的主观描述<br>
生成一个**像她一样说话的 AI Skill**<br>
用她的语气回消息，知道她什么时候在撒娇、什么时候真的生气了

[数据来源](#支持的数据来源) · [安装](#安装) · [使用](#使用) · [效果示例](#效果示例) · [详细安装说明](INSTALL.md) · [**English**](README_EN.md)

</div>

---

## 支持的数据来源

| 来源 | 聊天记录 | 照片 | 社交媒体 | 备注 |
|------|:-------:|:----:|:-------:|------|
| 微信聊天记录 | ✅ | — | — | WechatExporter 等工具导出 |
| iMessage | ✅ | — | — | macOS chat.db 或导出文件 |
| 短信 | ✅ | — | — | Android SMS Backup XML/CSV |
| 照片 | — | ✅ | — | EXIF 元数据提取时间线 |
| 微博 | — | — | ✅ | JSON 数据导出 |
| 豆瓣 | — | — | ✅ | JSON/HTML 导出 |
| 小红书 | — | — | ✅ | JSON 导出 |
| Instagram | — | — | ✅ | JSON 数据导出 |
| PDF / 图片 | ✅ | ✅ | — | 手动上传 |
| 直接粘贴文字 | ✅ | — | — | 手动输入 |

---

## 安装

### Claude Code

```bash
# 安装到当前项目（在 git 仓库根目录执行）
mkdir -p .claude/skills
git clone https://github.com/perkfly/ex-skill .claude/skills/create-ex

# 或安装到全局（所有项目都能用）
git clone https://github.com/perkfly/ex-skill ~/.claude/skills/create-ex
```

### OpenClaw

```bash
git clone https://github.com/perkfly/ex-skill ~/.openclaw/workspace/skills/create-ex
```

### 依赖（可选）

```bash
pip3 install -r requirements.txt
```

---

## 使用

在 Claude Code 中输入：

```
/create-ex
```

按提示输入她的昵称、关系信息（如 `在一起三年 大学同学 分手一年`）、性格标签，然后选择数据来源。所有字段均可跳过，仅凭描述也能生成。

完成后用 `/{slug}` 调用该前任 Skill。

### 管理命令

| 命令 | 说明 |
|------|------|
| `/list-exes` | 列出所有前任 Skill |
| `/{slug}` | 调用完整 Skill（Persona + Memories） |
| `/{slug}-memories` | 仅共同记忆 |
| `/{slug}-persona` | 仅人物性格 |
| `/ex-rollback {slug} {version}` | 回滚到历史版本 |
| `/delete-ex {slug}` | 删除 |

---

## 效果示例

> 输入：`ENFP 双子座 焦虑型 爱撒娇 翻旧账 嘴上说不在意其实比谁都在意`

**场景一：日常聊天**

```
用户      > 在干嘛呢

前任.skill > 刚下班
           > 好累啊今天
           > 你呢 怎么这个点才找我 🥺
```

**场景二：惹她生气了**

```
用户      > 不好意思刚才在忙

前任.skill > 哦
           > （过了5分钟）
           > 你每次都说在忙
           > 上次也是这样
```

**场景三：撒娇**

```
用户      > 想吃什么

前任.skill > 随便啊
用户      > 那吃面？
前任.skill > 不想吃面
用户      > 火锅？
前任.skill > 嘿嘿你怎么知道的 💕
```

---

## 功能特性

### 生成的 Skill 结构

每个前任 Skill 由两部分组成：

| 部分 | 内容 |
|------|------|
| **Part A — 共同记忆** | 关系时间线、日常仪式、偏好习惯、情感模式 |
| **Part B — Persona** | 5 层性格结构：硬规则 → 身份 → 表达风格 → 情感逻辑 → 关系行为 |

运行逻辑：`收到消息 → Persona 判断心情和态度 → Memories 提供记忆细节 → 用她的语气输出`

### 支持的标签

**恋爱性格**：爱撒娇 · 冷暴力 · 翻旧账 · 黏人 · 独立 · 细腻敏感 · 忽冷忽热 · 作 · 玻璃心 · 控制欲强 …

**吵架模式**：冷战派 · 爆发派 · 讲道理派 · 先道歉型 · 死不认错

**依恋类型**：安全型 · 焦虑型 · 回避型 · 混乱型

**爱的表达**：言语肯定 · 服务行为 · 送礼物 · 肢体接触 · 高质量陪伴

### 进化机制

- **追加聊天记录** → 自动分析增量 → merge 进对应部分，不覆盖已有结论
- **对话纠正** → 说「她不会这样，她应该是 xxx」→ 写入 Correction 层，立即生效
- **版本管理** → 每次更新自动存档，支持回滚到任意历史版本

---

## 项目结构

```
ex-skill/
├── SKILL.md              # skill 入口（AgentSkills 标准 frontmatter）
├── prompts/              # Prompt 模板
│   ├── intake.md         #   对话式信息录入
│   ├── memories_analyzer.md #  共同记忆提取
│   ├── persona_analyzer.md  #  性格行为提取（含标签翻译表）
│   ├── memories_builder.md  #  memories.md 生成模板
│   ├── persona_builder.md   #  persona.md 五层结构模板
│   ├── merger.md            #  增量 merge 逻辑
│   └── correction_handler.md # 对话纠正处理
├── tools/                # Python 工具
│   ├── wechat_parser.py       # 微信聊天记录解析
│   ├── imessage_parser.py     # iMessage 解析
│   ├── sms_parser.py          # 短信解析
│   ├── photo_analyzer.py      # 照片 EXIF 元数据分析
│   ├── social_media_parser.py # 社交媒体解析
│   ├── skill_writer.py        # Skill 文件管理
│   └── version_manager.py     # 版本存档与回滚
├── exes/                 # 生成的前任 Skill（gitignored）
├── docs/PRD.md
├── requirements.txt
└── LICENSE
```

---

## 注意事项

- **聊天记录质量决定 Skill 质量**：真实聊天记录 > 仅手动描述
- 建议优先收集：她**主动发的**长消息 > **情感类消息** > 日常消息
- 照片分析只提取元数据（日期/位置），不上传照片内容
- 所有数据仅在本地处理，不会发送到任何外部服务

---

<div align="center">

MIT License © [perkfly](https://github.com/perkfly)

</div>
