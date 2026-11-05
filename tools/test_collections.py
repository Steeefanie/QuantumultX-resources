"""核查完整分类构建、集合属性、离线复现及校验失败处理。"""
import contextlib
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest.mock import patch

import build
from query import find_matches, parse_domain


class CollectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.addCleanup(patch.stopall)
        patch.object(build, 'ROOT', self.root).start()
        self.data = {
            'a':'full:api.example.com\nexample.org\nads.example.org @ads\n',
            'b':'b.example\n',
            'category-demo':'include:a\ninclude:b\n',
            'category-ads':'include:a @ads\n',
            'regexp-only':'regexp:^special.*$\n',
        }
        self.manifest = {
            'schema':2, 'annotation_date':'2026-10-21', 'services':{'a':'示例服务'}, 'all_services':True, 'all_collections':True,
            'collections':{'combined':{'title':'示例集合', 'include':['category-demo'], 'policy':'direct'},
                           'other':{'title':'其他策略集合', 'include':['a'], 'policy':'proxy'}},
        }
        (self.root/'sources').mkdir()
        self.write_manifest()

    def write_manifest(self):
        (self.root/'sources/selection.json').write_text(json.dumps(self.manifest))

    def archive(self):
        content = io.BytesIO()
        with tarfile.open(fileobj=content, mode='w:gz', format=tarfile.PAX_FORMAT,
                          pax_headers={'comment':'a'*40}) as archive:
            for name, text in {**{f'data/{n}':v for n,v in self.data.items()},
                               'LICENSE':'MIT License\nCopyright Test\n'}.items():
                data = text.encode(); info = tarfile.TarInfo('source/'+name); info.size = len(data)
                archive.addfile(info, io.BytesIO(data))
        return content.getvalue()

    def build(self):
        with contextlib.redirect_stdout(io.StringIO()):
            build.build(self.archive())
            build.validate()

    def test_auto_expansion_preserves_ads_separation_and_does_not_publish_empty_files(self):
        self.build()
        service = (self.root/'filter/services/a.list').read_text()
        block = (self.root/'filter/collections/category-ads.list').read_text()
        combined = (self.root/'filter/collections/combined.list').read_text()
        other = (self.root/'filter/collections/other.list').read_text()
        lock = json.loads((self.root/'sources/lock.json').read_text())
        self.assertNotIn('host-suffix, ads.example.org,', service)
        self.assertIn('host-suffix, ads.example.org, reject', block)
        self.assertIn('host, api.example.com, direct', combined)
        self.assertIn('host-suffix, b.example, direct', combined)
        self.assertIn('host, api.example.com, proxy', other)
        self.assertFalse((self.root/'filter/services/regexp-only.list').exists())
        self.assertEqual(lock['未生成分类数'], 1)
        self.assertFalse((self.root/'metadata').exists())
        self.assertFalse((self.root/'catalog').exists())
        self.assertFalse((self.root/'reports').exists())

    def test_rebuild_is_offline_and_keeps_original_archive_hash(self):
        self.build()
        before = {p.relative_to(self.root):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        with patch.object(build.urllib.request, 'urlopen', side_effect=AssertionError('不得联网')):
            with contextlib.redirect_stdout(io.StringIO()):
                build.rebuild()
        self.assertEqual(before, {p.relative_to(self.root):p.read_bytes() for p in self.root.rglob('*') if p.is_file()})

    def test_check_rejects_tampered_lock_or_unknown_rule_file(self):
        self.build()
        lock_file = self.root/'sources/lock.json'; original = lock_file.read_bytes()
        tampered = json.loads(original.decode('utf-8'))
        tampered['域名规则数'] = 999999
        lock_file.write_text(json.dumps(tampered))
        with self.assertRaisesRegex(ValueError, 'sources/lock.json'):
            build.validate()
        lock_file.write_bytes(original)
        (self.root/'filter/services/unknown.list').write_text('host-suffix, unsafe.example, proxy\n')
        with self.assertRaisesRegex(ValueError, '不在构建计划'):
            build.validate()

    def test_bad_reference_does_not_replace_existing_outputs(self):
        self.build()
        previous = (self.root/'filter/collections/combined.list').read_bytes()
        self.manifest['collections']['combined']['include'] = ['missing']
        self.write_manifest()
        with self.assertRaisesRegex(ValueError, '不存在'):
            build.build(self.archive())
        self.assertEqual(previous, (self.root/'filter/collections/combined.list').read_bytes())

    def test_snapshot_tampering_fails_before_rebuild(self):
        self.build()
        (self.root/'sources/v2fly/data/a').write_text('compromised.example\n')
        with self.assertRaisesRegex(ValueError, '快照与锁定记录不一致'):
            build.rebuild()

    def test_query_reports_file_policy_but_does_not_match_sibling_domains(self):
        self.build()
        matches = find_matches('api.example.com', self.root)
        self.assertTrue(any(p == 'filter/services/a.list' for p, *_ in matches))
        self.assertTrue(any(p == 'filter/collections/combined.list' and policy == 'direct'
                            for p,kind,value,policy in matches))
        self.assertEqual(find_matches('badexample.org', self.root), [])
        self.assertTrue(all(p.startswith('filter/collections/') for p,*_ in find_matches('a.example.org', self.root,'collections')))
        self.assertEqual(parse_domain('https://API.Example.com/path?key=value'), 'api.example.com')
        with self.assertRaises(ValueError):
            parse_domain('example.org?query')

    def test_group_prefix_does_not_treat_filtered_inclusion_as_full_containment(self):
        self.data['parent'] = 'include:a\ninclude:b @ads\n'
        self.manifest['group_roots'] = ['parent']
        self.write_manifest()
        self.build()
        self.assertTrue((self.root/'filter/services/parent-a.list').is_file())
        self.assertTrue((self.root/'filter/services/b.list').is_file())
        self.assertFalse((self.root/'filter/services/parent-b.list').exists())
        text = (self.root/'filter/services/parent-a.list').read_text()
        self.assertIn('本地整理日期：2026-10-21', text)
        self.assertIn('非上游更新时间', text)
        self.assertIn('具体运营主体未逐项核实', text)

    def test_filename_collision_does_not_overwrite_another_service(self):
        self.build()
        previous = (self.root/'filter/services/b.list').read_bytes()
        self.manifest['filename_overrides'] = {'a':'b'}
        self.write_manifest()
        with self.assertRaisesRegex(ValueError, '文件名冲突'):
            build.build(self.archive())
        self.assertEqual(previous, (self.root/'filter/services/b.list').read_bytes())

    def test_exclusion_removes_dedicated_hosts_but_reports_broad_shared_parent(self):
        kept, removed, broad = build.exclude_conditions(
            {('host-suffix','google.com'), ('host-suffix','youtube.com'),
             ('host','api.youtube.com'), ('host-suffix','docs.google.com')},
            {('host-suffix','youtube.com'), ('host','wide-youtube.l.google.com')})
        self.assertEqual(removed, {('host-suffix','youtube.com'), ('host','api.youtube.com')})
        self.assertIn(('host-suffix','google.com'), kept)
        self.assertIn(('host-suffix','docs.google.com'), kept)
        self.assertIn(('host-suffix','google.com','host','wide-youtube.l.google.com'), broad)

    def test_collection_exclusion_works_in_generated_body_and_keeps_audit_record(self):
        self.manifest['collections']['combined']['exclude'] = ['a']
        self.write_manifest()
        self.build()
        text = (self.root/'filter/collections/combined.list').read_text()
        self.assertNotIn('host, api.example.com, direct', text)
        self.assertIn('host-suffix, b.example, direct', text)
        self.assertIn('# 排除分类：a；', text)

    def test_personal_profile_keeps_resources_and_policy_assignments_separate(self):
        self.manifest['personal_profiles'] = {'demo':[
            {'kind':'service','source':'a','tag':'服务A','policy':'美国节点'},
            {'kind':'service','source':'b','tag':'服务B','policy':'direct'},
        ]}
        self.write_manifest()
        self.build()
        text = (self.root/'examples/quantumult_demo.conf').read_text()
        self.assertIn('filter/services/a.list, tag=服务A, force-policy=美国节点,', text)
        self.assertIn('filter/services/b.list, tag=服务B, force-policy=direct,', text)
        self.assertFalse((self.root/'filter/collections/demo.list').exists())

    def test_personal_profile_rejects_policy_injection_before_writing(self):
        self.manifest['personal_profiles'] = {'demo':[
            {'kind':'service','source':'a','tag':'服务A','policy':'direct, enabled=true'},
        ]}
        self.write_manifest()
        with self.assertRaisesRegex(ValueError, '策略名不合法'):
            build.build(self.archive())
        self.assertFalse((self.root/'examples/quantumult_demo.conf').exists())


if __name__ == '__main__':
    unittest.main()
