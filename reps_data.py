reps_data = [
    {
        "id": f"rep{str(i+1).zfill(3)}",
        "name": name,
        "sentiment_score": score,
        "escalations": escalations,
        "calls": [
            {
                "date": "2025-06-11",
                "transcript": f"This is a sample call transcript for {name}. The customer had a {tone} experience.",
                "sentiment": {
                    "outcome": "resolved" if score > 65 else "escalated",
                    "score": round(score / 100, 2)
                }
            },
            {
                "date": "2025-06-10",
                "transcript": f"Another example of customer interaction with {name}.",
                "sentiment": {
                    "outcome": "resolved" if score > 70 else "escalated",
                    "score": round((score - 10) / 100, 2)
                }
            }
        ]
    }
    for i, (name, score, escalations, tone) in enumerate([
        ("Alice Johnson", 85, 2, "positive"),
        ("Bob Smith", 70, 4, "neutral"),
        ("Carla Diaz", 90, 1, "very positive"),
        ("David Kim", 60, 3, "neutral"),
        ("Eva Patel", 77, 2, "generally positive"),
        ("Faisal Khan", 50, 5, "mixed"),
        ("Grace Lee", 95, 0, "excellent"),
        ("Hector Ruiz", 65, 3, "somewhat frustrated"),
        ("Ivy Wang", 88, 1, "smooth"),
        ("Jamal White", 73, 2, "fine"),
        ("Kira Nakamura", 82, 2, "great"),
        ("Liam Novak", 55, 4, "frustrated")
    ])
]

def get_rep_by_id(rep_id):
    return next((rep for rep in reps_data if rep["id"] == rep_id), None)