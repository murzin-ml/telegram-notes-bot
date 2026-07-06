import re

INVALID_CHARS = re.compile(r'[<>:"/\\|?*\n\r]+')
MAX_TITLE_LEN = 80
FALLBACK_NAME = "Заметка"
