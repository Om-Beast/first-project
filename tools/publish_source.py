"""Build an account-free source browser and a real read-only HTTP Git repository.

Only an explicit allowlist enters the public snapshot. Internal raw retrievals,
credentials, deployment identity and generated repository objects are excluded.
The Git server-info files implement Git's documented static HTTP transport.
"""
from __future__ import annotations
import hashlib,html,json,pathlib,shutil,subprocess,tempfile,zipfile

ROOT=pathlib.Path(__file__).resolve().parents[1]

def command(*args,cwd=None):
    return subprocess.check_output(list(args),cwd=cwd,text=True,stderr=subprocess.STDOUT).strip()

def selected_files():
    result=[]
    for item in ['agent','data','docs','tests','tools','dist','.github','README.md','.gitignore','.env.example']:
        start=ROOT/item
        paths=[start] if start.is_file() else sorted(start.rglob('*'))
        for path in paths:
            if not path.is_file():continue
            parts=path.relative_to(ROOT).parts
            if 'raw' in parts or '__pycache__' in parts:continue
            if len(parts)>1 and parts[0]=='dist' and parts[1] in ['source','repo.git']:continue
            if path.name=='source.zip':continue
            result.append(path)
    return sorted(result,key=lambda p:str(p.relative_to(ROOT)))

def build_source():
    config=json.loads((ROOT/'data/publication.json').read_text())
    dist=ROOT/'dist';files=selected_files()
    manifest=[{'path':str(p.relative_to(ROOT)),'size':p.stat().st_size,
               'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
    with tempfile.TemporaryDirectory(prefix='atlas-public-source-') as temporary:
        work=pathlib.Path(temporary)/'work';work.mkdir()
        for p in files:
            target=work/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
        command('git','init','--initial-branch=main',str(work))
        # Project automation identity, not an invented personal email or signed commit.
        command('git','-C',str(work),'config','user.name','Atlas Research Build')
        command('git','-C',str(work),'config','user.email','noreply@agent-access-atlas.invalid')
        command('git','-C',str(work),'add','--all')
        command('git','-C',str(work),'commit','-m','Publish evidence-backed 100-app research snapshot')
        commit=command('git','-C',str(work),'rev-parse','HEAD')
        bare=pathlib.Path(temporary)/'repo.git'
        command('git','clone','--bare',str(work),str(bare))
        command('git','-C',str(bare),'config','--remove-section','remote.origin') if '[remote "origin"]' in (bare/'config').read_text() else None
        command('git','-C',str(bare),'repack','-a','-d')
        command('git','-C',str(bare),'update-server-info','--force')
        command('git','-C',str(bare),'fsck','--full')
        public_repo=dist/'repo.git'
        if public_repo.exists():shutil.rmtree(public_repo)
        public_repo.mkdir()
        for name in ['HEAD','packed-refs']:
            if (bare/name).exists():shutil.copyfile(bare/name,public_repo/name)
        for name in ['objects','refs','info']:
            shutil.copytree(bare/name,public_repo/name)
        # No config, hooks, remotes, reflogs or credentials are distributed.
        tracked=command('git','-C',str(work),'ls-files').splitlines()
        if sorted(tracked)!=sorted(x['path'] for x in manifest):raise ValueError('Public Git tree differs from allowlisted source files')
    source=dist/'source'
    if source.exists():shutil.rmtree(source)
    (source/'files').mkdir(parents=True)
    for p in files:
        target=source/'files'/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
    data={'commit':commit,'branch':'main','files':manifest,'clone_url':config['clone_url'],
          'case_study':config['live_url'],'applicant':config['applicant']}
    (source/'manifest.json').write_text(json.dumps(data,indent=2)+'\n')
    (source/'index.html').write_text(source_page(data),encoding='utf8')
    with zipfile.ZipFile(dist/'source.zip','w',zipfile.ZIP_DEFLATED,compresslevel=8) as archive:
        for p in files:archive.write(p,'agent-access-atlas/'+str(p.relative_to(ROOT)))
    print(json.dumps({'commit':commit,'files':len(files),'clone_url':config['clone_url'],
                      'source_url':config['source_url'],'zip_bytes':(dist/'source.zip').stat().st_size},indent=2))
    return data

def source_page(data):
    payload=json.dumps(data,ensure_ascii=False).replace('<','\\u003c')
    options=''.join('<option value="'+html.escape(f['path'],quote=True)+'">'+html.escape(f['path'])+'</option>' for f in data['files'])
    return '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Agent Access Atlas · source repository</title><style>
*{box-sizing:border-box}body{margin:0;font:16px/1.6 Arial,sans-serif;color:#14202b;background:#f4f7f9}header{background:white;border-bottom:1px solid #dce2e7;padding:25px 4%}header h1{font-size:28px;margin:8px 0 5px;letter-spacing:-.03em}a{color:#245fa3;text-underline-offset:3px}.muted{font-size:13px;color:#536170}.actions{display:flex;gap:20px;flex-wrap:wrap;font-size:14px}.wrap{width:92%;max-width:1420px;margin:auto}.clone{padding:20px 0 25px}.clone code{display:block;background:#14202b;color:#d0f980;padding:16px;border-radius:6px;overflow:auto;font-size:13px}.workspace{display:grid;grid-template-columns:285px minmax(0,1fr);border:1px solid #dce2e7;border-radius:7px;background:white;min-height:670px;margin-bottom:30px;overflow:hidden}.tree{border-right:1px solid #dce2e7;padding:18px 0;max-height:82vh;overflow:auto}.tree h2{font-size:13px;padding:0 16px}.tree button{display:block;width:100%;border:0;text-align:left;background:white;padding:6px 16px;font:12px/1.5 ui-monospace,monospace;color:#536170;overflow-wrap:anywhere;cursor:pointer}.tree button.active{background:#e8f1e9;color:#235b39}.tree button:hover{background:#f4f7f9}.viewer{min-width:0}.filehead{padding:17px 20px;border-bottom:1px solid #dce2e7;display:flex;justify-content:space-between;gap:15px;font-size:13px;overflow-wrap:anywhere}.filehead strong{font-family:ui-monospace,monospace}pre{padding:24px;margin:0;max-height:78vh;overflow:auto;font:13px/1.65 ui-monospace,SFMono-Regular,Consolas,monospace;tab-size:4;white-space:pre-wrap;overflow-wrap:anywhere}.mobile-select{display:none}button:focus-visible,a:focus-visible,select:focus-visible{outline:3px solid #326acb;outline-offset:3px}.status{font-size:13px;color:#536170;margin-top:12px}.sha{font-family:ui-monospace,monospace;font-size:12px;overflow-wrap:anywhere}@media(max-width:760px){.workspace{grid-template-columns:1fr;min-height:0}.tree{display:none}.mobile-select{display:block;padding:14px 20px;border-bottom:1px solid #dce2e7}.mobile-select label{display:block;font-size:12px;margin-bottom:6px}.mobile-select select{width:100%;font-size:14px;padding:10px;background:white;border:1px solid #cbd4dd;border-radius:4px}.filehead{display:block}.filehead a{display:block;margin-top:8px}pre{font-size:12px;padding:16px}header h1{font-size:25px}}
</style></head><body><header><div class="wrap"><div class="muted">COMPOSIO · AI PRODUCT OPS TAKE-HOME</div><h1>Agent Access Atlas / source</h1><p class="muted">Public read-only repository · complete source, evidence and verification artifacts</p><div class="actions"><a href="../">Open the case study</a><a href="../source.zip" download>Download complete ZIP</a><a href="manifest.json">File hashes and commit</a></div></div></header><main class="wrap"><section class="clone"><strong>Clone and run</strong><code id="clone-command"></code><p class="status">After cloning: <code>python3 -m agent.research --replay</code> then <code>python3 -m unittest discover -s tests -v</code>. Offline reproduction needs Python 3.10+, no API key.</p><div class="sha" id="commit"></div></section><section class="workspace"><aside class="tree"><h2>Repository files</h2><div id="file-tree"></div></aside><div class="viewer"><div class="mobile-select"><label for="file-select">Choose a file</label><select id="file-select">'''+options+'''</select></div><div class="filehead"><strong id="file-title">README.md</strong><a id="raw-link">Open raw file</a></div><pre id="file-content" tabindex="0">Loading README…</pre></div></section></main><script type="application/json" id="source-data">'''+payload+'''</script><script>
'use strict';const data=JSON.parse(document.getElementById('source-data').textContent),files=new Map(data.files.map(f=>[f.path,f]));const tree=document.getElementById('file-tree'),select=document.getElementById('file-select');document.getElementById('clone-command').textContent='git clone '+data.clone_url+' agent-access-atlas';document.getElementById('commit').textContent='main · '+data.commit+' · '+data.files.length+' files';let lastRequest=0;async function openFile(path){if(!files.has(path))return;const current=++lastRequest;document.getElementById('file-title').textContent=path;select.value=path;for(const b of tree.querySelectorAll('button'))b.classList.toggle('active',b.dataset.path===path);const target='files/'+path.split('/').map(encodeURIComponent).join('/');document.getElementById('raw-link').href=target;document.getElementById('file-content').textContent='Loading…';try{const response=await fetch(target);if(!response.ok)throw new Error('HTTP '+response.status);const text=await response.text();if(current!==lastRequest)return;document.getElementById('file-content').textContent=text;history.replaceState(null,'','?file='+encodeURIComponent(path))}catch(error){if(current===lastRequest)document.getElementById('file-content').textContent='This file could not be loaded. Use the complete ZIP download to inspect the repository.'}}for(const f of data.files){const button=document.createElement('button');button.textContent=f.path;button.dataset.path=f.path;button.addEventListener('click',()=>openFile(f.path));tree.append(button)}select.addEventListener('change',()=>openFile(select.value));const initial=new URLSearchParams(location.search).get('file');openFile(files.has(initial)?initial:'README.md');
</script></body></html>'''

if __name__=='__main__':build_source()
