#!/usr/bin/env python3
"""
Simple scheduler.
"""

import time
import sys
import os
import json
import subprocess
from os.path import join
from datetime import datetime
import logzero
from logzero import logger
import argparse

__author__ = "Nijraj Gelani"
__version__ = "0.0.1"
__license__ = "MIT"

CWD = os.getcwd()
LOCK_FILE = join(CWD, ".lock")
LOGS_FILE = join(CWD, "logs.log")
SCHEDULES_FILE = join(CWD, "schedules.json")

logzero.logfile(LOGS_FILE)


class Scheduler:
    """Simple process scheduler."""

    def __init__(self, source: str) -> None:
        """Initialize.

        Args:
            source (str): File path to load schedules from.
        """
        self._source = source
        self._schedules = self._load_schedules(source)
        self._original_schedules = {"schedules": self._schedules}

    def _load_schedules(self, source: str) -> list:
        """Load and parse schedules from disk.

        Args:
            source (str): File path to load schedules from.

        Raises:
            ValueError: Invalid schedule; must have `at` and `command`.

        Returns:
            list: List of schedules.
        """
        with open(source, "r", encoding="utf-8") as schedules_file:
            schedules = json.load(schedules_file)
            schedules = schedules.get("schedules", [])
            for schedule in schedules:
                if "at" not in schedule or "command" not in schedule:
                    raise ValueError(
                        "Invalid schedule; must have `at` and `command`"
                    )
                schedule["at"] = datetime.fromisoformat(schedule["at"])
            # sort schedules by time
            schedules.sort(key=lambda x: x["at"])
        return schedules

    def reload(self) -> None:
        """Load schedules from disk."""
        self._schedules = self._load_schedules(self._source)

    def get_wait_time(self) -> int:
        """Get the next schedule time."""
        # TODO: implement smarter wait time based on the schedule
        return 1

    def get_due_tasks(self) -> list:
        """Get list of due commands."""
        now = datetime.now()
        due_tasks = []
        for schedule in self._schedules:
            if (
                now >= schedule["at"].replace(tzinfo=None)
                and schedule.get("completed", False) is False
            ):
                due_tasks.append(schedule["command"])
                schedule["completed"] = True
        with open(self._source, "w", encoding="utf-8") as schedules_file:
            json.dump(
                {"schedules": self._schedules}, schedules_file, default=str
            )
        return due_tasks


def _process_is_running(pid: int) -> bool:
    """Check if process is running.

    Args:
        pid (int): Process ID.

    Returns:
        bool: True if process is running, False otherwise.
    """
    try:
        # Signal 0 does not kill the process, it just checks if it exists.
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True


def _start():
    with open(LOCK_FILE, "r", encoding="utf-8") as lock_file:
        try:
            pid = int(lock_file.read())
            if _process_is_running(pid):
                logger.info("Process already running. PID: %s", pid)
                return
            else:
                logger.info("Process not running. PID: %s; restarting.", pid)
        except ValueError:
            logger.error("Invalid PID in lock file.")
        logger.info("Starting daemon process...")
        try:
            proc = subprocess.Popen(
                [sys.argv[0], "daemon"], preexec_fn=os.setsid
            )
            if proc.pid > 0:
                logger.info("Daemon started. PID: %s", proc.pid)
                with open(LOCK_FILE, "w", encoding="utf-8") as lock_file_w:
                    lock_file_w.write(str(proc.pid))
        except Exception:
            logger.error("Failed to start daemon process.")


def _status():
    with open(LOCK_FILE, "r", encoding="utf-8") as lock_file:
        try:
            pid = int(lock_file.read())
            if _process_is_running(pid):
                print("Status: running")
            else:
                print("Status: stopped")
        except ValueError:
            print("Status: stopped")


def _stop():
    with open(LOCK_FILE, "r", encoding="utf-8") as lock_file:
        try:
            pid = int(lock_file.read())
            if _process_is_running(pid):
                os.killpg(os.getpgid(pid), 9)
                os.remove(LOCK_FILE)
                print("Status: stopped")
            else:
                print("Status: stopped")
        except ValueError:
            print("Status: stopped")


def _daemon():
    scheduler = Scheduler(SCHEDULES_FILE)
    while True:
        scheduler.reload()
        if tasks := scheduler.get_due_tasks():
            print("Executing tasks:", tasks)
        time.sleep(scheduler.get_wait_time())


def main(args):
    """Main entry point of the app"""
    if args.command == "start":
        _start()
    elif args.command == "stop":
        _stop()
    elif args.command == "status":
        _status()
    elif args.command == "daemon":
        _daemon()
    else:
        raise ValueError("unknown command")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # Required positional argument
    parser.add_argument(
        "command",
        choices=["status", "start", "stop", "daemon"],
        help="Required positional argument",
    )

    # Specify output of "--version"
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s (version {version})".format(version=__version__),
    )

    args = parser.parse_args()
    main(args)
