import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('localize_test', root/'__init__.py', submodule_search_locations=[str(root)])
module = importlib.util.module_from_spec(spec); sys.modules[spec.name] = module; spec.loader.exec_module(module)
from localize_test.core import Studio


class StudioTests(unittest.TestCase):
    def test_find_saved_draft_without_exposing_game_text(self):
        with tempfile.TemporaryDirectory(dir='/tmp') as tmp:
            source = Path(tmp)/'Actors.json'
            source.write_text(json.dumps([None, {'name': 'Private story text'}]))
            studio = Studio(Path(tmp)/'data')
            draft = studio.inspect(str(source))['draft_id']
            studio.translate(draft, 0, 'Translated')
            result = studio.list_drafts()
            self.assertEqual(result['drafts'][0]['draft_id'], draft)
            self.assertEqual(result['drafts'][0]['translated'], 1)
            self.assertNotIn('Private story text', str(result))

    def test_private_output_reimport_preserves_database_filename(self):
        with tempfile.TemporaryDirectory(dir='/tmp') as tmp:
            root = Path(tmp)
            source = root/'Actors.json'
            source.write_text(json.dumps([None, {'name':'Original'}]))
            private = root/'.hermes'
            studio = Studio(private/'plugin-data'/'game-localization-studio')
            draft = studio.inspect(str(source))['draft_id']
            studio.translate(draft, 0, 'Translated')
            output = Path(studio.export(draft)['path'])
            self.assertEqual(output.name, 'Actors.json')
            second = studio.inspect(str(output))
            self.assertEqual(studio.get(second['draft_id'])['units'][0]['source'], 'Translated')
            unrelated = private/'unrelated.json'
            unrelated.write_text('{}')
            with self.assertRaisesRegex(ValueError, 'Credential/configuration'):
                studio.inspect(str(unrelated))

    def test_custom_profile_configuration_stays_blocked(self):
        with tempfile.TemporaryDirectory(dir='/tmp') as tmp:
            profile = Path(tmp)/'custom-profile'
            profile.mkdir()
            source = profile/'unrelated.json'
            source.write_text('{}')
            studio = Studio(profile/'plugin-data'/'game-localization-studio')
            with self.assertRaisesRegex(ValueError, 'Credential/configuration'):
                studio.inspect(str(source))

    def test_tampered_source_copy_refuses_export(self):
        with tempfile.TemporaryDirectory(dir='/tmp') as tmp:
            source = Path(tmp)/'Map001.json'
            source.write_text(json.dumps({'events': [{'pages': [{'list': [{'code': 101, 'indent': 0, 'parameters': []}, {'code': 401, 'indent': 0, 'parameters': ['Original']}]}]}]}))
            studio = Studio(Path(tmp)/'data'); draft = studio.inspect(str(source))['draft_id']
            studio.translate(draft, 0, 'Translated')
            (Path(tmp)/'data'/draft/'source.json').write_text('{}')
            with self.assertRaisesRegex(ValueError, 'source bytes changed'): studio.export(draft)

    def test_missing_choice_end_does_not_capture_later_branches(self):
        with tempfile.TemporaryDirectory(dir='/tmp') as tmp:
            source = Path(tmp)/'CommonEvents.json'
            commands = [{'code': 102, 'indent': 0, 'parameters': [['Yes'], 0]},
                        {'code': 402, 'indent': 0, 'parameters': [0, 'Yes']},
                        {'code': 102, 'indent': 0, 'parameters': [['Yes'], 0]},
                        {'code': 402, 'indent': 0, 'parameters': [0, 'Yes']},
                        {'code': 404, 'indent': 0, 'parameters': []}]
            source.write_text(json.dumps([None, {'list': commands}]))
            studio = Studio(Path(tmp)/'data'); draft = studio.inspect(str(source))['draft_id']
            with self.assertRaisesRegex(ValueError, 'incomplete'): studio.translate(draft, 0, 'Oui')
            studio.translate(draft, 1, 'Oui')
            result = json.loads(Path(studio.export(draft)['path']).read_text())[1]['list']
            self.assertEqual(result[1]['parameters'][1], 'Yes')
            self.assertEqual(result[3]['parameters'][1], 'Oui')

    def test_system_fields_do_not_expose_internal_variable_names(self):
        with tempfile.TemporaryDirectory(dir='/tmp') as tmp:
            source = Path(tmp)/'System.json'
            source.write_text(json.dumps({'gameTitle': 'Original Game', 'currencyUnit': 'Gold', 'variables': ['', 'internal_secret_switch'], 'versionId': 42}))
            studio = Studio(Path(tmp)/'data'); draft = studio.inspect(str(source))['draft_id']
            units = studio.get(draft)['units']
            self.assertEqual([u['path'] for u in units], [['gameTitle'], ['currencyUnit']])
            studio.translate(draft, 0, 'Jeu original')
            result = json.loads(Path(studio.export(draft)['path']).read_text())
            self.assertEqual(result['variables'], ['', 'internal_secret_switch'])
            self.assertEqual(result['versionId'], 42)

    def test_database_fields_leave_internal_notes_and_ids_untouched(self):
        with tempfile.TemporaryDirectory(dir='/tmp') as tmp:
            source = Path(tmp)/'Items.json'
            source.write_text(json.dumps([None, {'id': 1, 'name': 'Potion', 'description': 'Restore %1 HP', 'note': '<internal:1>', 'price': 50}]))
            studio = Studio(Path(tmp)/'data'); draft = studio.inspect(str(source))['draft_id']
            units = studio.get(draft)['units']
            self.assertEqual([u['path'][-1] for u in units], ['name', 'description'])
            studio.translate(draft, 0, 'Potion FR'); studio.translate(draft, 1, 'Restaure %1 PV')
            item = json.loads(Path(studio.export(draft)['path']).read_text())[1]
            self.assertEqual(item['note'], '<internal:1>'); self.assertEqual(item['price'], 50)
            self.assertEqual(item['description'], 'Restaure %1 PV')

    def test_real_control_codes_and_placeholders(self):
        from localize_test.core import tokens, compatible_controls
        self.assertEqual(tokens(r'\C[3] \V[12] %1 \!'), {r'\C[3]': 1, r'\V[12]': 1, '%1': 1, r'\!': 1})
        self.assertFalse(compatible_controls(r'\C[3] Red \C[0]', r'\C[0] Rouge \C[3]'))
        self.assertTrue(compatible_controls(r'\N[1] has %1 coins', r'%1 pièces pour \N[1]'))

    def test_choice_branch_aliases_and_ambiguous_originals(self):
        with tempfile.TemporaryDirectory(dir='/tmp') as tmp:
            source = Path(tmp)/'CommonEvents.json'
            commands = [{'code': 102, 'indent': 0, 'parameters': [['Yes', 'No'], 0]},
                        {'code': 402, 'indent': 0, 'parameters': [0, 'Yes']},
                        {'code': 402, 'indent': 0, 'parameters': [1, 'internal_label']},
                        {'code': 404, 'indent': 0, 'parameters': []}]
            source.write_text(json.dumps([None, {'list': commands}]))
            studio = Studio(Path(tmp)/'data'); draft = studio.inspect(str(source))['draft_id']
            studio.translate(draft, 0, 'Oui')
            with self.assertRaises(ValueError): studio.translate(draft, 1, 'Non')
            result = json.loads(Path(studio.export(draft)['path']).read_text())[1]['list']
            self.assertEqual(result[0]['parameters'][0], ['Oui', 'No'])
            self.assertEqual(result[1]['parameters'], [0, 'Oui'])
            self.assertEqual(result[2]['parameters'], [1, 'internal_label'])

    def test_source_controls_blank_rows_and_original_preserved(self):
        with tempfile.TemporaryDirectory(dir='/tmp') as tmp:
            source = Path(tmp)/'Map001.json'
            original = {'events': [None, {'pages': [{'list': [
                {'code': 101, 'indent': 0, 'parameters': ['', 0, 0, 2]},
                {'code': 401, 'indent': 0, 'parameters': ['Hello \\N[1].']},
                {'code': 401, 'indent': 0, 'parameters': ['']},
                {'code': 401, 'indent': 0, 'parameters': ['Welcome.']},
                {'code': 355, 'indent': 0, 'parameters': ['doNotTranslate()']},
            ]}]}]}
            source.write_text(json.dumps(original)); before = source.read_bytes()
            studio = Studio(Path(tmp)/'data'); draft = studio.inspect(str(source), message_rows=3)['draft_id']
            with self.assertRaises(ValueError): studio.translate(draft, 0, 'Bonjour.')
            studio.translate(draft, 0, 'Bonjour \\N[1].')
            studio.translate(draft, 1, 'Bienvenue.\nSuite.')
            self.assertFalse(studio.validate(draft)['structural_ok'])
            studio.translate(draft, 1, 'Bienvenue.')
            output = json.loads(Path(studio.export(draft)['path']).read_text())
            self.assertEqual(source.read_bytes(), before)
            commands = output['events'][1]['pages'][0]['list']
            self.assertEqual(commands[1]['parameters'][0], 'Bonjour \\N[1].')
            self.assertEqual(commands[2]['parameters'][0], '')
            self.assertEqual(commands[4]['parameters'][0], 'doNotTranslate()')


if __name__ == '__main__': unittest.main()
