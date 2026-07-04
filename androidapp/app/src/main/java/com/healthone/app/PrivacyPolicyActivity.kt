package com.healthone.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

class PrivacyPolicyActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                Surface(modifier = Modifier.fillMaxSize()) {
                    Column(modifier = Modifier.padding(24.dp)) {
                        Text("Health ONE 隐私说明", style = MaterialTheme.typography.headlineSmall)
                        Text(
                            "Health ONE 只在你授权后读取 Health Connect 中的步数、活动消耗、训练、睡眠和体重数据。" +
                                "当前 MVP 默认上传每日汇总数据到你的本地 FastAPI 服务，用于生成饮食计划。" +
                                "请不要在未告知用户的情况下上传血压、血糖等更敏感的医疗数据。"
                        )
                    }
                }
            }
        }
    }
}

