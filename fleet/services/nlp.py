import re

SEVERITY_KEYWORDS = {
    "critical": ["mayday", "sos", "fire", "explosion", "piracy", "taking on water", "capsize"],
    "warning": ["engine", "steering", "leak", "medical", "injury", "collision", "grounding"],
}

PROBLEM_KEYWORDS = {
    "fire": ["fire", "smoke", "explosion"],
    "engine": ["engine", "power", "propulsion"],
    "collision": ["collision", "impact", "hit"],
    "leak": ["leak", "taking on water", "flood"],
    "medical": ["medical", "injury", "injured", "wounded"],
    "piracy": ["piracy", "hijack", "boarding"],
    "navigation": ["grounding", "stuck", "reef"],
}

INJURY_PATTERN = re.compile(r"(\d+)\s*(injured|injuries|wounded|casualties)", re.I)


def parse_distress(message: str) -> dict:
    normalized = message.lower()
    severity = "info"
    for level, keywords in SEVERITY_KEYWORDS.items():
        if any(keyword in normalized for keyword in keywords):
            severity = level
            break

    if severity == "info" and any(
        keyword in normalized for keyword in SEVERITY_KEYWORDS["warning"]
    ):
        severity = "warning"

    problems = []
    for problem, keywords in PROBLEM_KEYWORDS.items():
        if any(keyword in normalized for keyword in keywords):
            problems.append(problem)

    injuries = None
    match = INJURY_PATTERN.search(normalized)
    if match:
        injuries = int(match.group(1))

    summary = problems[0] if problems else "unknown issue"

    return {
        "severity": severity,
        "problems": problems,
        "injuries": injuries,
        "summary": summary,
    }
