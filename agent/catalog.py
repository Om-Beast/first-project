"""Optional Composio SDK catalog snapshot; separate from MCP presence.

Not run for the shipped case study. Requires the composio package and an API key.
Use exact catalog slugs for joins; do not infer an absent toolkit from a guessed slug.
"""
import datetime,json,os,pathlib

def main():
    if not os.getenv('COMPOSIO_API_KEY'):raise SystemExit('Set COMPOSIO_API_KEY to query your authenticated catalog')
    try:from composio import Composio
    except ImportError:raise SystemExit('Install optional dependency: python3 -m pip install composio') from None
    client=Composio(api_key=os.environ['COMPOSIO_API_KEY'])
    cursor=None;seen=set();rows=[]
    while True:
        result=client.toolkits.list(limit=1000,**({'cursor':cursor} if cursor else {}))
        result=result.model_dump(mode='json') if hasattr(result,'model_dump') else result
        if not isinstance(result,dict) or not isinstance(result.get('items'),list):
            raise SystemExit('Unexpected SDK response; inspect current official SDK docs before changing this adapter')
        rows+=result['items'];cursor=result.get('next_cursor')
        if not cursor:break
        if cursor in seen:raise SystemExit('Repeated pagination cursor; refusing an infinite loop')
        seen.add(cursor)
    target=pathlib.Path('runs/catalog.json');target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps({'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'items':rows,
        'note':'Authenticated project catalog; this is not an MCP-server registry.'},indent=2)+'\n')
    print(f'Saved {len(rows)} catalog entries to {target}')

if __name__=='__main__':main()
