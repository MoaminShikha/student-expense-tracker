"""Safe file I/O utilities for JSON persistence.

Provides atomic writes and backup mechanisms to prevent data loss
from concurrent access, power failures, or corruption.
"""
from __future__ import annotations

import json
import logging
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)


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

    # Step 1: Create backup of current file if it exists
    if storage_path.exists():
        backup_path = storage_path.with_suffix(".json.bak")
        try:
            shutil.copy2(storage_path, backup_path)
            logger.debug(f"Backup created at {backup_path}")
        except Exception as e:
            logger.warning(f"Failed to create backup: {e}")
            # Don't fail the entire save operation if backup fails

    # Step 2: Write to temporary file
    temp_path = storage_path.with_suffix(".json.tmp")
    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to write temporary file: {e}")
        # Clean up temp file if it exists
        if temp_path.exists():
            temp_path.unlink()
        raise

    # Step 3: Atomically rename temp file to target
    try:
        # On Windows, replace() works atomically after Python 3.8
        # On Unix, rename() is atomic
        temp_path.replace(storage_path)
        logger.debug(f"Data saved to {storage_path}")
    except Exception as e:
        logger.error(f"Failed to move temporary file to target: {e}")
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
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.warning(f"JSON decode failed for {storage_path}: {e}")
            # Fall through to try backup
        except Exception as e:
            logger.warning(f"Failed to read {storage_path}: {e}")
            # Fall through to try backup

    # Try backup file if primary failed
    backup_path = storage_path.with_suffix(".json.bak")
    if backup_path.exists():
        try:
            with open(backup_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                logger.info(f"Recovered data from backup: {backup_path}")
                return data
        except Exception as e:
            logger.warning(f"Failed to read backup {backup_path}: {e}")

    # Both failed or don't exist
    return []
