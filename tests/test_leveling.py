from app.core.models import init_db
from app.core.services.leveling import level_for_score

def test_level_assignment():
    init_db()
    assert level_for_score(0.9, 0.85, 0.6) == 1
    assert level_for_score(0.7, 0.85, 0.6) == 2
    assert level_for_score(0.5, 0.85, 0.6) == 3
