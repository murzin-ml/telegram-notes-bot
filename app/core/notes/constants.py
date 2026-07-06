import re

INBOX_FOLDER = "Входящее"
DEFAULT_TITLE = "Заметка"
JSON_FENCE = re.compile(r"^```(?:json)?|```$", re.MULTILINE)
