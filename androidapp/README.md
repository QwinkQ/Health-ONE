# Health ONE Android App

这是 Health ONE 的 Android 原生 App 骨架，使用 Kotlin、Jetpack Compose 和 Android Health Connect。

## 功能

- 请求 Health Connect 读取权限。
- 读取当天步数、活动消耗、训练、体重和睡眠。
- 汇总为每日健康日志并同步到 FastAPI：
  - `POST /api/health/connect/sync`
- 输入食材、忌口、训练和慢病约束后调用：
  - `POST /api/chat`

## 打开方式

用 Android Studio 打开 `android/` 目录。

如果 Android Studio 提示没有 SDK 路径，可以参考 `local.properties.example` 创建 `local.properties`：

```properties
sdk.dir=C\:\\Users\\choej\\AppData\\Local\\Android\\Sdk
```

如果提示缺少 `compileSdk 35`，让 Android Studio 自动安装对应 SDK Platform 即可。

如果使用模拟器，默认后端地址是：

```text
http://10.0.2.2:8000/api
```

如果使用真机，把 `HealthOneApi.kt` 里的 `baseUrl` 改成电脑局域网 IP，例如：

```text
http://192.168.1.10:8000/api
```

## 注意

- Health Connect 权限必须由 Android 端请求，后端不能直接读取手机健康数据。
- Google Fit API 已经进入迁移/弃用期，新项目优先使用 Health Connect。
- MVP 使用内存状态和 `HttpURLConnection`，后续可以替换成 Retrofit、Room、Hilt 和 WorkManager。
