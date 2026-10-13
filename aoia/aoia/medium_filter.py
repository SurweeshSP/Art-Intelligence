from __future__ import annotations

from typing import List, Tuple
import re

DEFAULT_MEDIUM_FILTER = {
    "include": [
        "painting", "drawing", "sculpture", "printmaking", "print making",
        "ceramics", "ceramic", "installation", "mixed media", "textile art",
        "fibre art", "mural", "public art", "contemporary art", "visual art",
        "fine art", "collage", "assemblage", "video art"
    ],
    "exclude": [
        "photography", "photo", "photographer", "photobook",
        "film", "cinema", "documentary",
        "music", "dance", "theatre", "theater", "drama",
        "literature", "poetry",
        "fashion", "graphic design", "architecture", "animation"
    ]
}

def filter_by_medium(text: str, filter_config: dict | None = None) -> Tuple[bool, List[str], List[str]]:
    """Evaluate medium suitability.
    
    Rule:
      Keep if matches >= 1 include term AND is not exclusively matched by exclude terms.
      Photography-only calls are dropped. Multi-disciplinary calls that name a fine-arts medium are kept.
    Returns:
      (keep: bool, matched_includes: List[str], matched_excludes: List[str])
    """
    cfg = filter_config or DEFAULT_MEDIUM_FILTER
    includes = cfg.get("include", DEFAULT_MEDIUM_FILTER["include"])
    excludes = cfg.get("exclude", DEFAULT_MEDIUM_FILTER["exclude"])
    
    low = text.lower()
    matched_inc = [inc for inc in includes if re.search(rf"\b{re.escape(inc.lower())}\b", low)]
    matched_exc = [exc for exc in excludes if re.search(rf"\b{re.escape(exc.lower())}\b", low)]
    
    # If no include term matched, but exclude terms matched -> drop
    if not matched_inc and matched_exc:
        return False, [], matched_exc
        
    # If >=1 include matched: keep, even if exclude terms also matched (e.g. sculpture + photography is kept!)
    if matched_inc:
        return True, matched_inc, matched_exc
        
    # If neither matched: by default fine-arts domain allows general visual calls if no exclusive exclude matched
    return False, [], []
