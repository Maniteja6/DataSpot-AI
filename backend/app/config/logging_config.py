"""
Logging configuration. Locally this logs structured lines to stdout; when
deployed to AWS (ECS/Fargate), stdout is captured by the awslogs driver into
the CloudWatch log groups defined in infra/aws/cloudwatch_log_groups.yaml —
so no separate CloudWatch SDK wiring is needed in application code.
"""

import logging
import sys
from app.config.settings import get_settings


def configure_logging() -> None:
    settings = get_settings()

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(settings.log_level.upper())

    # Quiet noisy third-party loggers unless we're debugging.
    for noisy in ("botocore", "boto3", "urllib3", "httpx"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
