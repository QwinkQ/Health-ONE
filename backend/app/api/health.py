from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.core.schemas import HealthConnectDailySyncRequest, HealthDailyLog, HealthSummaryResponse

router = APIRouter(prefix="/health", tags=["health"])

_daily_logs: dict[str, dict[str, HealthDailyLog]] = {}


@router.post("/connect/sync", response_model=HealthSummaryResponse)
def sync_health_connect_daily_log(request: HealthConnectDailySyncRequest) -> HealthSummaryResponse:
    """Receive a daily aggregate produced by an Android Health Connect client.

    Health Connect permissions and raw record reads happen on-device. The backend
    stores only the user's consented daily aggregate and optional audit samples.
    """

    log = HealthDailyLog(
        user_id=request.user_id,
        date=request.date,
        provider="health_connect",
        steps=request.steps,
        active_energy_kcal=request.active_energy_kcal,
        workout_energy_kcal=request.workout_energy_kcal,
        workout_type=request.workout_type,
        workout_duration_min=request.workout_duration_min,
        body_weight_kg=request.body_weight_kg,
        sleep_minutes=request.sleep_minutes,
        synced_at=datetime.now(timezone.utc).isoformat(),
        raw_samples=request.raw_samples,
    )
    _daily_logs.setdefault(request.user_id, {})[request.date] = log
    return _build_summary(log)


@router.get("/daily-log/{user_id}/{date}", response_model=HealthDailyLog)
def get_health_daily_log(user_id: str, date: str) -> HealthDailyLog:
    log = _daily_logs.get(user_id, {}).get(date)
    if not log:
        raise HTTPException(status_code=404, detail="Health daily log not found")
    return log


@router.get("/summary/{user_id}", response_model=HealthSummaryResponse)
def get_health_summary(user_id: str) -> HealthSummaryResponse:
    logs = _daily_logs.get(user_id, {})
    if not logs:
        return HealthSummaryResponse(
            user_id=user_id,
            latest_log=None,
            target_adjustment={},
            message="还没有同步 Health Connect 数据。可以先手动输入运动消耗，或从 Android 端同步每日汇总。",
        )
    latest = logs[sorted(logs.keys())[-1]]
    return _build_summary(latest)


def _build_summary(log: HealthDailyLog) -> HealthSummaryResponse:
    extra_kcal = round(log.workout_energy_kcal * 0.35, 1)
    protein_hint = "训练日建议优先保证蛋白质，并搭配适量主食帮助恢复。"
    if log.workout_energy_kcal <= 0:
        protein_hint = "今天暂无训练消耗记录，饮食计划按基础目标和步数轻微调整。"

    return HealthSummaryResponse(
        user_id=log.user_id,
        latest_log=log,
        target_adjustment={
            "exercise_energy_kcal": log.workout_energy_kcal,
            "active_energy_kcal": log.active_energy_kcal,
            "suggested_extra_intake_kcal_for_bulking": extra_kcal,
            "suggested_deficit_guard_kcal_for_cutting": "减脂期不建议把运动消耗全部扣掉，优先保持温和缺口。",
        },
        message=protein_hint,
    )
