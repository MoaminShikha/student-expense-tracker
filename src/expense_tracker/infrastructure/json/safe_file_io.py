"""Safe file I/O utilities for JSON persistence.

Provides atomic writes and backup mechanisms to prevent data loss
from concurrent access, power failures, or corruption.
"""
from __future__ import annotations

import json
import logging
import os
import shutil
import threading
from pathlib import Path

logger = logging.getLogger(__name__)

# One lock per absolute storage path, shared across all repositories in this
# process. Serializes the read-modify-write cycle so GUI worker threads and the
# main thread cannot interleave writes to the same file and clobber each other.
# (Cross-process safety would additionally require an OS-level file lock.)
_path_locks: dict[str, threading.Lock] = {}
_path_locks_guard = threading.Lock()


def _lock_for(storage_path: Path) -> threading.Lock:
    """Return the process-wide lock guarding writes to ``storage_path``."""
    key = str(storage_path.resolve() if storage_path.parent.exists() else storage_path)
    with _path_locks_guard:
        lock = _path_locks.get(key)
        if lock is None:
            lock = _path_locks[key] = threading.Lock()
        return lock


def save_json_safely(storage_path: Path, data: list[dict]) -> None:
    """
    Save JSON data atomically with backup.

    Strategy:
    1. Create backup of current file (if exists)
    2. Write to temporary file
    3. Atomically rename temp file to target path
    4. This ensures corrupt data never overwrites valid data

    :param storage_path: Path to save JSON file
    :param data: Data to serialize
    :return: None
    :raises IOError: If write or rename fails
    """
    storage_path = Path(storage_path)
    storage_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(storage_path.parent, 0o700)
    except OSError:
        pass

    with _lock_for(storage_path):
        _save_json_locked(storage_path, data)


def _save_json_locked(storage_path: Path, data: list[dict]) -> None:
    """Backup + atomic write, assuming the path lock is already held."""
    # Step 1: Create backup of current file if it exists
    if storage_path.exists():
        backup_path = storage_path.with_suffix(".json.bak")
        try:
            shutil.copy2(storage_path, backup_path)
            os.chmod(backup_path, 0o600)
            logger.debug("Backup created at %s", backup_path)
        except Exception as e:
            logger.warning("Failed to create backup: %s", e)
            # Don't fail the entire save operation if backup fails

    # Step 2: Write to temporary file
    temp_path = storage_path.with_suffix(".json.tmp")
    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.chmod(temp_path, 0o600)
    except Exception as e:
        logger.error("Failed to write temporary file: %s", e)
        # Clean up temp file if it exists
        if temp_path.exists():
            temp_path.unlink()
        raise

    # Step 3: Atomically rename temp file to target
    try:
        # On Windows, replace() works atomically after Python 3.8
        # On Unix, rename() is atomic
        temp_path.replace(storage_path)
        logger.debug("Data saved to %s", storage_path)
    except Exception as e:
        logger.error("Failed to move temporary file to target: %s", e)
        # Clean up temp file if it still exists
        if temp_path.exists():
            temp_path.unlink()
        raise


def load_json_safely(storage_path: Path) -> list[dict]:
    """
    Load JSON data with fallback to backup if corruption detected.

    Strategy:
    1. Try loading primary file
    2. If JSON decode fails, try backup file
    3. Return empty list if both fail

    :param storage_path: Path to JSON file
    :return: Loaded data or empty list
    """
    storage_path = Path(storage_path)

    # Try primary file first
    if storage_path.exists():
        try:
            with open(storage_path, "r", encoding="utf-8") as f:
                data: list[dict] = json.load(f)
                return data
        except json.JSONDecodeError as e:
            logger.warning("JSON decode failed for %s: %s", storage_path, e)
            # Fall through to try backup
        except Exception as e:
            logger.warning("Failed to read %s: %s", storage_path, e)
            # Fall through to try backup

    # Try backup file if primary failed
    backup_path = storage_path.with_suffix(".json.bak")
    if backup_path.exists():
        try:
            with open(backup_path, "r", encoding="utf-8") as f:
                backup_data: list[dict] = json.load(f)
                logger.info("Recovered data from backup: %s", backup_path)
                return backup_data
        except Exception as e:
            logger.warning("Failed to read backup %s: %s", backup_path, e)

    # Both failed or don't exist
    return []
