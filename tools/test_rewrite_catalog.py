"""检验脚本依赖隔离、来源篡改检测和重写/分流拆分，不执行第三方脚本。"""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from rewrite_catalog import create_plan


class ExtraRewriteTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root/'sources/fmz200'; self.source.mkdir(parents=True)
        known = 'https://raw.githubusercontent.com/fmz200/wool_scripts/main/Scripts/demo.js'
        unknown = 'https://unknown.example/missing.js'
        self.texts = {'LICENSE':'GNU GENERAL PUBLIC LICENSE\nVersion 3\n',
                      'Scripts/demo.js':'$done({});\n',
                      'demo.snippet':f'#!name=示例\nhost, ads.example.com, reject\n^https://api.example.com/data url script-response-body {known}\n^https://api.example.com/other url script-response-body {unknown}\nhostname = api.example.com\n'}
        self.project = {'id':'fmz200','repository':'fmz200/wool_scripts','branch':'main','commit':'a'*40,
                        'checked_on':'2026-11-04','source_directory':'sources/fmz200','license':'GPL-3.0','license_path':'LICENSE',
                        'modules':[{'id':'demo','source':'demo.snippet','title':'示例','notes':'测试数据'}]}
        self.write()

    def write(self):
        for name,text in self.texts.items():
            path=self.source/name; path.parent.mkdir(exist_ok=True,parents=True); path.write_text(text)
        self.project['files']={name:hashlib.sha256(text.encode()).hexdigest() for name,text in self.texts.items()}
        (self.root/'sources/rewrite-catalog.json').write_text(json.dumps({'schema':1,'projects':[self.project]}))

    def test_known_script_kept_and_unknown_dependency_isolated(self):
        files,rows,review,summary = create_plan(self.root,'https://resources.example/main',{})
        output=files['rewrite/fmz200/demo.conf']
        self.assertIn('https://resources.example/main/scripts/fmz200/demo.js',output)
        self.assertNotIn('unknown.example',output)
        self.assertEqual(files['scripts/fmz200/demo.js'],self.texts['Scripts/demo.js'])
        self.assertEqual(summary['modules'],1)
        self.assertEqual(len(review),1)
        self.assertIn('有脚本行隔离',rows[0]['限制'])
        self.assertNotIn('host, ads.example.com, reject',output)
        self.assertIn('host, ads.example.com, reject',files['filter/adblock/fmz200/demo.list'])

    def test_tampered_source_fails_before_returning_outputs(self):
        (self.source/'Scripts/demo.js').write_text('changed')
        with self.assertRaisesRegex(ValueError,'哈希不符'):
            create_plan(self.root,'https://resources.example/main',{})

    def test_filter_only_source_does_not_create_empty_rewrite(self):
        self.texts['demo.snippet']='host, ads.example.com, reject\n'; self.write()
        files,rows,review,summary=create_plan(self.root,'https://resources.example/main',{})
        self.assertNotIn('rewrite/fmz200/demo.conf',files)
        self.assertIn('filter/adblock/fmz200/demo.list',files)
        self.assertEqual(rows,[])
        self.assertEqual(summary['modules'],0)
        self.assertEqual(summary['filters'],1)

    def test_non_reject_companion_is_not_silently_overridden(self):
        self.texts['demo.snippet']='host, login.example.com, direct\n'; self.write()
        with self.assertRaisesRegex(ValueError,'非拦截动作'):
            create_plan(self.root,'https://resources.example/main',{})

    def test_source_path_cannot_escape_snapshot(self):
        self.project['files']['../outside.js']='0'*64
        (self.root/'sources/rewrite-catalog.json').write_text(json.dumps({'schema':1,'projects':[self.project]}))
        with self.assertRaisesRegex(ValueError,'路径不安全'):
            create_plan(self.root,'https://resources.example/main',{})

    def test_existing_mit_script_can_be_reused_without_duplicate_copy(self):
        self.texts['demo.snippet']='^https://api.example.com/data url script-response-body https://raw.githubusercontent.com/app2smile/rules/master/js/demo.js\n'
        self.write()
        files,rows,review,summary=create_plan(self.root,'https://resources.example/main',{'scripts/app2smile/demo.js':'original'})
        self.assertIn('/scripts/app2smile/demo.js',files['rewrite/fmz200/demo.conf'])
        self.assertEqual(summary['scripts'],0)
        self.assertFalse(review)

    def test_file_origins_override_default_commit_url_and_record_modifications(self):
        self.project['file_origins'] = {
            'demo.snippet': {
                'upstream': 'https://github.com/ddgksf2013/Rewrite/raw/master/AdBlock/Demo.conf',
                'status': 'modified_upstream',
                'license': 'GPL-3.0',
                'local_modification': '基于上游规则调整脚本指向本仓库。',
            }
        }
        (self.root/'sources/rewrite-catalog.json').write_text(json.dumps({'schema':1,'projects':[self.project]}))
        files,rows,review,summary=create_plan(self.root,'https://resources.example/main',{})
        self.assertIn('# 来源：https://github.com/ddgksf2013/Rewrite/raw/master/AdBlock/Demo.conf\n',files['rewrite/fmz200/demo.conf'])
        self.assertIn('# 本地修改：基于上游规则调整脚本指向本仓库。\n',files['rewrite/fmz200/demo.conf'])
