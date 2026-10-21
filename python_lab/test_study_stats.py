from study_stats import (average_minutes, filter_by_subject, longest_streak,
                         level_of, total_minutes)

RECORDS = [
    {'date': '2026-10-01', 'minutes': 45, 'subject': 'math'},
    {'date': '2026-10-02', 'minutes': 60, 'subject': 'english'},
    {'date': '2026-10-03', 'minutes': 30, 'subject': 'math'},
]


def test_total_minutes():
    assert total_minutes(RECORDS) == 135


def test_average_minutes():
    assert average_minutes(RECORDS) == 45.0
    assert average_minutes([]) == 0


def test_filter_by_subject():
    maths = filter_by_subject(RECORDS, 'math')
    assert len(maths) == 2
    assert total_minutes(maths) == 75


def test_longest_streak():
    assert longest_streak(['2026-10-01', '2026-10-02', '2026-10-03']) == 3
    assert longest_streak(['2026-10-01', '2026-10-03']) == 1
    assert longest_streak([]) == 0


def test_level_of():
    assert level_of(30) == 'LV1'
    assert level_of(120) == 'LV2'
    assert level_of(500) == 'LV3'
    assert level_of(2000) == 'LV4'
