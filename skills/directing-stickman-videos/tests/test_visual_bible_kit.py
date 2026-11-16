"""Regression coverage for snapshot integrity, gates, transport refs and event causality."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL/'scripts'))
import visual_bible_kit as kit


def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')


class VisualBibleRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.live, cls.live_root = kit.load_pack()
        cls.example = json.loads((SKILL/'examples/project-benchmark-2shot.json').read_text())

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.pack_root = self.root/'source'; self.pack_root.mkdir()
        self.pack = copy.deepcopy(self.live)
        ids = {'CHAR_01_AN','CHAR_02_BO','LOC_03_PHONG_KHACH','PROP_03_TACH_TRA','ENS_01_AN_VA_BO'}
        self.pack['entities'] = [e for e in self.pack['entities'] if e['id'] in ids]
        self.table = {e['id']:e for e in self.pack['entities']}
        for e in self.pack['entities']:
            for obj in [e]+e.get('approved_variants',[]):
                if obj.get('ref'):
                    path = self.pack_root/obj['ref']; path.parent.mkdir(exist_ok=True)
                    path.write_bytes(('synthetic-test-image:'+obj['ref']).encode())
                    obj['ref_hash'] = kit.sha256_file(path)
        self.pack['meta']['provider_limits']['example-provider']['example-model']['reference_images']['verified'] = True
        self.pack['meta']['provider_limits']['example-provider']['example-model']['reference_images']['note'] = 'Synthetic verified fixture; never a real provider claim.'
        self.path = self.root/'project.json'
        project = copy.deepcopy(self.example);project.pop('lockfile',None)
        save(self.path, project)
        self.relock()

    def relock(self):
        save(self.pack_root/'kit.json',self.pack)
        kit.create_lock(self.path,str(self.pack_root))
        self.project = kit.load_project(self.path)
        self.snapshot, self.snapshot_root, self.lock = kit.locked_pack(self.project)

    def compile(self, mode='prod',shot='S01'):
        return kit.compile_shot(self.project,shot,mode=mode)

    def lint(self):
        return kit.lint_project(self.project,self.snapshot,self.snapshot_root)

    def bad_lint(self):
        result = self.lint()
        self.assertFalse(result['valid'], result)
        with self.assertRaises(kit.KitError): self.compile()
        return ' '.join(result['errors'])

    def test_live_pack_schema_and_twelve_image_hashes(self):
        report=kit.audit_pack(self.live,self.live_root)
        self.assertEqual(report['valid_refs'],12)
        self.assertFalse(report['schema_errors'] or report['hash_mismatches'] or report['missing_files'])

    def test_happy_path_prod_has_complete_prompt_and_separate_manifest(self):
        result=self.compile()
        for block in ('STYLE & FIGURE CONSTRUCTION','STATIC DESIGN ANCHORS','FIRST FRAME & PLACEMENT','TIMED TRANSFERS & ACTION','FINAL STATE / CONTINUITY HANDOFF'):
            self.assertIn('['+block+']',result['prompt'])
        self.assertNotIn('[REFERENCE MANIFEST]',result['prompt'])
        self.assertEqual(result['reference_manifest']['quota_used'],2)
        self.assertEqual(len(result['reference_manifest']['attachments']),2)
        self.assertIn('"placed_at": null',result['prompt'])

    def test_original_examples_lint_and_preview_but_reject_production(self):
        for name in ('project-benchmark-2shot.json','benchmark-sequence-6shot.json'):
            project=kit.load_project(SKILL/'examples'/name)
            pack,root,_=kit.locked_pack(project)
            self.assertTrue(kit.lint_project(project,pack,root)['valid'])
            sid=project['timeline'][0]['shot_id']
            self.assertIn('DRAFT PREVIEW',kit.compile_shot(project,sid,mode='draft')['prompt'])
            with self.assertRaisesRegex(kit.ValidationError,'verified'):kit.compile_shot(project,sid)

    def test_missing_lock_rejected(self):
        self.project.pop('lockfile')
        with self.assertRaisesRegex(kit.ValidationError,'lockfile'):self.compile()

    def test_incomplete_lock_rejected(self):
        self.lock['locked_entities'].pop('CHAR_02_BO')
        save(self.root/self.project['lockfile'],self.lock)
        with self.assertRaisesRegex(kit.ValidationError,'dependency'):self.compile()

    def test_stale_revision_is_error(self):
        self.lock['locked_entities']['CHAR_02_BO']['revision']='stale'
        save(self.root/self.project['lockfile'],self.lock)
        with self.assertRaises(kit.ValidationError):self.compile()

    def test_live_pack_edits_do_not_change_locked_prompt(self):
        before=self.compile()['prompt']
        self.pack['entities'][0]['identity']['head']='different head'
        save(self.pack_root/'kit.json',self.pack)
        self.assertEqual(self.compile()['prompt'],before)

    def test_snapshot_description_tampering_rejected(self):
        self.snapshot['style']='modified'
        save(self.snapshot_root/'kit.json',self.snapshot)
        with self.assertRaisesRegex(kit.ValidationError,'Snapshot SHA'):self.compile()

    def test_snapshot_image_tampering_rejected_even_in_draft(self):
        (self.snapshot_root/self.table['CHAR_02_BO']['ref']).write_bytes(b'changed image')
        with self.assertRaisesRegex(kit.ValidationError,'SHA-256'):self.compile('draft')

    def test_missing_required_snapshot_image_rejected(self):
        (self.snapshot_root/self.table['CHAR_02_BO']['ref']).unlink()
        with self.assertRaisesRegex(kit.ValidationError,'Missing'):self.compile()

    def test_unknown_required_ref_rejected(self):
        shot=copy.deepcopy(self.project['timeline'][0]);shot['required_refs'].append('UNKNOWN')
        with self.assertRaisesRegex(kit.ValidationError,'reference'):kit.resolve_refs(self.snapshot,self.snapshot_root,shot,target=self.project['target'])

    def test_required_ref_without_image_rejected(self):
        shot=copy.deepcopy(self.project['timeline'][0]);shot['required_refs'].append('PROP_03_TACH_TRA')
        with self.assertRaisesRegex(kit.ValidationError,'required reference'):kit.resolve_refs(self.snapshot,self.snapshot_root,shot,target=self.project['target'])

    def test_reference_hash_checked_by_resolver(self):
        self.snapshot['entities'][0]['approved_variants'][0]['ref_hash']='0'*64
        with self.assertRaisesRegex(kit.ValidationError,'SHA-256'):
            shot=copy.deepcopy(self.project['timeline'][0]);shot['characters'].append({'id':'CHAR_01_AN','variant':'DEFAULT_DAILY'});shot['required_refs'].append('CHAR_01_AN')
            kit.resolve_refs(self.snapshot,self.snapshot_root,shot,target=self.project['target'])

    def test_gate_draft_prop_and_deprecated_character(self):
        for eid,status in [('PROP_03_TACH_TRA','draft'),('CHAR_02_BO','deprecated')]:
            original=self.table[eid]['status'];self.table[eid]['status']=status;self.relock()
            with self.assertRaisesRegex(kit.ValidationError,'Production compilation rejected'):self.compile()
            self.assertIn(eid,self.compile('draft')['prompt'])
            self.table[eid]['status']=original

    def test_gate_draft_variant(self):
        self.project['timeline'][0]['characters'][0]['variant']='BO_DARK_SHIRT'
        with self.assertRaisesRegex(kit.ValidationError,'BO_DARK_SHIRT'):self.compile()

    def test_gate_draft_angle_and_lighting(self):
        loc=self.table['LOC_03_PHONG_KHACH']
        for container,key in [('approved_angles','table_close'),('lighting_variants','morning')]:
            loc[container][key]['status']='draft';self.relock()
            with self.assertRaisesRegex(kit.ValidationError,key):self.compile()
            self.assertIn(key,self.compile('draft')['prompt'])
            loc[container][key]['status']='approved'

    def test_evening_changes_prompt_without_daylight_leak(self):
        morning=self.compile()['prompt']
        self.project['timeline'][0]['location']['lighting']='evening'
        evening=self.compile()['prompt']
        self.assertNotEqual(morning,evening)
        self.assertIn('ngoài cửa sổ là trời tối',evening)
        self.assertNotIn('nắng dịu buổi sáng',evening)
        self.assertNotIn('gentle daylight',evening)

    def test_unknown_capability_rejected_no_default_quota(self):
        self.project['target']['model']='unknown'
        with self.assertRaisesRegex(kit.ValidationError,'Unknown capability'):self.compile()

    def test_no_pickup_but_claimed_final_state_rejected(self):
        self.project['timeline'][0]['events']=[]
        self.assertIn('computed',self.bad_lint())

    def test_unknown_op_and_invalid_actor_time_rejected(self):
        for patch in ({'op':'teleport'},{'actor':'GHOST'},{'time_s':999},{'time_s':-1}):
            original=copy.deepcopy(self.project['timeline'][0]['events'][0]);self.project['timeline'][0]['events'][0].update(patch)
            self.bad_lint();self.project['timeline'][0]['events'][0]=original

    def test_legacy_action_field_rejected(self):
        ev=self.project['timeline'][0]['events'][0];ev['action']=ev.pop('op')
        self.assertIn('missing op',self.bad_lint())

    def test_wrong_pickup_source_rejected(self):
        self.project['timeline'][0]['events'][0]['from']='tea_table_surface'
        self.assertIn('wrong placement',self.bad_lint())

    def test_initial_held_by_mismatch_rejected(self):
        self.project['timeline'][0]['initial_state']['cup_01']['held_by']='CHAR_02_BO'
        self.bad_lint()

    def test_continuity_cannot_reset_fill(self):
        self.project['timeline'][1]['initial_state']['cup_01']['fill_fraction']=0.5
        self.assertIn('Continuity error',self.bad_lint())

    def test_consume_cannot_exceed_content(self):
        self.project['timeline'][1]['events'][0]['amount_fraction']=1.1
        self.assertIn('amount_fraction',self.bad_lint())

    def test_no_auto_half_full_after_one_sip(self):
        self.project['timeline'][1]['expected_final_state']['cup_01']['fill_fraction']=0.5
        self.assertIn('computed',self.bad_lint())

    def test_same_time_events_rejected(self):
        self.project['timeline'][1]['events'].append(copy.deepcopy(self.project['timeline'][1]['events'][0]))
        self.assertIn('time_s',self.bad_lint())

    def test_compile_lints_other_shots(self):
        self.project['timeline'][1]['events']=[]
        with self.assertRaises(kit.ContinuityError):self.compile(shot='S01')

    def test_quota_and_dedup(self):
        shot=copy.deepcopy(self.project['timeline'][0]);shot['required_refs']*=3
        result=kit.resolve_refs(self.snapshot,self.snapshot_root,shot,target=self.project['target'])
        self.assertEqual(result['quota_used'],2)
        profile=self.snapshot['meta']['provider_limits']['example-provider']['example-model']['reference_images'];profile['max_refs']=1
        with self.assertRaises(kit.QuotaExceededError):kit.resolve_refs(self.snapshot,self.snapshot_root,shot,target=self.project['target'])

    def test_optional_ref_kept_when_slot_available(self):
        self.assertEqual(self.compile(shot='S02')['reference_manifest']['quota_used'],2)

    def test_ens_draft_or_wrong_members_never_substitutes(self):
        shot=copy.deepcopy(self.project['timeline'][0]);shot['characters'].append({'id':'CHAR_01_AN','variant':'DEFAULT_DAILY'});shot['required_refs'].append('CHAR_01_AN')
        self.snapshot['meta']['provider_limits']['example-provider']['example-model']['reference_images']['max_refs']=2
        ens=next(e for e in self.snapshot['entities'] if e['type']=='ENS')
        ens['ref']=self.table['CHAR_01_AN']['ref'];ens['ref_hash']=self.table['CHAR_01_AN']['ref_hash'];ens['reference_role']='identity'
        for status,revision in [('draft',self.table['CHAR_01_AN']['revision']),('approved','stale')]:
            ens['status']=status;ens['member_revisions']['CHAR_01_AN']=revision
            with self.assertRaises(kit.QuotaExceededError):kit.resolve_refs(self.snapshot,self.snapshot_root,shot,target=self.project['target'])
        ens['member_revisions']['CHAR_01_AN']=self.table['CHAR_01_AN']['revision']
        self.assertEqual(kit.resolve_refs(self.snapshot,self.snapshot_root,shot,target=self.project['target'])['ens_used'],ens['id'])
        ens['reference_role']='composition';ens['context']=None
        with self.assertRaises(kit.QuotaExceededError):kit.resolve_refs(self.snapshot,self.snapshot_root,shot,target=self.project['target'])

    def test_schema_requires_character_identity(self):
        broken=copy.deepcopy(self.pack);broken['entities'][0].pop('identity')
        self.assertTrue(kit.validate_pack_schema(broken))

    def test_user_prop_decisions_preserved(self):
        table={e['id']:e for e in self.live['entities']}
        self.assertEqual(table['PROP_02_XE_MAY']['shape'],'plain motorbike, blank license plate with no numbers and no letters')
        self.assertNotIn('beige',table['PROP_03_TACH_TRA']['shape'])

    def test_handover_putdown_and_capacity(self):
        project=copy.deepcopy(self.project)
        shot=project['timeline'][0]
        project['timeline']=[shot]
        shot['characters'].append({'id':'CHAR_01_AN','variant':'DEFAULT_DAILY'})
        an={'pose':'seated','seat':'sofa','holding':None,'hands':{'left':None,'right':None}}
        shot['initial_state']['CHAR_01_AN']=copy.deepcopy(an)
        shot['expected_final_state']=copy.deepcopy(shot['initial_state'])
        shot['events'] += [
            {'time_s':2,'op':'handover','actor':'CHAR_02_BO','recipient':'CHAR_01_AN','recipient_hands':['right'],'target':'cup_01'},
            {'time_s':3,'op':'putdown','actor':'CHAR_01_AN','target':'cup_01','to':'on_tea_table_center'}]
        result=kit.lint_project(project,self.snapshot,self.snapshot_root)
        self.assertTrue(result['valid'],result['errors'])
        shot['prop_instances'].append({'instance_id':'cup_02','type_id':'PROP_03_TACH_TRA'})
        for field in ('initial_state','expected_final_state'):
            shot[field]['cup_02']={'held_by':None,'placed_at':'on_tea_table_center','fill_fraction':1.0}
        self.assertFalse(kit.lint_project(project,self.snapshot,self.snapshot_root)['valid'])
        # Multiple cups on a non-exclusive table surface are legitimate.
        shot['initial_state']['cup_01']['placed_at']='tea_table_surface'
        shot['initial_state']['cup_02']['placed_at']='tea_table_surface'
        shot['expected_final_state']=copy.deepcopy(shot['initial_state'])
        shot['events']=[]
        self.assertTrue(kit.lint_project(project,self.snapshot,self.snapshot_root)['valid'])

    def test_jump_cannot_silently_reset_state(self):
        self.project['timeline'][1]['cut_type']='time_jump'
        self.project['timeline'][1]['initial_state']['cup_01']['fill_fraction']=0.5
        self.bad_lint()
        self.project['timeline'][1]['continuity_from']=None
        self.bad_lint()

    def test_initial_state_offscreen_actor_not_in_prompt(self):
        # Physical ledger may carry off-screen cast; its design/state must not leak.
        shot=self.project['timeline'][0]
        shot['initial_state']['CHAR_01_AN']={'pose':'seated','seat':'sofa','holding':None,'hands':{'left':None,'right':None}}
        prompt=self.compile()['prompt']
        self.assertNotIn('CHAR_01_AN',prompt)

    def test_duplicate_ids_and_unknown_angle_fail_closed(self):
        self.project['timeline'][1]['shot_id']='S01'
        self.bad_lint()
        self.project['timeline'][1]['shot_id']='S02'
        self.project['timeline'][0]['location']['angle']='unknown'
        self.bad_lint()

    def test_cli_wrapper_and_output_package(self):
        output=self.root/'output.json'
        result=subprocess.run([sys.executable,str(SKILL/'scripts/visual-bible-kit.py'),'compile','--project',str(self.path),'--shot','S01','--output',str(output)],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        payload=json.loads(output.read_text());self.assertTrue(payload['reference_manifest']['attachments'])


if __name__=='__main__':unittest.main()
