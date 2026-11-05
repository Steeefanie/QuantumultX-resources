"""以常见实际命名检验地区归类，避免城市名遗漏或将状态条目当作节点。"""
import re
import unittest

from config_templates import REGIONS, region_regex


def groups(name):
    return {label for _,label,expression,_ in REGIONS if re.search(region_regex(expression),name)}


class RegionNamesTests(unittest.TestCase):
    def test_popular_cities_without_country_names(self):
        examples = {
            'Taipei 01':'Taiwan','台北 02':'Taiwan','臺北 03':'Taiwan',
            'LosAngeles 01':'United States','Los Angeles 02':'United States','洛杉磯 03':'United States',
            'SanJose 01':'United States','San Jose 02':'United States',
            'Seattle 01':'United States','New_York 01':'United States','纽约 02':'United States',
            'Toronto 01':'Canada','Vancouver 01':'Canada','溫哥華 02':'Canada',
            'Sydney 01':'Australia','Melbourne 01':'Australia','墨尔本 02':'Australia',
            'Frankfurt 01':'Germany','Berlin 01':'Germany','法蘭克福 02':'Germany',
            '伦敦 01':'United Kingdom','Paris 01':'France',
        }
        for name,expected in examples.items():
            with self.subTest(name=name): self.assertEqual(groups(name),{expected})

    def test_country_names_codes_and_flags_remain_compatible(self):
        examples = [('Hong Kong 01','Hong Kong'),('Tokyo 01','Japan'),('🇸🇬 01','Singapore'),
                    ('Korean 01','South Korea'),('🇮🇩 01','Indonesia'),('TR 01','Turkey'),('US-01','United States')]
        for name,expected in examples:
            with self.subTest(name=name): self.assertEqual(groups(name),{expected})

    def test_status_items_and_ordinary_words_do_not_become_regions(self):
        for name in ('Taipei 剩余流量','LosAngeles Quota','Vancouver Expire',
                     '[BETA-1] HongKong [0.1x]','HongKong Beta 01','US beta',
                     'candidate','shadow','judge'):
            with self.subTest(name=name): self.assertEqual(groups(name),set())
