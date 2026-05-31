# B 站视频 → ai-news 调研报告 Pipeline

## 流程总览

```
Bilibili 视频 URL
    ↓
1. opencli bilibili subtitle "BVID" --lang ai-zh -f txt  ← 快路径（秒级）
    ↓ (如果无 AI 字幕则走 bilibili-transcribe skill 的 Whisper 流程)
2. mcp_chrome_devtools 打开页面提取标题/作者/描述
    ↓
3. 阅读完整字幕 → 提炼核心观点、架构、关键数据
    ↓
4. 按 ai-news-research-report skill 的 Phase 2-6 生成 bento HTML
    ↓
5. 运行 `npm run site:update` 同步首页和归档页，再按需要重建搜索索引 (`npm run build:search`) 并 push
```

## 已验证案例

- BV1DB546wEb8（小天fotos "Managed Agents 架构"，11 分钟，308 段字幕）
- 快路径：opencli 直接提取 AI 字幕，无需 Whisper 转录

## 关键注意事项

1. **先试 opencli**：大多数 B 站视频有 AI 字幕，opencli 几秒出结果。只有返回 EMPTY_RESULT 才走 bilibili-transcribe 全流程。
2. **页面元数据**：用 `mcp_chrome_devtools_evaluate_script` 提取标题、UP 主、描述，作为报告的 Hero/Quick Facts 卡片素材。
3. **字幕转内容**：opencli 输出是表格格式，用 `tail` / `head` 控制读取量。字幕中常夹杂语音识别误差（如 "on scorpic" → "Anthropic"），需要理解修正。
4. **参考来源标注**：必须包含视频原链接 + 标注「基于 Bilibili AI 字幕」。
