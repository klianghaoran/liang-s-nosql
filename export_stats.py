import json
from pathlib import Path
from db import get_db
from stats import category_stats, save_category_stats

db = get_db()
rows = save_category_stats(db)
out = Path("reports/category_stats.json")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(rows, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
print(json.dumps({"rows": len(rows), "file": str(out)}, ensure_ascii=False))
