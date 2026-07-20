import json
import logging
import sys

from app.core.config import settings


class JsonFormatter(logging.Formatter):
    """Formatte chaque log en une ligne JSON (logs structurés, exploitables par un collecteur)."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "time": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        # Champs additionnels passés via logger.info(..., extra={...})
        if hasattr(record, "context") and isinstance(record.context, dict):
            payload.update(record.context)
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def setup_logging() -> None:
    """Configure le logging racine en JSON sur stderr. Idempotent.

    stderr (non bufferisé) et non stdout (bufferisé par blocs en conteneur) : sinon les
    lignes JSON restent coincées dans le buffer et n'atteignent jamais le driver de logs
    Docker -> Fluentd -> Loki en temps réel. Couplé à PYTHONUNBUFFERED=1 (Dockerfile).
    """
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(settings.LOG_LEVEL)

    # Aligne les loggers uvicorn sur le même format
    for name in ("uvicorn", "uvicorn.access", "uvicorn.error"):
        lg = logging.getLogger(name)
        lg.handlers = [handler]
        lg.propagate = False
