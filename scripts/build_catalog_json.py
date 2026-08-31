import json
import re
from pathlib import Path
from src.catalog import CATALOG

index_path = Path("index.html")
content = index_path.read_text(encoding="utf-8")

catalog_json = json.dumps(CATALOG, ensure_ascii=False, indent=2)

# Replace 'let FULL_CATALOG = [];' with 'let FULL_CATALOG = ' + catalog_json + ';'
pattern = r"let FULL_CATALOG = \[\];"
replacement = f"let FULL_CATALOG = {catalog_json};"

if "let FULL_CATALOG = [];" in content:
    new_content = content.replace("let FULL_CATALOG = [];", replacement)
    index_path.write_text(new_content, encoding="utf-8")
    print("Catalog successfully inlined into index.html!")
else:
    # Try regex
    new_content = re.sub(r"let FULL_CATALOG = .*?;", replacement, content, count=1, flags=re.DOTALL)
    index_path.write_text(new_content, encoding="utf-8")
    print("Catalog updated via regex in index.html!")

