# 前任.skill 安装说明

---

## 选择你的平台

### A. Claude Code（推荐）

本项目遵循官方 [AgentSkills](https://agentskills.io) 标准，整个 repo 就是 skill 目录。克隆到 Claude skills 目录即可：

```bash
# ⚠️ 必须在 git 仓库根目录执行！
cd $(git rev-parse --show-toplevel)

# 方式 1：安装到当前项目
mkdir -p .claude/skills
git clone https://github.com/perkfly/ex-skill .claude/skills/create-ex

# 方式 2：安装到全局（所有项目都能用）
git clone https://github.com/perkfly/ex-skill ~/.claude/skills/create-ex
```

然后在 Claude Code 中说 `/create-ex` 即可启动。

生成的前任 Skill 默认写入 `./exes/` 目录。

---

### B. OpenClaw

```bash
git clone https://github.com/perkfly/ex-skill ~/.openclaw/workspace/skills/create-ex
```

重启 OpenClaw session，说 `/create-ex` 启动。

---

## 依赖安装

```bash
# 基础（Python 3.9+）
pip3 install pypinyin        # 中文姓名转拼音 slug（可选但推荐）

# iMessage 直接读取（macOS）
# 不需要额外依赖，但需要在 系统设置 → 隐私与安全性 → Full Disk Access 中授权终端

# 照片 EXIF 分析
# 不需要额外依赖（使用内置 JPEG EXIF 解析）
# 如需支持更多格式：
pip3 install Pillow          # 支持 HEIC/HEIF/TIFF 等格式的 EXIF 提取
```

---

## 数据来源准备指南

### 微信聊天记录

推荐使用 [WechatExporter](https://github.com/nicktang1990/WechatExporter) 导出：

1. iPhone 通过 iTunes 备份到电脑
2. 运行 WechatExporter，选择对应的聊天
3. 导出为 txt 或 html 格式
4. 在 `/create-ex` 流程中选择 [A] 微信聊天记录

### iMessage

**方式 1：直接读取**（macOS）
- 需要在 系统设置 → 隐私与安全性 → Full Disk Access 中授权终端或 Claude Code
- 使用 `--direct` 参数直接读取

**方式 2：导出文件**
- 使用 [iMazing](https://imazing.com/) 等工具导出
- 导出为 txt 或 csv 格式

### 照片

将相关照片放在一个文件夹中：
- 工具会自动提取 EXIF 元数据（拍摄日期、位置）
- 生成时间线摘要
- 具体照片内容由你选择后通过 Claude 查看

### 社交媒体

**微博**：设置 → 安全中心 → 个人信息与资料下载

**Instagram**：设置 → 你的活动 → 下载你的信息

**小红书/豆瓣**：使用浏览器开发者工具或第三方导出工具

---

## 快速验证

```bash
cd ~/.claude/skills/create-ex   # 或你的项目 .claude/skills/create-ex

# 测试微信解析器
python3 tools/wechat_parser.py --help

# 测试 iMessage 解析器
python3 tools/imessage_parser.py --help

# 测试照片分析器
python3 tools/photo_analyzer.py --help

# 列出已有前任 Skill
python3 tools/skill_writer.py --action list --base-dir ./exes
```

---

## 目录结构说明

```
ex-skill/                 ← clone 到 .claude/skills/create-ex/
├── SKILL.md              # skill 入口（AgentSkills frontmatter）
├── prompts/              # 分析和生成的 Prompt 模板
├── tools/                # Python 工具脚本
├── docs/                 # 文档
│
└── exes/                 # 生成的前任 Skill 存放处（.gitignore 排除）
    └── {slug}/
        ├── SKILL.md              # 完整 Skill（Persona + Memories）
        ├── memories.md           # 共同记忆
        ├── persona.md            # 人物性格
        ├── meta.json             # 元数据
        ├── versions/             # 历史版本
        └── knowledge/            # 原始材料归档
```
