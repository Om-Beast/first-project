"""Strict output contract. Uses the standard library; no installation step."""
from __future__ import annotations
from urllib.parse import urlsplit

AUTH = ['OAuth2','API key','token','Basic','HMAC','JWT','none','unknown','OAuth1','other']
ACCESS = ['free','trial','paid','approval','customer','self_hosted','unknown']
VERDICTS = ['build','conditional','outreach','investigate','local']
FIELDS = ['auth','access','api','mcp','verdict','summary']

def string(enum=None):
    value = {'type':'string'}
    if enum is not None: value['enum'] = enum
    return value

def array(items):
    return {'type':'array','items':items}

def obj(properties):
    return {'type':'object','properties':properties,'required':list(properties),'additionalProperties':False}

APP_SCHEMA = obj({
    'id':{'type':'integer'},'name':string(),'category':string(),'summary':string(),
    'auth':array(string(AUTH)),'access':string(ACCESS),'access_detail':string(),'production_gate':string(),
    'api':obj({'protocols':array(string()),'breadth':string(['broad','focused','local','unknown']),'resources':string()}),
    'mcp':obj({'status':string(['official','community','not_found','unknown']),
               'url':{'type':['string','null']},'note':string()}),
    'verdict':string(VERDICTS),'blocker':string(),'next_action':string(),
    'confidence':string(['high','medium','low']),
    'evidence':array(obj({'fields':array(string(FIELDS)),'url':string(),'title':string(),
                          'note':string(),'retrieval':string(['opened','search'])})),
    'checked_at':string()
})

def safe_url(value):
    """Only public-style HTTPS links, without embedded credentials or script URLs."""
    try:
        p=urlsplit(value)
        return p.scheme=='https' and bool(p.hostname) and not p.username and not p.password
    except (ValueError,TypeError):
        return False

def validate_schema(value, schema=APP_SCHEMA, path='record'):
    """Validate the deliberately small JSON-Schema subset used in this repository."""
    typ=schema.get('type')
    types=typ if isinstance(typ,list) else [typ]
    matches={'object':isinstance(value,dict),'array':isinstance(value,list),
             'string':isinstance(value,str),'integer':isinstance(value,int) and not isinstance(value,bool),
             'null':value is None}
    if not any(matches.get(t,False) for t in types): raise ValueError(f'{path}: expected {types}')
    if 'enum' in schema and value not in schema['enum']: raise ValueError(f'{path}: invalid enum {value!r}')
    if isinstance(value,dict):
        required=set(schema.get('required',[]));props=schema.get('properties',{})
        if required-set(value): raise ValueError(f'{path}: missing {sorted(required-set(value))}')
        if schema.get('additionalProperties') is False and set(value)-set(props):
            raise ValueError(f'{path}: unexpected keys {sorted(set(value)-set(props))}')
        for key,item in value.items():
            if key in props: validate_schema(item,props[key],path+'.'+key)
    elif isinstance(value,list):
        for i,item in enumerate(value): validate_schema(item,schema['items'],f'{path}[{i}]')

def validate_record(record):
    validate_schema(record)
    if not 1 <= record['id'] <= 100: raise ValueError('App id must be within assignment set')
    if not record['auth'] or not record['api']['protocols']: raise ValueError('Use explicit unknown, not empty methods')
    if not record['evidence']: raise ValueError('At least one primary evidence link is required')
    covered=set()
    for evidence in record['evidence']:
        if not safe_url(evidence['url']): raise ValueError('Unsafe evidence URL')
        covered.update(evidence['fields'])
    for field in ['auth','access','api','mcp','verdict']:
        known = not ((field=='auth' and record['auth']==['unknown']) or
                     (field=='access' and record['access']=='unknown') or
                     (field=='api' and record['api']['breadth']=='unknown') or
                     (field=='mcp' and record['mcp']['status']=='unknown'))
        if known and field not in covered: raise ValueError(f"{record['name']}: no evidence bound to {field}")
    if record['mcp']['url'] is not None and not safe_url(record['mcp']['url']): raise ValueError('Unsafe MCP evidence link')
    return record
