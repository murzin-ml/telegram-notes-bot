from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True, frozen=True)
class Reminder:
    id: int
    user_key: str
    chat_id: int
    text: str
    fire_at: datetime
    recurrence: str
