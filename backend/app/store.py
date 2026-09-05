"""JSON-file incident pack store."""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class IncidentStore:
    def __init__(self, data_dir: Path | None = None) -> None:
        root = Path(__file__).resolve().parents[2]
        self.data_dir = Path(data_dir or os.environ.get("DATA_DIR", root / "data" / "incidents"))
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def create(self, pack: dict[str, Any]) -> dict[str, Any]:
        incident_id = pack.get("id") or f"inc-{uuid.uuid4().hex[:10]}"
        pack = {**pack, "id": incident_id, "stored_at": datetime.now(timezone.utc).isoformat()}
        path = self.data_dir / f"{incident_id}.json"
        path.write_text(json.dumps(pack, indent=2))
        return pack

    def get(self, incident_id: str) -> dict[str, Any] | None:
        path = self.data_dir / f"{incident_id}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text())

    def list(self) -> list[dict[str, Any]]:
        items = []
        for path in sorted(self.data_dir.glob("*.json"), reverse=True):
            try:
                items.append(json.loads(path.read_text()))
            except json.JSONDecodeError:
                continue
        return items


store = IncidentStore()
