"""Command reference engine — lookup and variable substitution."""
from pathlib import Path
import yaml

DATA_DIR = Path(__file__).parent.parent.parent / "data" / "commands"


def load_commands(category: str) -> dict:
    path = DATA_DIR / f"{category}.yaml"
    if not path.exists():
        return None
    with open(path) as f:
        return yaml.safe_load(f)


def get_available_categories() -> list:
    if not DATA_DIR.exists():
        return []
    return [f.stem for f in DATA_DIR.glob("*.yaml")]


def substitute(command: str, **kwargs) -> str:
    """Replace placeholders like {IP}, {USER}, {PASS} with actual values."""
    replacements = {
        "IP": kwargs.get("ip", "{IP}"),
        "USER": kwargs.get("user", "{USER}"),
        "PASS": kwargs.get("password", "{PASS}"),
        "HASH": kwargs.get("hash", "{HASH}"),
        "DOMAIN": kwargs.get("domain", "{DOMAIN}"),
        "PORT": str(kwargs.get("port", "{PORT}")),
        "TARGET_IP": kwargs.get("ip", "{TARGET_IP}"),
    }
    result = command
    for key, val in replacements.items():
        result = result.replace(f"{{{key}}}", val)
    return result


def lookup(query: str, **kwargs) -> list:
    """Search commands across all categories."""
    results = []
    for cat in get_available_categories():
        data = load_commands(cat)
        if not data:
            continue
        for section_name, items in data.get("commands", {}).items():
            for item in items:
                if query.lower() in item.get("description", "").lower() or query.lower() in section_name.lower():
                    results.append({
                        "category": cat,
                        "section": section_name,
                        "description": item["description"],
                        "command": substitute(item["command"], **kwargs),
                    })
    return results
