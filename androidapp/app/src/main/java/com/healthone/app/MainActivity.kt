package com.healthone.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.health.connect.client.PermissionController
import kotlinx.coroutines.launch

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            HealthOneApp()
        }
    }
}

@Composable
private fun HealthOneApp() {
    val healthConnectManager = remember { HealthConnectManager() }
    val api = remember { HealthOneApi() }
    val scope = rememberCoroutineScope()
    var status by remember { mutableStateOf("准备同步 Health Connect 数据") }
    var prompt by remember {
        mutableStateOf("我今天练胸，消耗 650 kcal，想增肌。冰箱里有鸡胸肉、番茄、鸡蛋、菠菜，不吃香菜。我爸高血压，晚饭也一起吃，30 分钟内完成。")
    }
    var recommendation by remember { mutableStateOf("") }
    var dailyLog by remember { mutableStateOf<HealthDailyLog?>(null) }

    val permissionLauncher = rememberLauncherForActivityResult(
        contract = PermissionController.createRequestPermissionResultContract()
    ) {
        scope.launch {
            status = "权限已返回，正在读取今日健康数据"
            dailyLog = healthConnectManager.readToday(this@MainActivity)
            dailyLog?.let { log ->
                status = api.syncHealth(log)
            }
        }
    }

    LaunchedEffect(Unit) {
        status = healthConnectManager.availabilityMessage(this@MainActivity)
    }

    MaterialTheme {
        Surface(modifier = Modifier.fillMaxSize(), color = Color(0xFFF5F5F7)) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(
                        Brush.verticalGradient(
                            listOf(Color(0xFFF8FBFF), Color(0xFFEFF8F2), Color(0xFFF7F3F7))
                        )
                    )
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .verticalScroll(rememberScrollState())
                        .padding(20.dp),
                    verticalArrangement = Arrangement.spacedBy(18.dp)
                ) {
                    Text("Health ONE", color = Color(0xFF6E6E73), fontWeight = FontWeight.Bold)
                    Text(
                        "你的健康做菜 Agent",
                        fontSize = 42.sp,
                        lineHeight = 44.sp,
                        fontWeight = FontWeight.Black,
                        color = Color(0xFF1D1D1F)
                    )
                    Text(
                        "从 Health Connect 同步每日消耗，再让 Agent 生成训练日晚餐、轻盐改写和购物清单。",
                        color = Color(0xFF5D5D62),
                        fontSize = 17.sp,
                        lineHeight = 24.sp
                    )

                    GlassCard {
                        Text("Google Health Connect", fontWeight = FontWeight.Bold, fontSize = 20.sp)
                        Spacer(Modifier.height(8.dp))
                        Text(status, color = Color(0xFF5D5D62))
                        Spacer(Modifier.height(14.dp))
                        Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                            Button(onClick = {
                                scope.launch {
                                    val granted = healthConnectManager.hasAllPermissions(this@MainActivity)
                                    if (granted) {
                                        status = "正在读取今日健康数据"
                                        dailyLog = healthConnectManager.readToday(this@MainActivity)
                                        dailyLog?.let { status = api.syncHealth(it) }
                                    } else {
                                        permissionLauncher.launch(HealthConnectManager.permissions)
                                    }
                                }
                            }) {
                                Text("同步今日消耗")
                            }
                            OutlinedButton(onClick = {
                                scope.launch {
                                    val demo = HealthDailyLog.demo()
                                    dailyLog = demo
                                    status = api.syncHealth(demo)
                                }
                            }) {
                                Text("模拟数据")
                            }
                        }

                        dailyLog?.let { log ->
                            Spacer(Modifier.height(14.dp))
                            Text("步数 ${log.steps} · 活动 ${log.activeEnergyKcal} kcal · 训练 ${log.workoutEnergyKcal} kcal")
                        }
                    }

                    GlassCard {
                        Text("今天想怎么吃", fontWeight = FontWeight.Bold, fontSize = 20.sp)
                        Spacer(Modifier.height(10.dp))
                        OutlinedTextField(
                            value = prompt,
                            onValueChange = { prompt = it },
                            minLines = 5,
                            modifier = Modifier.fillMaxWidth(),
                            shape = RoundedCornerShape(18.dp)
                        )
                        Spacer(Modifier.height(12.dp))
                        Button(onClick = {
                            scope.launch {
                                recommendation = "生成中..."
                                recommendation = api.chat(prompt)
                            }
                        }) {
                            Text("生成推荐")
                        }
                    }

                    if (recommendation.isNotBlank()) {
                        GlassCard {
                            Text("推荐摘要", fontWeight = FontWeight.Bold, fontSize = 20.sp)
                            Spacer(Modifier.height(10.dp))
                            Text(recommendation, color = Color(0xFF333336), lineHeight = 23.sp)
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun GlassCard(content: @Composable ColumnScope.() -> Unit) {
    Card(
        colors = CardDefaults.cardColors(containerColor = Color.White.copy(alpha = 0.74f)),
        shape = RoundedCornerShape(26.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 0.dp),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.padding(18.dp), content = content)
    }
}
