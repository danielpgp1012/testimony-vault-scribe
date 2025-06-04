#!/usr/bin/env python3
"""
Script to run Celery worker locally for development.
Make sure Redis is running before starting this.
"""

import os

from src.app.tasks import celery

if __name__ == "__main__":
    # Set log level
    log_level = os.environ.get("CELERY_LOG_LEVEL", "info")

    print("Starting Celery worker...")
    print(f"Redis URL: {os.environ.get('REDIS_URL', 'redis://localhost:6379/0')}")
    print(f"Log level: {log_level}")
    print("Available tasks:")
    for task_name in celery.tasks:
        if not task_name.startswith("celery."):
            print(f"  - {task_name}")

    # Start the worker
    celery.start(
        [
            "celery",
            "worker",
            "-A",
            "src.app.tasks",
            "--loglevel",
            log_level,
            "--queues",
            "transcription",
            "--concurrency",
            "2",  # Limit concurrency for local development
        ]
    )
