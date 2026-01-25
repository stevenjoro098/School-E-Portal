# exams/utils/cbc_kjsea.py

CBC_KJSEA_SCALE = [
    # Exceeding Expectations
    (90, 100, "EE1", "Exceeding Expectations", 8),
    (75, 89,  "EE2", "Exceeding Expectations", 7),

    # Meeting Expectations
    (58, 74,  "ME1", "Meeting Expectations", 6),
    (41, 57,  "ME2", "Meeting Expectations", 5),

    # Approaching Expectations
    (31, 40,  "AE1", "Approaching Expectations", 4),
    (21, 30,  "AE2", "Approaching Expectations", 3),

    # Below Expectations
    (11, 20,  "BE1", "Below Expectations", 2),
    (1, 10,   "BE2", "Below Expectations", 1),
]


def score_to_cbc(score: int | None):
    """
    Returns:
    {
        level: EE / ME / AE / BE,
        band: EE1, ME2, etc,
        points: int
    }
    """
    if score is None or score <= 0:
        return None

    for low, high, band, level, points in CBC_KJSEA_SCALE:
        if low <= score <= high:
            return {
                "level": level,
                "band": band,
                "points": points,
            }
    return None
