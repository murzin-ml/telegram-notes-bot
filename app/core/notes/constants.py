import re

INBOX_FOLDER = "Входящее"
DEFAULT_TITLE = "Заметка"
SNIPPET_LEN = 300
BODY_SEPARATOR = "===BODY==="
JSON_FENCE = re.compile(r"^```(?:json)?|```$", re.MULTILINE)
