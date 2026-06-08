# Vision Bridge MCP Server 🔍

> 让 Claude Code 拥有视觉能力 —— 通过 Kimi Vision API 理解图片内容

**Vision Bridge** 是一个 MCP (Model Context Protocol) 服务器，它让 Claude Code 能够"看见"并理解图片 —— 截图、图表、照片、UI 界面、错误弹窗、游戏画面等等。

## 🎯 它能做什么

| 场景 | 示例 |
|------|------|
| 🖼️ 截图分析 | 把 GitHub Actions 报错截图发给 Claude，它直接告诉你哪里出了问题 |
| 🎮 游戏画面 | 截取 Unity/Unreal 运行画面，让 Claude 分析渲染 Bug |
| 📊 图表理解 | 发一张流程图/架构图，Claude 帮你解读 |
| 🐛 错误排查 | 错误弹窗截图直接分析，不用手动抄错误信息 |
| 🌐 网页分析 | 网页截图发给 Claude，帮你分析布局、内容、问题 |

## 🏗️ 工作原理

```
┌──────────────┐     ┌─────────────────┐     ┌──────────────────┐
│  Claude Code │────▶│  Vision Bridge  │────▶│  Kimi Vision API │
│  (MCP Client)│◀────│  (MCP Server)   │◀────│  (Moonshot)      │
└──────────────┘     └─────────────────┘     └──────────────────┘
```

1. Claude Code 调用 `describe_image` 工具，传入图片路径
2. Vision Bridge 读取图片，Base64 编码后发给 Kimi Vision API
3. Kimi 返回图片的文字描述
4. Claude 基于描述进行分析、回答、建议

**为什么用 Kimi 而不是其他模型？**
- Kimi 的 Anthropic 兼容端点 → 可直接用 `anthropic` Python SDK
- 中文理解能力强，适合中文用户
- 价格实惠，Moonshot 平台注册即可使用

## 📋 前置条件

### 1. Python 环境

需要 Python 3.10+：

```bash
python --version  # 应该 >= 3.10
```

### 2. Moonshot API Key

1. 打开 [https://platform.moonshot.cn](https://platform.moonshot.cn)
2. 注册/登录账号
3. 进入控制台 → API Keys → 创建新的 API Key
4. 复制密钥（格式：`sk-xxxxxxxxxxxxxxxxxxxxxxxx`）

> ⚠️ **API Key 是敏感信息，永远不要提交到 Git 或公开分享！**

## 📦 安装

### 步骤 1：克隆仓库

```bash
git clone https://github.com/ShaLuuFPS/vision-bridge.git
cd vision-bridge
```

### 步骤 2：安装依赖

```bash
pip install -r requirements.txt
```

或者用虚拟环境（推荐）：

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 步骤 3：配置 Claude Code

在 Claude Code 的 MCP 配置文件中添加 vision-bridge。

**打开配置文件：**

```bash
# 在终端中执行，Claude Code 会打开 mcp.json
claude mcp add
```

或者手动编辑 `~/.claude/mcp.json`（Windows 上是 `C:\Users\你的用户名\.claude\mcp.json`）：

```json
{
  "mcpServers": {
    "vision-bridge": {
      "type": "stdio",
      "command": "python",
      "args": [
        "C:/Users/你的用户名/Desktop/vision-bridge/server.py"
      ],
      "env": {
        "MOONSHOT_API_KEY": "sk-你的密钥"
      }
    }
  }
}
```

> ⚠️ **注意：** 把路径和密钥替换成你自己的！

### 步骤 4：验证安装

重启 Claude Code，然后试试：

```
请描述这张图片：C:\Users\Administrator\Desktop\screenshot.png
```

如果返回了图片描述，说明配置成功 ✅

## 🔧 配置说明

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `MOONSHOT_API_KEY` | **必填** - Moonshot API 密钥 | 无 |
| `ANTHROPIC_BASE_URL` | API 端点地址 | `https://api.moonshot.cn/anthropic` |
| `VISION_MODEL` | 使用的视觉模型 | `kimi-k2.6` |

### 支持的图片格式

PNG · JPG/JPEG · GIF · WebP · BMP

### 更换模型

在 `env` 中设置 `VISION_MODEL`：

```json
"env": {
  "MOONSHOT_API_KEY": "sk-xxx",
  "VISION_MODEL": "kimi-k2.6"
}
```

可用的 Kimi 视觉模型请查看 [Moonshot 官方文档](https://platform.moonshot.cn/docs)。

## 📖 使用示例

### 示例 1：分析错误截图

```
这张 Unity 报错截图是什么意思？怎么修？
C:\Users\Administrator\Desktop\unity-error.png
```

### 示例 2：理解架构图

```
帮我分析这张系统架构图，列出各个模块的职责
C:\projects\docs\architecture.png
```

### 示例 3：检查 UI 设计

```
对比这张 UI 截图和设计稿，找出不一致的地方
C:\projects\screenshots\login-page.png
```

### 示例 4：针对性提问

```
这张图中红色圈出来的按钮是什么文字？
C:\photos\remote-control.jpg
```

## 🐛 常见问题

### Q: 提示 "MOONSHOT_API_KEY not set"

API Key 没配置或配错了：
- 检查 `mcp.json` 中 `env.MOONSHOT_API_KEY` 是否正确
- 确认密钥格式：以 `sk-` 开头
- 确认 Moonshot 账户余额充足

### Q: 提示 "File not found"

- 图片路径必须是**绝对路径**，不能是相对路径
- 路径中包含中文时确保编码正确

### Q: 提示 "Kimi API error"

- 检查网络是否能访问 `api.moonshot.cn`（国内用户一般没问题）
- 海外用户可能需要配置代理
- 确认 API Key 还有额度

### Q: 提示 "Unsupported format"

- 确认图片格式是 PNG/JPG/GIF/WebP/BMP 之一
- 不支持 PDF、SVG、HEIC 等格式

### Q: Claude Code 里看不到 describe_image 工具

1. 确认 `mcp.json` 路径正确
2. 重启 Claude Code
3. 在 Claude Code 中输入 `/mcp` 查看已加载的 MCP 服务器列表

## 🛠️ 开发

### 本地测试

```bash
# 直接运行（stdin/stdout JSON-RPC 模式）
python server.py
```

### 项目结构

```
vision-bridge/
├── server.py          # 主程序 —— 只有一个文件！
├── requirements.txt   # Python 依赖
├── .gitignore         # 防止意外提交敏感文件
├── LICENSE            # MIT 许可证
└── README.md          # 本教程
```

### 扩展

想支持更多功能？`server.py` 只有不到 100 行，很容易修改：

- **支持更多图片格式** → 修改 `media_types` 字典
- **调整输出风格** → 修改 `prompt` 变量
- **支持更多模型** → 修改 `MODEL` 环境变量
- **添加新工具** → 用 `@mcp.tool()` 装饰器添加新函数

## 📄 许可证

MIT License — 详见 [LICENSE](LICENSE)

## 🙏 鸣谢

- [Anthropic MCP SDK](https://github.com/modelcontextprotocol/python-sdk) — MCP Python 框架
- [Moonshot AI](https://www.moonshot.cn/) — Kimi 视觉模型
- Claude Code — 最初帮我们写了这个项目 🤖
