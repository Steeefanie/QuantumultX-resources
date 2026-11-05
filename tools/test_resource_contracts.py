"""核对用户确认的网络/策略约定，以及实际输出的资源引用和原文保留。"""
import csv
import json
from pathlib import Path
import re
import unittest

from config_templates import RAW_ROOT, REGIONS, render_full_config

ROOT = Path(__file__).resolve().parents[1]


def sections(text):
    result={};section=''
    for line in text.splitlines():
        line=line.strip()
        if not line or line.startswith(('#',';','//')): continue
        if re.fullmatch(r'\[.*\]',line):
            section=line[1:-1];result.setdefault(section,[])
        else:result.setdefault(section,[]).append(line)
    return result


class ConfigurationContractTests(unittest.TestCase):
    def setUp(self):
        self.fragment='[filter_remote]\n'+RAW_ROOT+'/filter/services/openai.list, tag=OpenAI, force-policy=Global, enabled=true\n'
        self.rendered=render_full_config('test',self.fragment,'2026-11-04')
        self.config=sections(self.rendered)

    def test_network_settings_follow_approved_legacy_fixture(self):
        legacy=sections((ROOT/'tools/fixtures/network-legacy.conf').read_text())
        normalize=lambda values:[v.replace(' ','') for v in values]
        self.assertEqual(normalize(self.config['dns']),normalize(legacy['dns']))
        actual={x.partition('=')[0].strip():x.partition('=')[2].replace(' ','') for x in self.config['general']}
        for line in legacy['general']:
            key,_,value=line.partition('=')
            self.assertEqual(actual[key.strip()],value.replace(' ',''))

    def test_proxy_only_selects_regions_and_regions_benchmark_nodes(self):
        policies=self.config['policy']
        proxy=next(x for x in policies if x.startswith('static = Global,'))
        candidates=[p.strip() for p in proxy.split(',')[1:] if '=' not in p]
        self.assertEqual(candidates,[label for _,label,_,enabled in REGIONS if enabled] + ['proxy', 'direct'])
        self.assertEqual(candidates[0],'Hong Kong')
        benchmarks=[x for x in policies if x.startswith('url-latency-benchmark = ')]
        self.assertEqual(len(benchmarks),sum(enabled for _,_,_,enabled in REGIONS))
        for line in benchmarks:
            self.assertIn('tolerance=20,',line)
        self.assertFalse(any('自动选择' in x for x in policies))

    def test_rendered_resources_remain_enabled_and_sections_are_not_duplicated(self):
        for line in self.config['filter_remote']:
            self.assertIn('enabled=true',line)
        headings=re.findall(r'^\[([^\]]+)\]$',self.rendered,re.M)
        self.assertEqual(len(headings),len(set(headings)))


class RepositoryResourceTests(unittest.TestCase):
    def test_generated_network_configuration_matches_template_contract(self):
        legacy=sections((ROOT/'tools/fixtures/network-legacy.conf').read_text())
        actual=sections((ROOT/'examples/quantumult_steeefanie.conf').read_text())
        self.assertEqual([x.replace(' ','') for x in actual['dns']],
                         [x.replace(' ','') for x in legacy['dns']])
        self.assertIn('udp_whitelist=1-442,444-65535',[x.replace(' ','') for x in actual['general']])

    def test_xiaohongshu_is_an_independent_resource(self):
        config=sections((ROOT/'examples/quantumult_steeefanie.conf').read_text())
        found=[x for x in config['filter_remote'] if re.search(r',\s*tag=小红书,',x)]
        self.assertEqual(len(found),1)
        self.assertIn('/filter/services/xiaohongshu.list,',found[0])
        self.assertIn('force-policy=direct',found[0])
        self.assertIn('enabled=true',found[0])

    def test_all_local_repository_urls_resolve_to_files(self):
        paths=[*ROOT.joinpath('examples').glob('*.txt'),*ROOT.joinpath('examples').glob('*.conf'),
               *ROOT.joinpath('rewrite').rglob('*.conf')]
        count=0
        for path in paths:
            for target in re.findall(re.escape(RAW_ROOT+'/')+r'([^\s,]+)',path.read_text()):
                with self.subTest(file=str(path.relative_to(ROOT)),target=target):
                    self.assertTrue((ROOT/target).is_file())
                count+=1
        self.assertGreater(count,100)

    def test_every_active_script_dependency_is_local_and_has_purpose_comments(self):
        dependencies=set()
        for path in (ROOT/'rewrite').rglob('*.conf'):
            for line in path.read_text().splitlines():
                if line.lstrip().startswith(('#',';','//')): continue
                match=re.search(r'\burl\s+script-\S+\s+(https?://\S+)',line)
                if not match: continue
                with self.subTest(file=str(path.relative_to(ROOT)),url=match[1]):
                    self.assertTrue(match[1].startswith(RAW_ROOT+'/scripts/'))
                    local=match[1].removeprefix(RAW_ROOT+'/')
                    self.assertTrue((ROOT/local).is_file())
                    source=(ROOT/local).read_text()
                    self.assertTrue(source.startswith('/*\n * 名称：'))
                    self.assertIn(' * 用途：',source[:2000])
                    self.assertIn(' * 处理阶段：',source[:2000])
                    dependencies.add(local)
        lock=json.loads((ROOT/'sources/rewrites.lock.json').read_text())
        self.assertEqual(len(dependencies),lock['script_count'])

    def test_generated_scripts_retain_exact_original_body(self):
        manifest=json.loads((ROOT/'sources/rewrites.json').read_text())
        script_sources={}
        for module in manifest['modules']:
            for source in module['scripts']:
                script_sources['scripts/app2smile/'+Path(source).name]=ROOT/'sources/app2smile'/source
        lock=json.loads((ROOT/'sources/rewrites.lock.json').read_text())
        for project in lock['additional_projects']:
            for output,source in project['script_outputs'].items():
                script_sources[output]=ROOT/'sources/fmz200'/source
        for output,source in script_sources.items():
            with self.subTest(script=output):
                prefix,body=(ROOT/output).read_bytes().split(b' */\n',1)
                self.assertEqual(body,source.read_bytes())
        self.assertEqual(len(script_sources),lock['script_count'])

    def test_inventory_matches_actual_rewrite_and_script_outputs(self):
        lock=json.loads((ROOT/'sources/rewrites.lock.json').read_text())
        catalog_lines=[line for line in (ROOT/'rewrite/catalog.md').read_text().splitlines()
                       if line.startswith('| [')]
        self.assertEqual(len(catalog_lines),lock['module_count'])
        self.assertEqual(len(list((ROOT/'rewrite').rglob('*.conf'))),lock['module_count'])
        rewrite_scripts = [p for p in (ROOT/'scripts').rglob('*.js') if 'scripts/tools/' not in p.as_posix()]
        self.assertEqual(len(rewrite_scripts),lock['script_count'])
        partial=sum('基础条目，有隔离行' in line for line in catalog_lines)
        self.assertEqual(partial,lock['partial_module_count'])
        self.assertEqual(len(catalog_lines)-partial,lock['complete_direct_dependency_count'])
