"""检查全部 JS 语法，并在无网络/文件接口的模拟上下文运行四段可核对的处理逻辑。"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT=Path(__file__).resolve().parents[1]
NODE=os.environ.get('QX_TEST_NODE') or shutil.which('node')
if not NODE:
    bundled=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
    if bundled.is_file(): NODE=str(bundled)

BRIDGE=r'''
const fs=require('node:fs');
const vm=require('node:vm');
const fixture=JSON.parse(fs.readFileSync(0,'utf8'));
const source=fs.readFileSync(process.argv[1],'utf8');
const context=vm.createContext(Object.create(null),{codeGeneration:{strings:false,wasm:false}});
// 在上下文内部创建数据与回调，不向脚本暴露主进程对象、文件或网络接口。
vm.runInContext('globalThis.$request='+JSON.stringify(fixture.request||{})+';'+
 'globalThis.$response='+JSON.stringify(fixture.response||{})+';'+
 'globalThis.__results=[];globalThis.console={log(){},warn(){},error(){}};'+
 'globalThis.$done=(value)=>__results.push(value);',context,{timeout:1000});
vm.runInContext(source,context,{timeout:1000,filename:process.argv[1]});
process.stdout.write(vm.runInContext('JSON.stringify(__results)',context,{timeout:1000}));
'''


@unittest.skipUnless(NODE,'Node.js 不可用，JavaScript 语法与模拟处理检查未运行')
class JavaScriptTests(unittest.TestCase):
    def run_script(self,path,request=None,response=None):
        result=subprocess.run([NODE,'-e',BRIDGE,str(ROOT/path)],
                              input=json.dumps({'request':request or {},'response':response or {}}),
                              capture_output=True,text=True,timeout=5,env={})
        self.assertEqual(result.returncode,0,result.stderr[-1800:])
        results=json.loads(result.stdout)
        self.assertEqual(len(results),1,'应返回一次处理结果')
        return results[0]

    def test_all_generated_javascript_parses_without_execution(self):
        paths=sorted((ROOT/'scripts').rglob('*.js'))
        self.assertTrue(paths)
        for path in paths:
            with self.subTest(script=str(path.relative_to(ROOT))):
                result=subprocess.run([NODE,'--check',str(path)],capture_output=True,text=True,timeout=5,env={})
                self.assertEqual(result.returncode,0,result.stderr[-1800:])

    def test_spotify_cache_header_removal_preserves_other_headers(self):
        result=self.run_script('scripts/app2smile/spotify-qx-header.js',
                               request={'headers':{'If-None-Match':'fixture-etag','User-Agent':'fixture-client','X-Fixture':'keep'}})
        self.assertNotIn('If-None-Match',result['headers'])
        self.assertEqual(result['headers']['User-Agent'],'fixture-client')
        self.assertEqual(result['headers']['X-Fixture'],'keep')

    def test_spotify_url_rewrite_preserves_path_and_other_query_parameters(self):
        result=self.run_script('scripts/app2smile/spotify-json.js',
                               request={'url':'https://spclient.wg.spotify.com:443/artistview/v1/artist?platform=iphone&fixture=keep'})
        self.assertEqual(result['url'],'https://spclient.wg.spotify.com/artistview/v1/artist?platform=ipad&fixture=keep')

    def test_vgtime_removes_ad_and_keeps_other_response_data(self):
        result=self.run_script('scripts/app2smile/vgtime.js',response={'body':json.dumps({'data':{'ad':{'id':'fixture-ad'},'keep':'unchanged'}})})
        body=json.loads(result['body'])
        self.assertIsNone(body['data']['ad'])
        self.assertEqual(body['data']['keep'],'unchanged')

    def test_ithome_filters_ads_but_keeps_ordinary_news(self):
        body={'data':{'list':[{'id':1,'feedType':1,'feedContent':{'smallTags':[]}},
                              {'id':2,'feedType':1,'feedContent':{'smallTags':[{'text':'广告'}]}},
                              {'id':3,'feedType':10002,'feedContent':{}},
                              {'id':4,'feedType':10003,'feedContent':{}}]}}
        result=self.run_script('scripts/fmz200/ithome/ithome.js',
                               request={'url':'https://napi.ithome.com/api/news/index'},
                               response={'body':json.dumps(body)})
        self.assertEqual([item['id'] for item in json.loads(result['body'])['data']['list']],[1])
