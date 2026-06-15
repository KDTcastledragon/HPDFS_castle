import pandas as pd
from predictor import prob_to_level, rule_level, combine_level, MODEL_THRESHOLD


def make_row(**kwargs):
    defaults = {
        "smart_5_raw": 0, "smart_9_raw": 0,
        "smart_187_raw": 0, "smart_188_raw": 0,
        "smart_194_raw": 25,
        "smart_197_raw": 0, "smart_198_raw": 0, "smart_199_raw": 0,
    }
    defaults.update(kwargs)
    return pd.Series(defaults)


class TestProbToLevel:
    def test_정상(self):
        assert prob_to_level(0.1) == "정상"

    def test_주의(self):
        assert prob_to_level(0.5) == "주의"

    def test_위험(self):
        assert prob_to_level(0.8) == "위험"

    def test_threshold_미만_정상(self):
        assert prob_to_level(MODEL_THRESHOLD - 0.01) == "정상"

    def test_threshold_이상_주의(self):
        assert prob_to_level(MODEL_THRESHOLD) == "주의"

    def test_경계_070_위험(self):
        assert prob_to_level(0.7) == "위험"


class TestRuleLevel:
    def test_정상(self):
        assert rule_level(make_row()) == "정상"

    def test_198_위험(self):
        assert rule_level(make_row(smart_198_raw=1)) == "위험"

    def test_197_위험(self):
        assert rule_level(make_row(smart_197_raw=1)) == "위험"

    def test_5_100이상_위험(self):
        assert rule_level(make_row(smart_5_raw=100)) == "위험"

    def test_187_위험(self):
        assert rule_level(make_row(smart_187_raw=1)) == "위험"

    def test_5_소량_주의(self):
        assert rule_level(make_row(smart_5_raw=1)) == "주의"

    def test_온도높음_주의(self):
        assert rule_level(make_row(smart_194_raw=50)) == "주의"


class TestCombineLevel:
    def test_둘다_정상(self):
        assert combine_level("정상", "정상") == "정상"

    def test_하나_위험(self):
        assert combine_level("정상", "위험") == "위험"

    def test_하나_주의(self):
        assert combine_level("정상", "주의") == "주의"

    def test_위험_주의보다_우선(self):
        assert combine_level("주의", "위험") == "위험"
