![Health ONE](pic/pic.png)

# Health One

Health ONE 是一个面向健康饮食的家庭的智能化做菜Agent。项目目标不是只做一个“菜谱聊天机器人”，而是打通：Agent + Function Calling + RAG + DeepSeek + node.js，支持菜谱、营养、食材替换、膳食适配.



## 与普通开源菜谱 Agent / RAG 项目的优势

Health One 的差异在于：

| 对比点 | 普通菜谱 RAG / Agent demo | Health ONE |
|---|---|---|
| 健康数据 | 通常没有真实运动消耗 | Android Health Connect 同步步数、活动消耗、训练、睡眠、体重 |
| 推荐逻辑 | 主要靠 LLM 文本生成 | RAG 检索 + 营养计算工具 + 健康追寻 + 购物清单工具 |
| 健身目标 | 常见只有“减脂/增肌”提示 | 根据每日训练消耗调整热量和蛋白质等建议 |
| 慢病饮食 | 多数只做简单忌口 | 高血压轻盐、糖尿病控糖、肾病谨慎、老人易咀嚼规则 |
| 食材库存 | 常见只输入一次食材 | 设计了冰箱库存、缺少食材、剩菜推荐和购物清单 |
| 可验证性 | LLM 可能编造营养 | 营养计算由后端工具按食材克重计算 |
| 面向家庭场景 | 多数是大菜谱 | 面向中式家常菜、忌口、家庭老人共同用餐 |


Health ONE 的核心优势是把“今天这个时候实际能做什么、适不适合家里所有人吃”连起来。

## 项目结构

```text
backend/     FastAPI 后端、Agent tools、RAG 占位检索、示例数据
frontend/    React + Vite 前端，以及无依赖 standalone 前端
android/     Kotlin + Jetpack Compose + Health Connect Android App
docs/        架构、API、Android、Google Health Connect、测试用例文档
```

## 后端启动

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

后端地址：

```text
http://127.0.0.1:8000
```

接口文档：

```text
http://127.0.0.1:8000/docs
```

```text
我今天练胸，消耗 650 kcal，想增肌。冰箱里有鸡胸肉、番茄、鸡蛋、菠菜，不吃香菜。我爸高血压，晚饭也一起吃，30 分钟内完成。
```

系统会返回：

- 推荐菜谱
- 已有 / 缺少食材
- 营养汇总
- 高血压轻盐提醒
- 购物清单


## Android App

用 Android Studio 打开 `android/` 目录。

安卓端第一版包含：

- Jetpack Compose UI
- Health Connect 权限申请
- 当日步数、活动消耗、训练、睡眠、体重读取
- `POST /api/health/connect/sync` 同步到 FastAPI
- `POST /api/chat` 获取饮食推荐

模拟器访问电脑本机 FastAPI 默认使用：

```text
http://10.0.2.2:8000/api
```

真机调试时，把下面文件里的 `baseUrl` 改成电脑局域网 IP：

```text
android/app/src/main/java/com/healthone/app/HealthOneApi.kt
```
## 基于 Google Health 健康数据

Health ONE 的 MVP 使用 **Google Health Connect** 作为 Android 端健康数据入口，可扩展 Google Health API。

官方参考：

- [Health Connect](https://developer.android.com/health-and-fitness/health-connect)


## Health Connect 数据流

```text
Android App
  -> 请求 Health Connect 权限
  -> 读取 Steps / Calories / Exercise / Sleep / Weight
  -> 汇总为每日健康日志
  -> POST /api/health/connect/sync
  -> FastAPI 后端保存每日汇总
  -> Agent 根据训练消耗调整饮食建议
```

后端不会绕过手机权限直接读取用户健康数据。Health Connect 的授权、读取和权限解释都发生在 Android 设备端；后端只接收用户授权后的每日汇总。
## 后续路线

- 用 Room 缓存 Android 本地健康日志。
- 增加拍照识别冰箱食材。
- 增加家庭成员共享和老人饮食提醒。

## 未来打算打造iOS App

iOS 版使用 **Apple HealthKit**，用现有 FastAPI、菜谱 RAG、营养计算和 Agent 工具链。也就是说，iOS 端只需要负责授权、读取和同步健康数据，不重做后端核心逻辑。

## 参考项目

感谢以下开源项目，Health One的架构、菜谱管理、营养计算和 Agent 工具调用设计等都可以从它们中借鉴。

- [Mealie](https://github.com/mealie-recipes/mealie)：自托管菜谱管理、Meal Plan、购物清单、REST API，最适合参考产品架构。注意 AGPL-3.0。
- [Tandoor Recipes](https://github.com/TandoorRecipes/recipes)：菜谱管理、餐食计划、购物清单，功能很接近基础需求。
- [Grocy](https://github.com/grocy/grocy)：冰箱、家庭库存、保质期、购物管理，非常适合参考“根据剩余食材推荐”。
- [RecipeSage](https://github.com/julianpoy/RecipeSage)：PWA、菜谱保存、Meal Plan、购物清单、营养追踪。
- [PANTS](https://github.com/dylanleigh/PriceAndNutritionTrackingSystem)：开源营养追踪和菜谱营养分析，适合参考营养计算。
- [mealie-cli](https://github.com/jez500/mealie-cli)：把 Mealie 做成 CLI / MCP 风格工具，适合参考 Agent 工具调用设计。
