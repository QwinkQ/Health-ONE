package com.healthone.app

import android.content.Context
import androidx.health.connect.client.HealthConnectClient
import androidx.health.connect.client.PermissionController
import androidx.health.connect.client.permission.HealthPermission
import androidx.health.connect.client.records.ActiveCaloriesBurnedRecord
import androidx.health.connect.client.records.ExerciseSessionRecord
import androidx.health.connect.client.records.SleepSessionRecord
import androidx.health.connect.client.records.StepsRecord
import androidx.health.connect.client.records.TotalCaloriesBurnedRecord
import androidx.health.connect.client.records.WeightRecord
import androidx.health.connect.client.request.AggregateRequest
import androidx.health.connect.client.request.ReadRecordsRequest
import androidx.health.connect.client.time.TimeRangeFilter
import java.time.LocalDate
import java.time.ZoneId
import kotlin.math.roundToInt

class HealthConnectManager {
    suspend fun hasAllPermissions(context: Context): Boolean {
        val client = HealthConnectClient.getOrCreate(context)
        return client.permissionController.getGrantedPermissions().containsAll(permissions)
    }

    fun availabilityMessage(context: Context): String {
        return when (HealthConnectClient.getSdkStatus(context)) {
            HealthConnectClient.SDK_AVAILABLE -> "Health Connect 可用，可以同步每日消耗。"
            HealthConnectClient.SDK_UNAVAILABLE_PROVIDER_UPDATE_REQUIRED -> "需要安装或更新 Health Connect。"
            else -> "当前设备暂不支持 Health Connect。"
        }
    }

    suspend fun readToday(context: Context): HealthDailyLog {
        val client = HealthConnectClient.getOrCreate(context)
        val zone = ZoneId.systemDefault()
        val start = LocalDate.now(zone).atStartOfDay(zone).toInstant()
        val end = LocalDate.now(zone).plusDays(1).atStartOfDay(zone).toInstant()
        val filter = TimeRangeFilter.between(start, end)

        val aggregate = client.aggregate(
            AggregateRequest(
                metrics = setOf(
                    StepsRecord.COUNT_TOTAL,
                    ActiveCaloriesBurnedRecord.ACTIVE_CALORIES_TOTAL,
                    TotalCaloriesBurnedRecord.ENERGY_TOTAL,
                ),
                timeRangeFilter = filter,
            )
        )

        val exercises = client.readRecords(
            ReadRecordsRequest(
                recordType = ExerciseSessionRecord::class,
                timeRangeFilter = filter,
            )
        ).records

        val sleeps = client.readRecords(
            ReadRecordsRequest(
                recordType = SleepSessionRecord::class,
                timeRangeFilter = filter,
            )
        ).records

        val weights = client.readRecords(
            ReadRecordsRequest(
                recordType = WeightRecord::class,
                timeRangeFilter = filter,
            )
        ).records

        val steps = aggregate[StepsRecord.COUNT_TOTAL]?.toInt() ?: 0
        val activeKcal = aggregate[ActiveCaloriesBurnedRecord.ACTIVE_CALORIES_TOTAL]?.inKilocalories ?: 0.0
        val totalKcal = aggregate[TotalCaloriesBurnedRecord.ENERGY_TOTAL]?.inKilocalories ?: activeKcal
        val workoutDuration = exercises.sumOf {
            java.time.Duration.between(it.startTime, it.endTime).toMinutes().toInt()
        }
        val sleepMinutes = sleeps.sumOf {
            java.time.Duration.between(it.startTime, it.endTime).toMinutes().toInt()
        }
        val weightKg = weights.maxByOrNull { it.time }?.weight?.inKilograms

        return HealthDailyLog(
            userId = "demo-user",
            date = LocalDate.now(zone).toString(),
            steps = steps,
            activeEnergyKcal = activeKcal.round1(),
            workoutEnergyKcal = (totalKcal - activeKcal).coerceAtLeast(0.0).round1(),
            workoutType = exercises.firstOrNull()?.exerciseType?.toString(),
            workoutDurationMin = workoutDuration,
            bodyWeightKg = weightKg?.round1(),
            sleepMinutes = sleepMinutes.takeIf { it > 0 },
        )
    }

    private fun Double.round1(): Double = (this * 10).roundToInt() / 10.0

    companion object {
        val permissions = setOf(
            HealthPermission.getReadPermission(StepsRecord::class),
            HealthPermission.getReadPermission(ActiveCaloriesBurnedRecord::class),
            HealthPermission.getReadPermission(TotalCaloriesBurnedRecord::class),
            HealthPermission.getReadPermission(ExerciseSessionRecord::class),
            HealthPermission.getReadPermission(WeightRecord::class),
            HealthPermission.getReadPermission(SleepSessionRecord::class),
        )
    }
}

