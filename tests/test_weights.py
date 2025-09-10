from app.core.utils.calc import normalize_weights

def test_normalize_basic():
    assert sum(normalize_weights([0.2,0.3,0.5])) == 1.0

def test_normalize_zero_sum():
    w = normalize_weights([0,0,0])
    assert len(w)==3 and abs(sum(w)-1.0) < 1e-9

def test_normalize_negative():
    w = normalize_weights([-1, 0.2])
    assert abs(sum(w)-1.0) < 1e-9 and w[0] == 0.0
