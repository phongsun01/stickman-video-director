#!/usr/bin/env python3
"""Snapshot-based prompt compilation; technical checks never certify generated images."""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import math
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
DEFAULT_KITS_DIR = SKILL_DIR / 'assets/kits'
CORE_SCHEMA_PATH = DEFAULT_KITS_DIR / 'core-schema.json'
STATUSES = {'approved', 'draft', 'conflict', 'deprecated'}
OPS = {'pickup', 'putdown', 'handover', 'consume'}
CHAR_FIELDS = ('pose', 'seat', 'holding', 'hands')
PROP_FIELDS = ('placed_at', 'held_by', 'fill_fraction')
class KitError(Exception): pass
class ValidationError(KitError): pass
class QuotaExceededError(KitError): pass
class ContinuityError(KitError): pass

def read_json(path):
    try:
        with open(path, encoding='utf-8') as f: return json.load(f)
    except (OSError, ValueError) as exc: raise ValidationError(f'Cannot read JSON {path}: {exc}') from exc

def canonical_hash(data):
    return hashlib.sha256(json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''): h.update(chunk)
    return h.hexdigest()

def safe_path(root, relative):
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute(): raise ValidationError(f'Expected relative path: {relative!r}')
    root = Path(root).resolve(); result = (root / relative).resolve()
    if not result.is_relative_to(root): raise ValidationError(f'Path escapes root: {relative}')
    return result

def find_pack_dir(name, kits_dir=None):
    p = Path(name)
    if p.is_file() and p.name == 'kit.json': return p.parent.resolve()
    if p.is_dir() and (p/'kit.json').is_file(): return p.resolve()
    p = Path(kits_dir or DEFAULT_KITS_DIR)/name
    if (p/'kit.json').is_file(): return p.resolve()
    raise ValidationError(f'Cannot find pack {name!r}')

def validate_document(value, schema, path='$'):
    """Evaluate the bounded JSON Schema vocabulary used by our two shipped schemas.

    Cross references, hashes, approval and timeline causality are semantic checks.
    """
    errors = []
    types = {'object': lambda x: isinstance(x, dict), 'array': lambda x: isinstance(x, list),
             'string': lambda x: isinstance(x, str), 'null': lambda x: x is None,
             'integer': lambda x: type(x) is int,
             'number': lambda x: type(x) in (int, float) and math.isfinite(x)}
    expected = schema.get('type')
    if expected and not any(types[t](value) for t in ([expected] if isinstance(expected, str) else expected)):
        return [f'{path}: invalid type, expected {expected}']
    if 'enum' in schema and value not in schema['enum']: errors.append(f'{path}: invalid enum')
    if 'const' in schema and value != schema['const']: errors.append(f'{path}: invalid const')
    if isinstance(value, dict):
        for key in schema.get('required', []):
            if key not in value: errors.append(f'{path}: missing {key}')
        properties = schema.get('properties', {})
        for key, item in value.items():
            if key in properties: errors.extend(validate_document(item, properties[key], f'{path}.{key}'))
            elif isinstance(schema.get('additionalProperties'), dict):
                errors.extend(validate_document(item, schema['additionalProperties'], f'{path}.{key}'))
    if isinstance(value, list):
        if len(value) < schema.get('minItems', 0): errors.append(f'{path}: too few items')
        for index, item in enumerate(value):
            if 'items' in schema: errors.extend(validate_document(item, schema['items'], f'{path}[{index}]'))
    if isinstance(value, str):
        if len(value) < schema.get('minLength', 0): errors.append(f'{path}: empty string')
        if 'pattern' in schema and not re.search(schema['pattern'], value): errors.append(f'{path}: invalid pattern')
    if type(value) in (int, float):
        for key, check in [('minimum', lambda x,y: x >= y), ('maximum', lambda x,y: x <= y), ('exclusiveMinimum', lambda x,y: x > y)]:
            if key in schema and not check(value, schema[key]): errors.append(f'{path}: violates {key}')
    for rule in schema.get('allOf', []): errors.extend(validate_document(value, rule, path))
    if 'if' in schema and not validate_document(value, schema['if'], path):
        errors.extend(validate_document(value, schema.get('then', {}), path))
    return errors

def validate_pack_schema(data):
    errors=validate_document(data, read_json(CORE_SCHEMA_PATH))
    if not isinstance(data,dict): return ['Pack must be an object']
    for key,typ in {'pack':str,'title':str,'version':str,'style':str,'global_rules':dict,'entities':list,'meta':dict}.items():
        if not isinstance(data.get(key),typ): errors.append(f'Missing/invalid top-level {key}')
    rules=data.get('global_rules',{})
    if isinstance(rules,dict):
        for key,typ in {'figure_construction':str,'drawing_rule':str,'forbid':list}.items():
            if not isinstance(rules.get(key),typ): errors.append(f'Invalid global rule {key}')
    if not isinstance(data.get('entities'),list): return errors
    seen=set()
    for e in data['entities']:
        if not isinstance(e,dict): errors.append('Entity must be an object');continue
        eid=e.get('id')
        if not isinstance(eid,str): errors.append('Entity id must be string');continue
        if eid in seen: errors.append(f'Duplicate entity id {eid}')
        seen.add(eid)
        for k in ('name','revision'):
            if not isinstance(e.get(k),str): errors.append(f'{eid}: missing {k}')
        if e.get('status') not in STATUSES: errors.append(f'{eid}: invalid status')
        required={'CHAR':{'identity':dict,'approved_variants':list,'forbid':list},'LOC':{'spatial_layout':dict,'approved_angles':dict,'lighting_variants':dict,'forbid':list},'PROP':{'shape':str,'scale_relative':str,'visible_faces':dict,'forbid':list},'ENS':{'members':list,'member_revisions':dict,'member_variants':dict,'reference_role':str}}
        kind=e.get('type')
        if kind not in required: errors.append(f'{eid}: invalid type');continue
        for key,typ in required[kind].items():
            if not isinstance(e.get(key),typ): errors.append(f'{eid}: invalid/missing {key}')
        if kind=='CHAR' and isinstance(e.get('identity'),dict):
            for key in ('head','torso','limbs','proportions','marks'):
                if key not in e['identity']: errors.append(f'{eid}: missing identity.{key}')
        if kind=='CHAR' and e.get('status')=='approved' and not e.get('ref'):
            errors.append(f'{eid}: approved character requires an image')
        variants=e.get('approved_variants',[])
        if not isinstance(variants,list):variants=[]
        vids=set()
        for obj in variants:
            if not isinstance(obj,dict):errors.append(f'{eid}: invalid variant');continue
            vid=obj.get('variant_id')
            if not isinstance(vid,str) or vid in vids:errors.append(f'{eid}: missing/duplicate variant id')
            else:vids.add(vid)
            if obj.get('status')=='approved' and not obj.get('ref'):
                errors.append(f'{eid}/{vid}: approved variant requires an image')
            if obj.get('status') not in STATUSES or not isinstance(obj.get('outfit'),str):errors.append(f'{eid}: invalid variant status/outfit')
        for obj in [e]+[v for v in variants if isinstance(v,dict)]:
            ref,digest=obj.get('ref'),obj.get('ref_hash')
            if bool(ref)!=bool(digest): errors.append(f'{eid}: ref and ref_hash must be paired')
            if digest and (not isinstance(digest,str) or len(digest)!=64 or any(c not in '0123456789abcdef' for c in digest)):errors.append(f'{eid}: invalid SHA-256')
    return errors

def validate_ref(obj,root,required=False):
    ref=obj.get('ref')
    if not ref:
        if required:raise ValidationError(f'Missing required reference {obj.get("id",obj.get("variant_id"))}')
        return None
    p=safe_path(root,ref)
    if not p.is_file():raise ValidationError(f'Missing reference file: {p}')
    if not obj.get('ref_hash') or sha256_file(p)!=obj['ref_hash']:raise ValidationError(f'SHA-256 mismatch: {ref}')
    return p

def audit_pack(data,pack_dir):
    errors=validate_pack_schema(data);missing=[];mismatches=[];conflicts=[];valid=set();total=set()
    if errors:
        return {'pack':data.get('pack'),'version':data.get('version'),'schema_errors':errors,'missing_files':[],'hash_mismatches':[],'conflicts':[],'pending_clarification':[],'valid_refs':0,'total_declared_refs':0,'total_entities':len(data.get('entities',[])) if isinstance(data.get('entities'),list) else 0}
    table={e['id']:e for e in data.get('entities',[]) if isinstance(e,dict) and isinstance(e.get('id'),str)}
    for eid,e in table.items():
        if e.get('status')=='conflict':conflicts.append({'id':eid,'note':e.get('conflict_note','')})
        for obj in [e]+e.get('approved_variants',[]):
            if not obj.get('ref'):continue
            total.add(obj['ref'])
            try:validate_ref(obj,pack_dir);valid.add(obj['ref'])
            except ValidationError as exc:(missing if 'Missing' in str(exc) else mismatches).append({'id':eid,'error':str(exc)})
        if e.get('type')=='ENS' and e.get('status')=='approved':
            if not e.get('ref'):errors.append(f'{eid}: approved ENS requires an image')
            for member in e.get('members',[]):
                ent=table.get(member,{})
                var=next((v for v in ent.get('approved_variants',[]) if v['variant_id']==e.get('member_variants',{}).get(member)),{})
                if ent.get('status')!='approved' or var.get('status')!='approved' or ent.get('revision')!=e.get('member_revisions',{}).get(member):errors.append(f'{eid}: unapproved/stale member {member}')
    return {'pack':data.get('pack'),'version':data.get('version'),'schema_errors':errors,'missing_files':missing,'hash_mismatches':mismatches,'conflicts':conflicts,'pending_clarification':[],'valid_refs':len(valid),'total_declared_refs':len(total),'total_entities':len(table)}

def load_pack(pack_name_or_path='vietnamese-daily',kits_dir=None):
    root=find_pack_dir(pack_name_or_path,kits_dir);data=read_json(root/'kit.json');report=audit_pack(data,root)
    if any(report[k] for k in ('schema_errors','missing_files','hash_mismatches')):raise ValidationError(json.dumps(report,ensure_ascii=False))
    return data,root

def load_project(path):
    path=Path(path).resolve();project=read_json(path);project['_project_dir']=str(path.parent);return project

def dependencies(project):
    result=set()
    for s in project.get('timeline',[]):
        result.update(c['id'] for c in s.get('characters',[]));result.update(p['type_id'] for p in s.get('prop_instances',[]))
        if s.get('location',{}).get('id'):result.add(s['location']['id'])
        result.update(s.get('required_refs',[]));result.update(s.get('optional_refs',[]))
    return result

def create_lock(project_path,pack_name='vietnamese-daily',kits_dir=None):
    project_path=Path(project_path).resolve();project=read_json(project_path);pack,root=load_pack(pack_name,kits_dir)
    digest=canonical_hash(pack);snapshot=project_path.parent/'snapshots'/digest;snapshot.mkdir(parents=True,exist_ok=True);f=snapshot/'kit.json'
    if f.exists() and canonical_hash(read_json(f))!=digest:raise ValidationError('Existing snapshot changed; refusing to overwrite')
    for e in pack['entities']:
        for obj in [e]+e.get('approved_variants',[]):
            if not obj.get('ref'):continue
            source=validate_ref(obj,root);dest=safe_path(snapshot,obj['ref']);dest.parent.mkdir(parents=True,exist_ok=True)
            if dest.exists():validate_ref(obj,snapshot)
            else:shutil.copyfile(source,dest)
    if not f.exists():f.write_text(json.dumps(pack,ensure_ascii=False,indent=2)+'\n')
    table={e['id']:e for e in pack['entities']};used=dependencies(project)
    if not used<=table.keys():raise ValidationError(f'Unknown dependencies {used-table.keys()}')
    used.update(e['id'] for e in pack['entities'] if e['type']=='ENS')
    lock={'project_id':project['project_id'],'locked_at':datetime.now(timezone.utc).isoformat(),'kit_pack':pack['pack'],'kit_pack_version':pack['version'],'kit_snapshot':str(f.relative_to(project_path.parent)),'kit_snapshot_sha256':digest,'locked_entities':{eid:{'revision':table[eid]['revision'],'ref_hash':table[eid].get('ref_hash')} for eid in sorted(used)}}
    name=project.get('lockfile',project_path.stem+'.lock.json');lockpath=safe_path(project_path.parent,name);lockpath.parent.mkdir(parents=True,exist_ok=True);lockpath.write_text(json.dumps(lock,ensure_ascii=False,indent=2)+'\n')
    project.pop('pack_lock',None);project['lockfile']=name;project_path.write_text(json.dumps(project,ensure_ascii=False,indent=2)+'\n');return lockpath

def locked_pack(project):
    if not project.get('_project_dir') or not project.get('lockfile'):raise ValidationError('Project lockfile required; use load_project() and kit lock explicitly')
    root=Path(project['_project_dir']);lock=read_json(safe_path(root,project['lockfile']))
    if lock.get('project_id')!=project.get('project_id'):raise ValidationError('Lockfile project_id mismatch')
    snapshot=safe_path(root,lock.get('kit_snapshot'));data=read_json(snapshot)
    if canonical_hash(data)!=lock.get('kit_snapshot_sha256'):raise ValidationError('Snapshot SHA-256 mismatch')
    data,pack_dir=load_pack(str(snapshot))
    if lock.get('kit_pack')!=data['pack'] or lock.get('kit_pack_version')!=data['version'] or project.get('pack_ref')!=f"{data['pack']}@{data['version']}":raise ValidationError('Locked pack/version mismatch')
    table={e['id']:e for e in data['entities']}
    for eid in dependencies(project):
        e=table.get(eid);item=lock.get('locked_entities',{}).get(eid)
        if not e or not item or item.get('revision')!=e['revision'] or item.get('ref_hash')!=e.get('ref_hash'):raise ValidationError(f'Incomplete/stale lock dependency {eid}')
    return data,pack_dir,lock

def capability(pack,target,production=False):
    if not isinstance(target,dict) or not all(target.get(k) for k in ('provider','model','mode')):raise ValidationError('Explicit target provider/model/mode required')
    try:profile=pack['meta']['provider_limits'][target['provider']][target['model']][target['mode']]
    except (KeyError,TypeError):raise ValidationError(f'Unknown capability profile {target}')
    if not isinstance(profile,dict) or type(profile.get('max_refs')) is not int or profile['max_refs']<0:raise ValidationError('Invalid capability profile')
    if production and profile.get('verified') is not True:raise ValidationError('Production requires verified model capabilities; example target is draft only')
    return profile

def selected_variant(e,char):
    var=next((v for v in e.get('approved_variants',[]) if v['variant_id']==char.get('variant')),None)
    if var is None:raise ValidationError(f'Unknown variant {char.get("variant")} for {e["id"]}')
    return var

def gate_shot(pack,shot,production=False):
    table={e['id']:e for e in pack['entities']};warnings=[]
    def check(obj,label):
        if obj.get('status')!='approved':
            msg=f'{label}: status {obj.get("status")}'
            if production:raise ValidationError('Production compilation rejected: '+msg)
            warnings.append(msg)
    for char in shot.get('characters',[]):
        ent=table.get(char['id'])
        if not ent or ent['type']!='CHAR':raise ValidationError(f'Unknown character {char["id"]}')
        check(ent,ent['id']);check(selected_variant(ent,char),char['variant'])
    for prop in shot.get('prop_instances',[]):
        ent=table.get(prop['type_id'])
        if not ent or ent['type']!='PROP':raise ValidationError(f'Unknown prop {prop["type_id"]}')
        check(ent,ent['id'])
    ent=table.get(shot.get('location',{}).get('id'))
    if not ent or ent['type']!='LOC':raise ValidationError('Unknown location')
    check(ent,ent['id'])
    for field,key in [('approved_angles','angle'),('lighting_variants','lighting')]:
        obj=ent.get(field,{}).get(shot['location'].get(key))
        if not isinstance(obj,dict):raise ValidationError(f'Unknown/invalid {key}')
        check(obj,shot['location'][key])
    return warnings

def resolve_refs(pack_data,pack_dir,shot,provider=None,mode=None,*,target=None,production=False,lock=None):
    profile=capability(pack_data,target or shot.get('target'),production);quota=profile['max_refs'];table={e['id']:e for e in pack_data['entities']}
    chars={c['id']:c for c in shot.get('characters',[])};allowed=set(chars)|{p['type_id'] for p in shot.get('prop_instances',[])}|{shot.get('location',{}).get('id')}
    required=list(dict.fromkeys(shot.get('required_refs',[])));optional=[eid for eid in dict.fromkeys(shot.get('optional_refs',[])) if eid not in required]
    def make(eid,required=True):
        ent=table.get(eid)
        if not ent or (eid not in allowed and ent['type']!='ENS'):raise ValidationError(f'Unknown/out-of-shot reference {eid}')
        obj=selected_variant(ent,chars[eid]) if ent['type']=='CHAR' else ent
        path=validate_ref(obj,pack_dir,required)
        if path is None:return None
        role=ent.get('reference_role') or ('identity' if ent['type']=='CHAR' else 'composition')
        if role not in profile.get('supported_roles',[]):raise ValidationError(f'Unsupported reference role {role}')
        if production and (ent['status']!='approved' or obj['status']!='approved'):raise ValidationError(f'Unapproved reference {eid}')
        return {'entity_id':eid,'covers':[eid],'path':str(path),'relative_path':obj['ref'],'ref_hash':obj['ref_hash'],'role':role,'name':ent['name'],'reason':'requested reference'}
    def ensemble_ok(ens):
        if ens.get('status')!='approved' or not ens.get('members') or not set(ens['members'])<=chars.keys():return False
        if lock:
            item=lock.get('locked_entities',{}).get(ens['id'],{})
            if item.get('revision')!=ens['revision'] or item.get('ref_hash')!=ens.get('ref_hash'):return False
        for eid in ens['members']:
            e=table[eid];v=selected_variant(e,chars[eid])
            if e['status']!='approved' or v['status']!='approved' or ens.get('member_revisions',{}).get(eid)!=e['revision'] or ens.get('member_variants',{}).get(eid)!=chars[eid]['variant']:return False
        if ens.get('reference_role')!='identity':
            if ens.get('location_id')!=shot.get('location',{}).get('id'):return False
            if ens.get('context')!={'location':shot.get('location'),'initial_state':shot.get('initial_state')}:return False
        return True
    def dedup(items):
        result=[]
        for item in items:
            same=next((e for e in result if (e['path'],e['role'])==(item['path'],item['role'])),None)
            if same:same['covers']=list(dict.fromkeys(same['covers']+item['covers']))
            else:result.append(item)
        return result
    for eid in required+optional:
        if eid in table and table[eid]['type']=='ENS' and not ensemble_ok(table[eid]):raise ValidationError(f'Invalid ENS context {eid}')
    entries=dedup([make(eid) for eid in required]);ens_used=None
    if len(entries)>quota:
        for ens in sorted((e for e in pack_data['entities'] if e['type']=='ENS'),key=lambda e:e['id']):
            if not ensemble_ok(ens):continue
            covered=set(ens['members'])&set(required)
            if len(covered)<2:continue
            item=make(ens['id']);item['covers']=list(ens['members']);item['reason']='approved exact-member ENS'
            candidate=dedup([e for e in entries if not set(e['covers'])<=covered]+[item])
            if len(candidate)<len(entries):entries=candidate;ens_used=ens['id']
            if len(entries)<=quota:break
    if len(entries)>quota:raise QuotaExceededError(f'Required attachments {len(entries)} exceeds quota ({quota}); split shot or approve matching ENS')
    pruned=[]
    for eid in optional:
        item=make(eid,False)
        if item is None:pruned.append({'entity_id':eid,'reason':'optional reference has no image'});continue
        candidate=dedup(copy.deepcopy(entries)+[item])
        if len(candidate)<=quota:entries=candidate
        else:pruned.append({'entity_id':eid,'reason':'quota exhausted'})
    return {'quota':quota,'quota_used':len(entries),'manifest_refs':entries,'attachments':entries,'pruned_refs':pruned,'ens_used':ens_used}

def lint_project(project_data,pack_data,pack_dir):
    errors=validate_document(project_data, read_json(DEFAULT_KITS_DIR/'project-schema.json'))
    if errors: return {'valid':False,'errors':errors,'warnings':[],'shot_count':len(project_data.get('timeline',[])), 'computed_final_states':{}}
    finals={};instance_types={};table={e['id']:e for e in pack_data['entities']}
    def fail(msg):raise ContinuityError(msg)
    def fields(eid,state):return {k:state[k] for k in (CHAR_FIELDS if eid in table and table[eid]['type']=='CHAR' else PROP_FIELDS) if k in state}
    for shot in project_data.get('timeline',[]):
        sid=shot.get('shot_id')
        try:
            if not sid or sid in finals:fail('Missing/duplicate shot_id')
            gate_shot(pack_data,shot)
            duration=shot.get('duration_s')
            if type(duration) not in (int,float) or not math.isfinite(duration) or duration<=0:fail('Invalid duration_s')
            chars={c['id'] for c in shot.get('characters',[])};instances={p['instance_id']:p['type_id'] for p in shot.get('prop_instances',[])}
            if len(chars)!=len(shot.get('characters',[])) or len(instances)!=len(shot.get('prop_instances',[])):fail('Duplicate cast/instance id')
            for iid,tid in instances.items():
                if iid in table or (iid in instance_types and instance_types[iid]!=tid):fail('Instance id/type changed')
                instance_types[iid]=tid
            anchors=table[shot['location']['id']]['spatial_layout'].get('anchors',{});initial=shot.get('initial_state',{})
            if not (chars|instances.keys())<=initial.keys():fail('Missing initial state')
            source=shot.get('continuity_from');cut=shot.get('cut_type')
            if cut not in ('scene_establish','continuous','time_jump','location_cut'):fail('Invalid cut_type')
            if finals and not source:fail('Later shots need continuity_from and explicit state_changes for jumps')
            if source and source not in finals:fail('continuity_from must refer to earlier shot')
            if cut=='continuous' and not source:fail('continuous cut needs continuity_from')
            inherited=copy.deepcopy(finals.get(source,{}));changes=shot.get('state_changes',[])
            if changes and cut not in ('time_jump','location_cut'):fail('state_changes require explicit jump')
            for change in changes:
                eid=change.get('entity');key=change.get('field')
                if not change.get('reason') or eid not in inherited or key not in fields(eid,inherited[eid]) or inherited[eid][key]!=change.get('before'):fail('Invalid state_changes before/reason')
                inherited[eid][key]=change.get('after')
            for eid,st in initial.items():
                if (eid not in table and eid not in instance_types) or (eid in table and table[eid]['type']!='CHAR'):fail(f'Unknown/non-character initial state {eid}')
                if eid in inherited and fields(eid,inherited[eid])!=fields(eid,st):fail(f"Continuity error between '{source}' and '{sid}': {eid} holding/hands/placement/pose/fill differ")
            state=inherited;state.update(copy.deepcopy(initial))
            def invariant():
                occupied={}
                for eid,st in state.items():
                    if eid in table and table[eid]['type']=='CHAR':
                        if not all(k in st for k in CHAR_FIELDS):fail(f'{eid}: missing character state')
                        if st['pose'] not in ('standing','seated','lying') or not isinstance(st['hands'],dict) or set(st['hands'])!={'left','right'}:fail('Invalid normalized pose/hands')
                        if any(v not in (None,st['holding']) for v in st['hands'].values()):fail('hands/holding mismatch')
                        if st['holding']:
                            if st['holding'] not in state or state[st['holding']].get('held_by')!=eid or st['holding'] not in st['hands'].values():fail('holding/held_by/hands mismatch')
                    elif eid in instance_types:
                        if not all(k in st for k in ('placed_at','held_by')):fail('Missing prop state')
                        placed,held=st['placed_at'],st['held_by']
                        if (placed is None)==(held is None):fail('Prop needs exactly one holder/support')
                        if held:
                            if held not in state or state[held].get('holding')!=eid:fail('held_by/holding mismatch')
                        elif eid in instances:
                            if placed not in anchors:fail(f'Unknown placement {placed}')
                            occupied[placed]=occupied.get(placed,0)+1
                            if occupied[placed]>anchors[placed]['capacity']:fail('Anchor capacity exceeded')
                        if 'fill_fraction' in st and (type(st['fill_fraction']) not in (int,float) or not math.isfinite(st['fill_fraction']) or not 0<=st['fill_fraction']<=1):fail('Invalid fill_fraction')
            invariant();previous_time=-1
            for ev in shot.get('events',[]):
                op=ev.get('op');t=ev.get('time_s');actor=ev.get('actor');target=ev.get('target')
                if op not in OPS:fail(f'Unknown event op {op!r}; use op/time_s')
                if type(t) not in (int,float) or not math.isfinite(t) or not previous_time<t<=duration or t<0:fail('Invalid/out-of-order time_s')
                previous_time=t
                if actor not in chars or target not in instances:fail('Unknown/out-of-shot actor or target')
                person=state[actor];obj=state[target]
                def hands_ok(hands):return isinstance(hands,list) and bool(hands) and len(set(hands))==len(hands) and set(hands)<={'left','right'}
                if op=='pickup':
                    hands=ev.get('hands')
                    if not hands_ok(hands):fail('Invalid pickup hands')
                    if person['holding'] is not None or any(person['hands'][h] for h in hands):fail(f"Actor '{actor}' cannot pickup '{target}' because hands are already holding")
                    if ev.get('from') not in anchors or obj['placed_at']!=ev['from'] or obj['held_by'] is not None:fail('pickup from wrong placement')
                    obj['placed_at']=None;obj['held_by']=actor;person['holding']=target
                    for h in hands:person['hands'][h]=target
                else:
                    if person['holding']!=target or obj['held_by']!=actor:fail(f'{op}: actor is not holding target')
                    if op=='consume':
                        amount=ev.get('amount_fraction')
                        if type(amount) not in (int,float) or not math.isfinite(amount) or not 0<amount<=obj.get('fill_fraction',0):fail('Invalid consume amount_fraction')
                        obj['fill_fraction']=round(obj['fill_fraction']-amount,10)
                    else:
                        if op=='putdown':
                            if ev.get('to') not in anchors:fail('Unknown putdown anchor')
                            obj['placed_at']=ev['to'];obj['held_by']=None
                        else:
                            recipient=ev.get('recipient');hands=ev.get('recipient_hands')
                            if recipient not in chars or recipient==actor or not hands_ok(hands):fail('Invalid handover recipient/hands')
                            other=state[recipient]
                            if other['holding'] is not None or any(other['hands'][h] for h in hands):fail('Recipient hands busy')
                            other['holding']=target
                            for h in hands:other['hands'][h]=target
                            obj['held_by']=recipient
                        person['holding']=None;person['hands']={'left':None,'right':None}
                invariant()
            expected=shot.get('expected_final_state',{})
            if not (chars|instances.keys())<=expected.keys():fail('Missing expected final state')
            for eid,st in expected.items():
                if eid not in state or fields(eid,st)!=fields(eid,state[eid]):fail(f'Expected final state differs from computed events: {eid}')
            if source and cut=='continuous' and next(s for s in project_data['timeline'] if s['shot_id']==source)['location']['id']!=shot['location']['id']:fail('continuous cut changed location')
            finals[sid]=copy.deepcopy(state)
        except (KitError,KeyError,TypeError,ValueError) as exc:errors.append(f'Shot {sid}: {exc}')
    if not project_data.get('timeline'):errors.append('Empty timeline')
    return {'valid':not errors,'errors':errors,'warnings':[],'shot_count':len(project_data.get('timeline',[])),'computed_final_states':finals}

def compile_shot(project_data,shot_id,pack_data=None,pack_dir=None,mode='prod',provider=None):
    if mode not in ('prod','draft'):raise ValidationError('Unknown compilation mode')
    pack,root,lock=locked_pack(project_data);target=project_data.get('target');profile=capability(pack,target,mode=='prod')
    if provider and provider!=target['provider']:raise ValidationError('Provider override requires explicit target update')
    lint=lint_project(project_data,pack,root)
    if not lint['valid']:raise ContinuityError('; '.join(lint['errors']))
    warnings=[]
    for shot in project_data['timeline']:
        warnings.extend(gate_shot(pack,shot,mode=='prod'));resolve_refs(pack,root,shot,target=target,production=mode=='prod',lock=lock)
    shot=next((s for s in project_data['timeline'] if s['shot_id']==shot_id),None)
    if not shot:raise ValidationError(f'Unknown shot {shot_id}')
    refs=resolve_refs(pack,root,shot,target=target,production=mode=='prod',lock=lock);table={e['id']:e for e in pack['entities']};loc=table[shot['location']['id']];blocks=[]
    if warnings or not profile.get('verified'):blocks.append('[DRAFT PREVIEW]\n'+'\n'.join(warnings+([] if profile.get('verified') else ['Unverified target; manual preview only.'])))
    blocks.append('[STYLE & FIGURE CONSTRUCTION]\n'+pack['style']+'\n'+pack['global_rules']['figure_construction']+'\n'+pack['global_rules']['drawing_rule']+'\nForbid: '+', '.join(pack['global_rules']['forbid']))
    anchors=['[STATIC DESIGN ANCHORS]']
    for char in shot['characters']:
        e=table[char['id']];v=selected_variant(e,char);ident=copy.deepcopy(e['identity']);ident.update(v.get('surface_override',{}))
        anchors.append(f"- {e['id']} ({e['name']}, {v['variant_id']}): "+'; '.join(str(ident.get(k,'')) for k in ('head','torso','limbs','proportions'))+'; outfit: '+v['outfit']+'; marks: '+', '.join(ident['marks'])+'; forbid: '+', '.join(e['forbid']))
    angle=loc['approved_angles'][shot['location']['angle']];lighting=loc['lighting_variants'][shot['location']['lighting']]
    anchors.append(f"- {loc['id']} ({shot['location']['angle']}): "+'; '.join(loc['spatial_layout']['fixed_relations'])+'; '+'; '.join(str(angle.get(k,'')) for k in ('foreground','middle_ground','background'))+f"; lighting {shot['location']['lighting']}: {lighting['description']}"+'; forbid: '+', '.join(loc['forbid']))
    for inst in shot.get('prop_instances',[]):
        e=table[inst['type_id']];anchors.append(f"- {e['id']} ({inst['instance_id']}): {e['shape']}; scale: {e['scale_relative']}; faces: {json.dumps(e['visible_faces'],ensure_ascii=False)}; forbid: "+', '.join(e['forbid']))
    blocks.append('\n'.join(anchors))
    for title,value in [('FIRST FRAME & PLACEMENT',{eid:st for eid,st in shot['initial_state'].items() if eid in {c['id'] for c in shot['characters']} | {p['instance_id'] for p in shot.get('prop_instances',[])}}),('TIMED TRANSFERS & ACTION',{'acting':shot.get('narrative_action',''),'events':shot.get('events',[]),'camera':shot.get('camera',{})}),('FINAL STATE / CONTINUITY HANDOFF',{eid:lint['computed_final_states'][shot_id][eid] for eid in shot['expected_final_state']})]:blocks.append(f'[{title}]\n'+json.dumps(value,ensure_ascii=False,indent=2))
    return {'shot_id':shot_id,'mode':mode,'unresolved_warnings':warnings,'prompt':'\n\n'.join(blocks),'reference_manifest':refs,'snapshot_sha256':lock['kit_snapshot_sha256']}

def cmd_bible(pack_name_or_path='vietnamese-daily',entity_ids=None,kits_dir=None):
    pack,_=load_pack(pack_name_or_path,kits_dir);ids=set(entity_ids or [e['id'] for e in pack['entities']]);return json.dumps({'style':pack['style'],'global_rules':pack['global_rules'],'entities':[e for e in pack['entities'] if e['id'] in ids]},ensure_ascii=False,indent=2)

def cmd_list(kits_dir=None):
    for p in sorted(Path(kits_dir or DEFAULT_KITS_DIR).glob('*/kit.json')):
        d=read_json(p);print(d['pack'],d['version'],len(d['entities']),'entities')

def cmd_audit(pack_name_or_path='vietnamese-daily',kits_dir=None):
    root=find_pack_dir(pack_name_or_path,kits_dir);r=audit_pack(read_json(root/'kit.json'),root);print(json.dumps(r,ensure_ascii=False,indent=2));return int(any(r[k] for k in ('schema_errors','missing_files','hash_mismatches','conflicts')))

def main():
    parser=argparse.ArgumentParser(description=__doc__);subs=parser.add_subparsers(dest='command',required=True)
    for name in ('list','audit','check','bible','lock','compile','lint'):
        p=subs.add_parser(name);p.add_argument('--kits-dir');p.add_argument('--pack')
        if name in ('lock','compile','lint','check'):p.add_argument('--project',required=name!='check')
        if name=='bible':p.add_argument('--entities',nargs='*')
        if name=='compile':
            p.add_argument('--shot',required=True);p.add_argument('--mode',choices=['prod','draft'],default='prod');p.add_argument('--draft',action='store_true');p.add_argument('--provider');p.add_argument('--output')
    a=parser.parse_args()
    try:
        if a.command=='list':cmd_list(a.kits_dir)
        elif a.command=='bible':print(cmd_bible(a.pack or 'vietnamese-daily',a.entities,a.kits_dir))
        elif a.command=='audit' or (a.command=='check' and not a.project):return cmd_audit(a.pack or 'vietnamese-daily',a.kits_dir)
        elif a.command=='lock':print(create_lock(a.project,a.pack or 'vietnamese-daily',a.kits_dir))
        else:
            project=load_project(a.project)
            if a.pack:raise ValidationError('Locked project uses snapshot; change pack with kit lock')
            if a.command=='compile':
                result=compile_shot(project,a.shot,mode='draft' if a.draft else a.mode,provider=a.provider);payload=json.dumps(result,ensure_ascii=False,indent=2)
                if a.output:
                    output=Path(a.output);output.parent.mkdir(parents=True,exist_ok=True);output.write_text(payload+'\n')
                else:print(payload)
            else:
                pack,root,_=locked_pack(project);r=lint_project(project,pack,root);capability(pack,project.get('target'))
                for shot in project['timeline']:resolve_refs(pack,root,shot,target=project['target'])
                print(json.dumps(r,ensure_ascii=False,indent=2));return int(not r['valid'])
        return 0
    except (KitError,OSError,ValueError,KeyError,TypeError) as exc:print(f'ERROR: {exc}',file=sys.stderr);return 2

if __name__=='__main__':sys.exit(main())
