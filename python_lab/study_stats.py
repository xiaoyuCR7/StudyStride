"""StudyStride 学习数据统计模块（开源软件实验二 Python 项目）。"""
from datetime import date, timedelta


def total_minutes(records):
    """累计学习总分钟数。records: [{'date': 'YYYY-MM-DD', 'minutes': int, 'subject': str}]"""
    return sum(r['minutes'] for r in records)


def average_minutes(records):
    """平均每次学习分钟数，空记录返回 0。"""
    if not records:
        return 0
    return total_minutes(records) / len(records)


def filter_by_subject(records, subject):
    """按科目过滤学习记录。"""
    return [r for r in records if r.get('subject') == subject]


def longest_streak(dates):
    """最长连续学习天数。dates: ['YYYY-MM-DD', ...]"""
    if not dates:
        return 0
    days = sorted({date.fromisoformat(d) for d in dates})
    best = cur = 1
    for prev, cur_day in zip(days, days[1:]):
        cur = cur + 1 if cur_day - prev == timedelta(days=1) else 1
        best = max(best, cur)
    return best


def level_of(minutes):
    """按累计分钟数划分学习等级。"""
    if minutes < 60:
        return 'LV1'
    if minutes < 300:
        return 'LV2'
    if minutes < 1000:
        return 'LV3'
    return 'LV4'
