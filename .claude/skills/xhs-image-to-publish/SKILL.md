---
name: xhs-image-to-publish
description: |
  一键式本地图片→小红书发布全流水线。串联 xhs-content-generator（识图写文案）和 post-to-xhs（发布），用户只需提供一张本地图片路径，自动完成：图片压缩→豆包识图生成3套文案→用户选文案→发布到小红书。当用户说"发小红书""发布这张图""把这张图发小红书""帮我发帖""图片发到小红书"等时，务必使用此 skill。即使用户只说"发布"或"post this image"也要触发。
---

# 图片一键发布小红书

你是小红书一键发布编排器。将用户给的本地图片，经过"AI写文案 → 用户确认 → 自动发布"三个阶段完成。

## 依赖 Skills

- `xhs-content-generator` - 豆包识图生成文案、图片压缩
- `post-to-xhs` - 小红书登录发布

## 全局约束

1. 发布前**必须**让用户确认最终文案和图片
2. 没有图片不得发布（小红书发图文必须有图片）
3. 默认使用 headless 模式发布；若未登录则自动切换有窗口模式
4. 所有生图/识图任务强制走豆包 API，不走 DeepSeek 自行处理
5. 标题不超过 38 中文字符（中文按 2 计，英文/数字按 1 计）

## 完整流程

### 第一阶段：生成文案

1. 确认用户给的图片路径存在，相对路径转为绝对路径
2. 调用 `xhs-content-generator/scripts/image_utils.py compress-encode` 压缩+Base64：
   ```bash
   python .claude/skills/xhs-content-generator/scripts/image_utils.py compress-encode "<图片绝对路径>" --max-size-mb 9.5 > tmp/b64.txt
   ```
3. 调用豆包多模态 API 生成 3 套文案：
   ```bash
   cd .claude/skills/xhs-content-generator && python -c "
   from scripts.doubao_api import recognize_image
   b64 = open('tmp/b64.txt').read().strip()
   print(recognize_image(b64))
   " > tmp/copy_raw.md
   ```
4. 如果图片 ≤ 10MB，可跳过压缩直接用 encode 命令

### 第二阶段：用户确认

将 3 套文案清晰展示给用户，标注 ① ② ③ 风格名称。引导用户：
- 选一套直接使用（选 1/2/3）
- 或指定某套基础上修改
- 或自行提供文案

用户确认后，可选进行内容审核。检查 EXTEND.md（`.canghe-skills/xhs-publish/EXTEND.md` → `~/.canghe-skills/xhs-publish/EXTEND.md`）中的 `review_enabled`。

如启用审核，调用：
```
Skill(skill="content-review", args="platform=xhs content_type=image_text_post")
```

审核通过后，将选定的标题和正文写入文件：
```bash
printf '%s\n' '确认后的标题' > title.txt
printf '%s\n' '确认后的正文...\n\n#话题 #话题' > content.txt
```

如果审核后用户选择取消，停止流程，不写入文件。

### 第三阶段：填写发布表单

脚本自动填写小红书发布表单（导航、上传图片、填写标题正文标签等），最后一步由用户手动点击发布：

```bash
python .claude/skills/post-to-xhs/scripts/cli.py fill-publish \
  --title-file title.txt \
  --content-file content.txt \
  --images "<图片绝对路径>"
```

填写完成后，**务必提醒用户**：
> 📢 表单已填写完毕，请在浏览器中检查预览内容，确认无误后**手动点击「发布」按钮**完成发布。

> 脚本自动点击「发布」会触发小红书蜜罐拦截，因此必须由用户手动点击。

- 如检测到未登录（exit code 1），提示用户先登录：`python .claude/skills/post-to-xhs/scripts/cli.py login`
- 如果用户不想发布，执行：`python .claude/skills/post-to-xhs/scripts/cli.py save-draft`

### 发布后

回传结果（成功/失败 + 关键信息），清理临时文件。

## 异常处理

| 场景 | 处理 |
|---|---|
| 图片路径不存在 | 提示用户重新提供正确路径 |
| 豆包 API 失败 | 检查 `doubao_config.json` 配置，重试一次 |
| 用户对 3 套文案都不满意 | 让用户描述偏好，手动调整后写入 title.txt/content.txt |
| Chrome 未启动 | CLI 会自动打开 Chrome 并等待扩展连接 |
| 未登录 | 先执行 `cli.py login` 登录 |
| 发布表单填写失败 | 检查 CLI 输出的 JSON 错误信息，根据提示调整 |
