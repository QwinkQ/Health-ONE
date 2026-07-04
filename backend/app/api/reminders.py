from fastapi import APIRouter

router = APIRouter(prefix="/reminders", tags=["reminders"])


@router.get("/{user_id}")
def get_reminders(user_id: str) -> list[dict[str, str]]:
    return [
        {
            "type": "fruit",
            "message": "最近如果连续几天没有水果摄入，可以补充一份低负担水果，例如苹果或浆果。",
        },
        {
            "type": "sodium",
            "message": "如有高血压，今天做饭建议少盐少生抽，优先蒸煮炖。",
        },
    ]

