import copy, hashlib, io, json, pathlib, unittest, urllib.error
from unittest.mock import patch
from agent.schema import validate_record
from agent.research import extract, post, request_payload
from tools.build import ROOT, SAMPLE, collect, embedded, metrics

class ResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.first,cls.final,cls.audits,cls.cross,cls.adjudications=collect()
        cls.record=copy.deepcopy(cls.final[0])

    def response(self,record=None,sources=True):
        record=record or self.record
        output=[]
        if sources:output.append({'type':'web_search_call','action':{'sources':[{'url':e['url']} for e in record['evidence']]}})
        output.append({'type':'message','content':[{'type':'output_text','text':json.dumps(record)}]})
        return {'status':'completed','output':output}

    def app(self):return {k:self.record[k] for k in ['id','name','category']}|{'domains':['developer.salesforce.com']}

    def test_exact_assignment_and_evidence_contract(self):
        self.assertEqual([r['id'] for r in self.final],list(range(1,101)))
        self.assertEqual(len({r['name'].casefold() for r in self.final}),100)
        for record in self.final:validate_record(record)
        changed=copy.deepcopy(self.record);changed['evidence']=[]
        with self.assertRaises(ValueError):validate_record(changed)

    def test_fixed_sample_denominator_excludes_opportunistic_checks(self):
        m=metrics(self.final,self.audits)
        self.assertEqual(m['sample_fields'],100)
        self.assertEqual(len({a['app_id'] for a in self.audits if a['sample']}),20)
        self.assertEqual(m['supported_before']+m['changed']+m['unresolved'],100)
        self.assertEqual(m['supported_after']+m['unresolved'],100)
        extra=copy.deepcopy(self.audits[0]);extra['sample']=False
        self.assertEqual(metrics(self.final,self.audits+[extra])['sample_fields'],100)

    def test_unknown_resolutions_are_not_factual_error_counts(self):
        m=metrics(self.final,self.audits)
        self.assertEqual(m['changed'],m['known_corrections']+m['resolved_unknowns'])
        self.assertGreater(m['resolved_unknowns'],0)

    def test_portable_extraction_requires_consulted_source_trace(self):
        self.assertEqual(extract(self.response(),self.app())['id'],1)
        with self.assertRaisesRegex(ValueError,'source trace'):extract(self.response(sources=False),self.app())
        forged=self.response();forged['output'][0]['action']['sources']=[]
        forged['output'][0]['action']['sources'].append({'url':'https://example.org/unused'})
        with self.assertRaisesRegex(ValueError,'missing from live source trace'):extract(forged,self.app())

    def test_wrong_app_incomplete_and_refused_outputs_are_rejected(self):
        wrong=copy.deepcopy(self.record);wrong['name']='A different app'
        with self.assertRaisesRegex(ValueError,'identity mismatch'):extract(self.response(wrong),self.app())
        partial=self.response();partial['status']='incomplete'
        with self.assertRaisesRegex(ValueError,'incomplete'):extract(partial,self.app())
        refusal={'status':'completed','output':[{'content':[{'type':'refusal','refusal':'No'}]}]}
        with self.assertRaisesRegex(ValueError,'refused'):extract(refusal,self.app())

    def test_live_request_forces_live_research_with_domain_hints(self):
        payload=request_payload(self.app(),'test-model',self.record)
        self.assertTrue(payload['tools'][0]['external_web_access'])
        self.assertEqual(payload['tool_choice'],'required')
        self.assertIn('web_search_call.action.sources',payload['include'])
        self.assertIn('prior_claims',json.loads(payload['input']))
        self.assertTrue(payload['text']['format']['strict'])

    def test_provider_transport_retries_transient_errors_without_logging_key(self):
        transient=urllib.error.HTTPError('https://api.openai.com/v1/responses',429,'limited',{'Retry-After':'1'},None)
        response=io.BytesIO(b'{"status":"completed","output":[]}')
        with patch('urllib.request.urlopen',side_effect=[transient,response]) as opener,patch('time.sleep') as sleep:
            result=post({'model':'test'},'test-secret')
        self.assertEqual(result['status'],'completed')
        self.assertEqual(opener.call_count,2)
        self.assertEqual(sleep.call_count,1)

    def test_provider_transport_does_not_retry_permanent_auth_failure(self):
        permanent=urllib.error.HTTPError('https://api.openai.com/v1/responses',401,'rejected',{},None)
        with patch('urllib.request.urlopen',side_effect=permanent) as opener:
            with self.assertRaisesRegex(RuntimeError,'HTTP 401') as result:post({},'test-secret')
        self.assertEqual(opener.call_count,1)
        self.assertNotIn('test-secret',str(result.exception))

    def test_embedded_untrusted_text_cannot_close_script(self):
        value={'note':'</script><script>alert(1)</script> & <img>'}
        text=embedded(value)
        self.assertNotIn('<',text)
        self.assertEqual(json.loads(text),value)

    def test_frozen_first_pass_hashes(self):
        manifest=json.loads((ROOT/'data'/'first_pass_manifest.json').read_text())
        for filename,expected in manifest.items():
            self.assertEqual(hashlib.sha256((ROOT/'data'/filename).read_bytes()).hexdigest(),expected,filename)

    def test_single_page_contains_complete_machine_readable_dataset(self):
        from html.parser import HTMLParser
        class Parser(HTMLParser):
            def __init__(self):super().__init__();self.current=None;self.payload='';self.remote_scripts=[]
            def handle_starttag(self,tag,attrs):
                a=dict(attrs)
                if tag=='script' and a.get('id')=='app-data':self.current='data'
                if tag=='script' and a.get('src'):self.remote_scripts.append(a['src'])
            def handle_endtag(self,tag):
                if tag=='script':self.current=None
            def handle_data(self,data):
                if self.current:self.payload+=data
        p=Parser();p.feed((ROOT/'dist'/'index.html').read_text())
        self.assertEqual(json.loads(p.payload),self.final)
        self.assertEqual(p.remote_scripts,[])

if __name__=='__main__':unittest.main()
