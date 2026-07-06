import asyncio
import logging

from app.infra.git.constants import GIT_OK

logger = logging.getLogger(__name__)


class GitSync:
    def __init__(self, repo_path: str, push: bool) -> None:
        self._path = repo_path
        self._push = push

    async def commit(self, message: str) -> None:
        try:
            await self._run("git", "add", "-A")
            code, _ = await self._run("git", "commit", "-m", message)
            if code != GIT_OK:
                return
            if self._push:
                push_code, err = await self._run("git", "push")
                if push_code != GIT_OK:
                    logger.warning("git push не удался: %s", err.strip())
        except FileNotFoundError:
            logger.warning("git не найден — синхронизация пропущена")
        except OSError:
            logger.exception("git синхронизация не удалась")

    async def _run(self, *args: str) -> tuple[int, str]:
        proc = await asyncio.create_subprocess_exec(
            *args,
            cwd=self._path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await proc.communicate()
        return proc.returncode or GIT_OK, stderr.decode(errors="ignore")
