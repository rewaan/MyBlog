import os

def env_bool(name: str, default: bool = False) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.lower() in ("1", "true", "yes", "on")

def env_list(name: str) -> list[str]:
    v = os.getenv(name, "")
    return [x.strip() for x in v.split(",") if x.strip()]
