"""Generic JSON repository base.

Holds the load/save/cache machinery that every list-backed adapter shared, and
delegates (de)serialization to a :class:`~..mappers.Mapper`. Concrete repos only
declare their queries.

Caching: records are reloaded only when the file's modification time changes, so
repeated reads in a single process no longer re-parse the whole file on every
call. A cross-process writer is still observed because the cache key is the
on-disk mtime.
"""
from __future__ import annotations

from pathlib import Path
from typing import Generic, Protocol, TypeVar

from ..safe_file_io import load_json_safely, save_json_safely

T = TypeVar("T")


class _Mapper(Protocol[T]):
    def from_dict(self, record: dict) -> T: ...
    def to_dict(self, entity: T) -> dict: ...


class JsonStore(Generic[T]):
    """Base adapter for a list of entities persisted to one JSON file."""

    def __init__(self, storage_path: Path | str, mapper: _Mapper[T]) -> None:
        """
        :param storage_path: Path to the JSON storage file.
        :param mapper: Mapper translating entities to and from records.
        """
        self._storage_path: Path = Path(storage_path)
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._mapper = mapper
        self._cache: list[dict] | None = None
        self._cache_key: int | None = None

    def _records(self) -> list[dict]:
        """Return a private copy of the raw records, using an mtime-keyed cache."""
        key = self._storage_path.stat().st_mtime_ns if self._storage_path.exists() else None
        if self._cache is None or key != self._cache_key:
            self._cache = load_json_safely(self._storage_path)
            self._cache_key = key
        return [dict(record) for record in self._cache]

    def _all(self) -> list[T]:
        """Return every stored entity, deserialized."""
        return [self._mapper.from_dict(record) for record in self._records()]

    def _persist(self, records: list[dict]) -> None:
        """Atomically write ``records`` and refresh the cache."""
        save_json_safely(self._storage_path, records)
        self._cache = [dict(record) for record in records]
        self._cache_key = None  # force mtime re-read on next _records() call

    def _append(self, entity: T) -> None:
        """Serialize and append one entity."""
        records = self._records()
        records.append(self._mapper.to_dict(entity))
        self._persist(records)

    def _delete_by_id(self, id_field: str, id_value: str) -> bool:
        """Remove the record with the given id field value. Returns True if removed."""
        records = self._records()
        new_records = [r for r in records if str(r.get(id_field)) != id_value]
        if len(new_records) == len(records):
            return False
        self._persist(new_records)
        return True
