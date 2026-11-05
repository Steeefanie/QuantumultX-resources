"""检验用途注释保留原文并防止说明字段提前终止 JavaScript 注释。"""
import json
from pathlib import Path
import tempfile
import unittest

from script_headers import annotate_script


class ScriptHeaderTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);(self.root/'sources').mkdir()
        self.output='scripts/demo.js'
        self.info={'title':'示例','purpose':'清理匹配响应的广告字段','stage':'响应体：JSON',
                   'requirements':'由对应重写调用','notes':'不决定代理地区','annotation_date':'2026-11-04'}
        self.write()

    def write(self):
        (self.root/'sources/script-info.json').write_text(json.dumps({self.output:self.info}))

    def render(self, body):
        return annotate_script(self.root,self.output,body,'example/repo','a'*40,'demo.js','MIT')

    def test_original_body_and_directive_preserved(self):
        body='"use strict";\r\n// 原作者署名\r\n$done({});\r\n'
        result=self.render(body)
        self.assertEqual(result.split(' */\n',1)[1],body)
        self.assertIn('用途：',result)
        self.assertIn('处理阶段：响应体：JSON',result)
        self.assertIn('/blob/'+('a'*40)+'/demo.js',result)

    def test_missing_annotation_fails_clearly(self):
        with self.assertRaisesRegex(ValueError,'缺少脚本用途'):
            annotate_script(self.root,'scripts/missing.js','original','example/repo','a'*40,'demo.js','MIT')

    def test_annotation_cannot_escape_comment(self):
        for value in ('结束 */ unwanted(); /*','两行\n正文'):
            with self.subTest(value=value):
                self.info['notes']=value;self.write()
                with self.assertRaisesRegex(ValueError,'说明字段不合法'):
                    self.render('$done({});')
