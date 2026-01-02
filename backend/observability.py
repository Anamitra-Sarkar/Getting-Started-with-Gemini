import logging
import json


class JSONFormatter(logging.Formatter):
    def format(self, record):
        payload = {
            "name": record.name,
            "level": record.levelname,
            "msg": record.getMessage(),
            "time": self.formatTime(record, self.datefmt),
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload)


def setup_logging(level=logging.INFO):
    logger = logging.getLogger()
    logger.setLevel(level)
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    logger.handlers = [handler]
    return logger


logger = setup_logging()
