"""Validate canonical research, compute every displayed number, emit one HTML file."""
from __future__ import annotations
import collections, csv, hashlib, html, io, json, pathlib, re
from urllib.parse import urlsplit
from agent.schema import validate_record

ROOT=pathlib.Path(__file__).resolve().parents[1]
SAMPLE=[2,5,15,18,25,28,31,35,46,49,53,59,65,68,72,79,82,87,91,93]
FIELD_NAMES=['auth','access','api','mcp','verdict']
ACCESS_LABELS={'free':'Free / self-serve','trial':'Trial / sandbox','paid':'Paid plan','approval':'Approval required','customer':'Existing customer','self_hosted':'Self-hosted / local','unknown':'Unresolved'}
VERDICT_LABELS={'build':'Build first','conditional':'With conditions','outreach':'Needs outreach','investigate':'Investigate','local':'Local wrapper'}
MCP_LABELS={'official':'Vendor documented','community':'Community / Labs','not_found':'Not found in search','unknown':'Unresolved'}

def load(path):return json.loads(path.read_text(encoding='utf8'))
def dump(path,value):path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
def esc(value):return html.escape(str(value),quote=True)
def embedded(value):return json.dumps(value,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')

def is_unknown(value,field):
    if field=='mcp':return value.get('status')=='unknown'
    if field=='auth':return value==['unknown']
    if field=='api':return value.get('breadth')=='unknown'
    if field=='access' and isinstance(value,dict):return value.get('value')=='unknown'
    return value=='unknown'

def collect():
    data=ROOT/'data';first=[];final=[];audits=[]
    for f in sorted(data.glob('batch*.first.json')):first+=load(f)
    for f in sorted(data.glob('batch*.final.json')):final+=load(f)
    for f in sorted(data.glob('audit[0-9][0-9].json')):audits+=load(f)
    for stage,rows in [('first',first),('final',final)]:
        if sorted(r['id'] for r in rows)!=list(range(1,101)):raise ValueError(f'{stage}: assignment ids must appear exactly once')
        for row in rows:validate_record(row)
        counts=collections.Counter(r['category'] for r in rows)
        if len(counts)!=10 or set(counts.values())!={10}:raise ValueError('Expected ten categories of ten')
    expected={(i,f) for i in SAMPLE for f in FIELD_NAMES}
    sampled=[a for a in audits if a.get('sample',True)]
    if collections.Counter((a['app_id'],a['field']) for a in sampled)!=collections.Counter(expected):
        raise ValueError('Fixed audit sample must contain exactly five fields per selected app')
    for a in audits:a.setdefault('sample',True)
    # Independent follow-ups can supersede an earlier audit interpretation, with a full log.
    adjudications=load(data/'adjudications.json') if (data/'adjudications.json').exists() else []
    consolidated=json.loads(json.dumps(audits))
    for amendment in adjudications:
        for a in consolidated:
            if (a['app_id'],a['field'])==(amendment['app_id'],amendment['field']):
                a.update({k:amendment[k] for k in ['after','status','url','explanation']})
                a['followup_adjudicated']=True
    cross=[]
    for f in sorted(data.glob('cross_review*.json')):cross+=load(f)
    return sorted(first,key=lambda x:x['id']),sorted(final,key=lambda x:x['id']),consolidated,cross,adjudications

def metrics(rows,audits):
    sample=[a for a in audits if a['sample']]
    corrections=[a for a in sample if a['status']=='corrected']
    resolutions=[a for a in corrections if is_unknown(a['before'],a['field'])]
    return {'apps':len(rows),'categories':len({r['category'] for r in rows}),
            'access':dict(collections.Counter(r['access'] for r in rows)),
            'verdict':dict(collections.Counter(r['verdict'] for r in rows)),
            'mcp':dict(collections.Counter(r['mcp']['status'] for r in rows)),
            'auth':dict(collections.Counter(x for r in rows for x in sorted(set(r['auth'])))),
            'self_serve':sum(r['access'] in ['free','trial'] for r in rows),
            'sample_apps':len(SAMPLE),'sample_fields':len(sample),
            'supported_before':sum(a['status']=='supported' for a in sample),
            'supported_after':sum(a['status']!='unresolved' for a in sample),
            'changed':len(corrections),'resolved_unknowns':len(resolutions),
            'known_corrections':len(corrections)-len(resolutions),
            'unresolved':sum(a['status']=='unresolved' for a in sample),
            'extra_checks':sum(not a['sample'] for a in audits),
            'evidence_links':len({e['url'] for r in rows for e in r['evidence']}),
            'low_confidence':sum(r['confidence']=='low' for r in rows)}

def provenance(rows):
    sources={}
    for row in rows:
        for e in row['evidence']:
            entry=sources.setdefault(e['url'],{'url':e['url'],'title':e['title'],'app_ids':[],'fields':[]})
            entry['app_ids']=sorted(set(entry['app_ids']+[row['id']]))
            entry['fields']=sorted(set(entry['fields']+e['fields']))
    retrievals=[]
    for f in sorted((ROOT/'data'/'raw').glob('*.json')):
        raw=f.read_bytes()
        retrievals.append({'file':f.name,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)})
    if not retrievals and (ROOT/'data'/'evidence_index.json').exists():
        # Public clones deliberately omit raw vendor-document extracts. Preserve
        # their existing receipts rather than erasing provenance during replay.
        retrievals=load(ROOT/'data'/'evidence_index.json').get('internal_retrieval_digests',[])
    return {'checked_at':'2026-11-24','sources':list(sources.values()),'internal_retrieval_digests':retrievals,
            'note':'Full vendor-document extracts are not redistributed. Notes and field-bound primary links remain in the dataset.'}

def row_html(r):
    primary=r['evidence'][0]
    auth=' / '.join(r['auth'])
    return f'''<tr data-id="{r['id']}"><td class="app-cell"><button class="app-open" data-open="{r['id']}">{esc(r['name'])}<span class="app-id">{r['id']:03d}</span></button><p>{esc(r['summary'])}</p></td><td><span class="cell-label">{esc(r['category'])}</span><span class="subline">{esc(auth)}</span></td><td><span class="access {esc(r['access'])}">{esc(ACCESS_LABELS[r['access']])}</span><span class="subline">{esc(' + '.join(r['api']['protocols']))} · {esc(r['api']['breadth'])}</span></td><td><span class="mcp-status">{esc(MCP_LABELS[r['mcp']['status']])}</span><span class="subline">{esc(r['confidence'])} confidence</span></td><td><span class="verdict {esc(r['verdict'])}">{esc(VERDICT_LABELS[r['verdict']])}</span></td><td><button class="evidence-open" data-open="{r['id']}">{len(r['evidence'])} sources</button><a class="source-link" href="{esc(primary['url'])}" target="_blank" rel="noopener noreferrer">Primary doc</a></td></tr>'''

def category_bars(rows):
    groups=collections.defaultdict(list)
    for row in rows:groups[row['category']].append(row)
    out=[]
    for name,items in groups.items():
        counts=collections.Counter(r['access'] for r in items)
        parts=''.join(f'<span class="segment {key}" style="width:{counts[key]*10}%" title="{esc(ACCESS_LABELS[key])}: {counts[key]}"></span>' for key in ACCESS_LABELS if counts[key])
        quick=sum(r['access'] in ['free','trial'] for r in items)
        out.append(f'<button class="category-bar" data-category="{esc(name)}"><span>{esc(name)}</span><span class="bar-track">{parts}</span><strong>{quick}/10</strong></button>')
    return ''.join(out)

def build():
    first,rows,audits,cross,adjudications=collect();m=metrics(rows,audits)
    data=ROOT/'data';dist=ROOT/'dist';dist.mkdir(exist_ok=True)
    clustering=load(data/'blocker_clusters.json')
    assignments=clustering['items']
    if len(assignments)!=len({a['app_id'] for a in assignments}) or {a['app_id'] for a in assignments}!={r['id'] for r in rows if r['verdict']!='build'}:
        raise ValueError('Primary-friction clusters must cover each non-build-first app exactly once')
    m['primary_blockers']=dict(collections.Counter(a['cluster'] for a in assignments))
    common_blocker,common_count=max(m['primary_blockers'].items(),key=lambda x:x[1])
    dump(data/'results.json',rows);dump(data/'first_pass.json',first);dump(data/'verification.json',audits)
    dump(data/'metrics.json',m);dump(data/'evidence_index.json',provenance(rows))
    if not (data/'apps.json').exists():
        apps=[]
        for r in rows:
            domains=sorted({urlsplit(e['url']).hostname for e in r['evidence']})
            apps.append({k:r[k] for k in ['id','name','category']}|{'domains':domains})
        dump(data/'apps.json',apps)
    human=load(data/'human_review.json') if (data/'human_review.json').exists() else {'status':'not_performed','checks':[]}
    publication=load(data/'publication.json')
    meta={'as_of':'24 November 2026','sample_ids':SAMPLE,'metrics':m,'cross_checks':len(cross),
          'human_review':human,'labels':{'access':ACCESS_LABELS,'verdict':VERDICT_LABELS,'mcp':MCP_LABELS},
          'execution':'Hosted Codex agents performed live discovery and document audits. Portable CLI live-provider mode is implemented with offline transport tests; no direct provider run or authenticated app API test is claimed.'}
    template=(ROOT/'tools'/'page.html').read_text()
    replacements={'__ROWS__':''.join(row_html(r) for r in rows),'__CATEGORY_BARS__':category_bars(rows),
                  '__DATA__':embedded(rows),'__AUDIT__':embedded(audits),'__CROSS__':embedded(cross),'__META__':embedded(meta),
                  '__BUILD_COUNT__':str(m['verdict'].get('build',0)),
                  '__OUTREACH_COUNT__':str(m['verdict'].get('outreach',0)),
                  '__SELF_SERVE__':str(m['self_serve']),'__SOURCE_COUNT__':str(m['evidence_links']),
                  '__BEFORE__':str(m['supported_before']),'__AFTER__':str(m['supported_after']),
                  '__CHANGED__':str(m['changed']),'__KNOWN_FIXES__':str(m['known_corrections']),
                  '__RESOLVED__':str(m['resolved_unknowns']),'__UNRESOLVED__':str(m['unresolved']),
                  '__OAUTH__':str(m['auth'].get('OAuth2',0)),
                  '__BLOCKER_COUNT__':str(common_count),'__BLOCKER_NAME__':esc(common_blocker),
                  '__NON_BUILD__':str(len(assignments)),
                  '__REPO_URL__':esc(publication['source_url']),'__APPLICANT__':esc(publication['applicant'])}
    for old,new in replacements.items():template=template.replace(old,new)
    if re.search(r'__[A-Z_]+__',template):raise ValueError('Unexpanded page token')
    (dist/'index.html').write_text(template,encoding='utf8')
    for name in ['results.json','first_pass.json','verification.json','metrics.json','evidence_index.json','additional_doc_checks.json']:
        (dist/name).write_bytes((data/name).read_bytes())
    (dist/'apps.json').write_bytes((data/'apps.json').read_bytes())
    with (dist/'results.csv').open('w',newline='',encoding='utf8') as f:
        w=csv.writer(f);w.writerow(['id','app','category','summary','auth','access','access_detail','production_gate','api_protocols','api_scope','mcp_status','mcp_note','verdict','blocker','next_action','confidence','evidence_urls','checked_at'])
        for r in rows:w.writerow([r['id'],r['name'],r['category'],r['summary'],'; '.join(r['auth']),r['access'],r['access_detail'],r['production_gate'],'; '.join(r['api']['protocols']),r['api']['resources'],r['mcp']['status'],r['mcp']['note'],r['verdict'],r['blocker'],r['next_action'],r['confidence'],'; '.join(e['url'] for e in r['evidence']),r['checked_at']])
    print(json.dumps({'apps':len(rows),'output':'dist/index.html','metrics':m},indent=2))
    return rows,m

if __name__=='__main__':build()
