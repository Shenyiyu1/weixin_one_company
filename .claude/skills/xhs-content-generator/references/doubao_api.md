# 豆包（Doubao）API 参数参考

## 配置说明

配置文件：`config/doubao_config.json`

| 字段 | 必填 | 说明 |
|---|---|---|
| `api_key` | 是 | 豆包开放平台 API Key（在火山引擎方舟平台创建） |
| `base_url` | 是 | API 基础地址 |
| `multimodal_endpoint` | 否 | 多模态识图接口路径，默认 `chat/completions` |
| `multimodal_model` | 否 | 多模态模型 ID，默认 `doubao-vision-pro-32k` |
| `image_gen_endpoint` | 否 | 文生图接口路径，默认 `images/generations` |
| `image_gen_model` | 否 | 文生图模型 ID，默认 `doubao-seedream-4.0` |

## 获取 API Key

1. 登录火山引擎方舟平台：https://console.volcengine.com/ark
2. 创建 API Key（接入点 → API Key 管理）
3. 确保已开通所需模型服务（多模态模型 + 文生图模型）
4. 将 API Key 填入 `config/doubao_config.json`

## 支持的模型

### 多模态模型（识图写文案）
- `doubao-vision-pro-32k`：高精度视觉理解，适合复杂场景
- `doubao-vision-pro-128k`：支持更长上下文

### 文生图模型
- `doubao-seedream-4.0`：最新版本，画质最佳

## API 调用限制

- 单次请求图片 Base64 不超过 10MB
- 文生图默认单次生成 1 张
- 建议生图尺寸使用小红书竖版比例 768:1024
