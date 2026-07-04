# Health ONE Android App

这是 Health ONE 的 Android 原生 App，使用 Kotlin、Jetpack Compose 和 Android Health Connect。

## 功能

- 请求 Health Connect 读取权限。
- 读取当天步数、活动消耗、训练、体重和睡眠。
- 汇总为每日健康日志并同步到 FastAPI：`POST /api/health/connect/sync`。
- 输入食材、忌口、训练和慢病约束后调用：`POST /api/chat`。

## 打开方式

使用 Android Studio 打开 `androidapp/` 目录。

如果提示缺少 `compileSdk 35`，让 Android Studio 自动安装对应 SDK Platform 即可。

模拟器默认后端地址：

```text
http://10.0.2.2:8000/api
```

真机调试时，把 `HealthOneApi.kt` 里的 `baseUrl` 改成电脑局域网 IP。

## 注意

- Health Connect 权限必须由 Android 端请求，后端不能直接读取手机健康数据。
- 新项目优先使用 Health Connect 作为 Android 健康数据入口。
- 当前版本使用内存状态和 `HttpURLConnection`，后续可替换为 Retrofit、Room、Hilt 和 WorkManager。
