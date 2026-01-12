# 音效文件指南

## 音效文件位置

所有音效文件应该放在 `resources/sounds/` 目录下。

## 所需音效文件

以下是游戏使用的音效文件列表：

| 音效文件 | 用途 | 描述 |
|---------|------|------|
| `button_click.wav` | 按钮点击 | 玩家点击任何按钮时播放 |
| `submit.wav` | 提交成语 | 成功提交成语时播放 |
| `hint.wav` | 使用提示 | 使用提示功能时播放 |
| `card_appear.wav` | 卡片出现 | 玩家成语卡片出现时播放 |
| `ai_thinking.wav` | AI思考 | AI正在思考时播放 |
| `victory.wav` | 胜利 | 玩家获胜时播放 |
| `defeat.wav` | 失败 | 玩家失败时播放 |
| `error.wav` | 错误 | 输入错误时播放 |
| `timeout.wav` | 超时 | 游戏超时时播放 |

## 音效文件格式

- **格式**: WAV (推荐), MP3, OGG
- **采样率**: 44100 Hz 或 48000 Hz
- **位深度**: 16-bit 或 24-bit
- **声道**: 单声道或立体声
- **时长**: 建议 1-3 秒（短音效）

## 如何添加音效

### 方法 1: 使用免费音效网站

推荐以下免费音效资源：

1. **Freesound** (https://freesound.org/)
   - 需要注册账号
   - 大量高质量音效
   - 搜索关键词：`button click`, `success`, `fail`, `thinking`

2. **Zapsplat** (https://www.zapsplat.com/)
   - 免费音效库
   - 分类清晰

3. **Mixkit** (https://mixkit.co/free-sound-effects/)
   - 无需注册
   - 高质量音效

### 方法 2: 使用文本转语音 (TTS) 生成

使用在线 TTS 工具生成音效：

1. 访问 https://ttsmp3.com/
2. 输入文字，如 "成功"、"错误"、"胜利"
3. 选择中文语音
4. 下载并重命名

### 方法 3: 使用 AI 生成

使用 AI 音乐生成工具：

- **Suno AI**: https://suno.ai/
- **Udio**: https://www.udio.com/

## 创建 sounds 目录

在项目根目录下执行：

```bash
mkdir -p resources/sounds
```

然后将音效文件放入该目录。

## 音效设置

音效可以在游戏设置中启用/禁用：

1. 点击主菜单的"设置"按钮
2. 找到"界面设置"部分
3. 勾选或取消"启用音效"

## 音量调节

目前音量默认设置为 70%，可以在 `src/utils/sound_manager.py` 中修改：

```python
effect.setVolume(0.7)  # 0.0 到 1.0
```

## 故障排除

### 音效无法播放

1. 检查音效文件是否在正确位置 (`resources/sounds/`)
2. 检查音效文件格式是否支持
3. 确认游戏设置中音效已启用
4. 查看日志文件 `logs/game.log` 中的错误信息

### 音效音量太小

- 检查系统音量设置
- 在代码中调整 `setVolume()` 的值
- 使用音频编辑软件增强音效文件音量

## 推荐音效组合

### 中国风音效推荐

- 按钮点击：轻微的敲击声
- 成功提交：清脆的铃声
- 提示：柔和的水滴声
- 思考：轻柔的古琴声
- 胜利：欢快的锣鼓声
- 失败：低沉的锣声

### 现代风格音效推荐

- 按钮点击：数字按键声
- 成功提交：成功提示音
- 提示：魔法音效
- 思考：加载中的声音
- 胜利：胜利号角
- 失败：失败提示音

## 音频编辑工具推荐

- **Audacity** (免费) - https://www.audacityteam.org/
- **Ocenaudio** (免费) - https://www.ocenaudio.com/
- **Adobe Audition** (付费)

这些工具可以用来：
- 调整音量
- 裁剪音效
- 转换格式
- 添加效果（淡入淡出、回声等）
