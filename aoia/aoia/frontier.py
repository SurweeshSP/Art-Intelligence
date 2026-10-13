def get_due_sources(sources):
    return [s for s in sources if s.get("verification") == "PASSED"]
