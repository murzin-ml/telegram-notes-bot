import re

INBOX_FOLDER = "Входящее"
DEFAULT_TITLE = "Заметка"
SNIPPET_LEN = 300
JSON_FENCE = re.compile(r"^```(?:json)?|```$", re.MULTILINE)
