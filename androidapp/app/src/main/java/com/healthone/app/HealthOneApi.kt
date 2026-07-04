package com.healthone.app

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.io.OutputStreamWriter
import java.net.HttpURLConnection
import java.net.URL

class HealthOneApi(
    private val baseUrl: String = "http://10.0.2.2:8000/api",
) {
    suspend fun syncHealth(log: HealthDailyLog): String = withContext(Dispatchers.IO) {
        val response = postJson("/health/connect/sync", log.toJson())
        val json = JSONObject(response)
        json.optString("message", "健康数据已同步")
    }

    suspend fun chat(userId: String, message: String): String = withContext(Dispatchers.IO) {
        val payload = JSONObject()
            .put("user_id", userId)
            .put("message", message)
        val response = postJson("/chat", payload)
        JSONObject(response).optString("answer", response)
    }

    private fun postJson(path: String, payload: JSONObject): String {
        val connection = (URL("$baseUrl$path").openConnection() as HttpURLConnection).apply {
            requestMethod = "POST"
            setRequestProperty("Content-Type", "application/json; charset=utf-8")
            connectTimeout = 10_000
            readTimeout = 20_000
            doOutput = true
        }
        OutputStreamWriter(connection.outputStream, Charsets.UTF_8).use {
            it.write(payload.toString())
        }
        val stream = if (connection.responseCode in 200..299) {
            connection.inputStream
        } else {
            connection.errorStream
        }
        val body = stream.bufferedReader(Charsets.UTF_8).use { it.readText() }
        if (connection.responseCode !in 200..299) {
            error("后端请求失败：${connection.responseCode} $body")
        }
        return body
    }
}

data class HealthDailyLog(
    val userId: String,
    val date: String,
    val steps: Int,
    val activeEnergyKcal: Double,
    val workoutEnergyKcal: Double,
    val workoutType: String? = null,
    val workoutDurationMin: Int = 0,
    val bodyWeightKg: Double? = null,
    val sleepMinutes: Int? = null,
) {
    fun toJson(): JSONObject {
        return JSONObject()
            .put("user_id", userId)
            .put("date", date)
            .put("timezone", java.time.ZoneId.systemDefault().id)
            .put("steps", steps)
            .put("active_energy_kcal", activeEnergyKcal)
            .put("workout_energy_kcal", workoutEnergyKcal)
            .put("workout_type", workoutType)
            .put("workout_duration_min", workoutDurationMin)
            .put("body_weight_kg", bodyWeightKg)
            .put("sleep_minutes", sleepMinutes)
    }
}
