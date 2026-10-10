"""Temporary synthetic images test import behavior, never add real library cases."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image
from scripts import benchmark_importer
from scripts.visual_benchmark import ROOT, LIBRARY, load_records, read_json, retrieve


class ImporterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for folder in ['schemas', 'templates']:
            shutil.copytree(ROOT / LIBRARY / folder, self.root / LIBRARY / folder)
        self.images = self.root / LIBRARY / 'images'
        self.images.mkdir()
        self.database = self.root / LIBRARY / 'database.json'
        self.database.write_text(json.dumps(dict(library_version='0.1', image_records=[], cases=[])))

    def image(self, name, color='white'):
        path = self.images / name
        path.parent.mkdir(parents=True, exist_ok=True)
        Image.new('RGB', (24, 16), color).save(path)
        return path

    def test_import_metadata_and_pending_unknown_score(self):
        self.image('birthday-number.png')
        result = benchmark_importer.import_images(self.root)
        self.assertEqual(result['imported'][0]['image_id'], 'CR001')
        records = load_records(self.root)
        self.assertEqual(len(records), 1)
        _, record = records[0]
        self.assertEqual((record['category'], record['product_type']), ('birthday', 'marquee-number'))
        self.assertEqual(record['status'], 'pending')
        self.assertIsNone(record['teacher_score']['value'])
        self.assertIsNone(record['score_level'])
        self.assertIsNone(record['visual_analysis']['composition'])
        self.assertEqual(record['visual_tags'][0], 'image:landscape')
        self.assertEqual(read_json(self.database)['cases'][0]['image_id'], 'CR001')
        self.assertEqual(retrieve(records, {})['status'], 'no_match')

    def test_repeat_duplicate_and_incremental_ids(self):
        first = self.image('a.png')
        benchmark_importer.import_images(self.root)
        shutil.copy(first, self.images / 'copy.png')
        self.assertEqual(benchmark_importer.import_images(self.root)['imported'], [])
        self.image('second.PNG', 'red')
        result = benchmark_importer.import_images(self.root)
        self.assertEqual(result['imported'][0]['image_id'], 'CR002')
        self.assertEqual(len(load_records(self.root)), 2)

    def test_review_fields_are_not_overwritten_and_relocation(self):
        path = self.image('a.png')
        benchmark_importer.import_images(self.root)
        metadata_path = self.root / read_json(self.database)['image_records'][0]
        record = read_json(metadata_path)
        record['why_good'] = ['Manually reviewed information']
        metadata_path.write_text(json.dumps(record))
        path.rename(self.images / 'renamed.png')
        result = benchmark_importer.import_images(self.root)
        self.assertEqual(result['relocated'], ['CR001'])
        record = load_records(self.root)[0][1]
        self.assertEqual(record['why_good'], ['Manually reviewed information'])
        self.assertTrue(record['asset']['path'].endswith('renamed.png'))

    def test_corrupt_file_does_not_block_valid_image(self):
        (self.images / 'a-broken.png').write_bytes(b'not an image')
        self.image('b-good.png')
        result = benchmark_importer.import_images(self.root)
        self.assertEqual(len(result['errors']), 1)
        self.assertEqual(len(result['imported']), 1)
        self.assertEqual(len(load_records(self.root)), 1)

    def test_replaced_image_not_silently_reassigned(self):
        self.image('a.png')
        benchmark_importer.import_images(self.root)
        self.image('a.png', 'blue')
        result = benchmark_importer.import_images(self.root)
        self.assertEqual(len(result['errors']), 1)
        self.assertEqual(result['imported'], [])
        self.assertEqual(result['registered_images'], 1)

    def test_interrupted_database_write_recovers_id(self):
        self.image('a.png')
        original_write = benchmark_importer.atomic_json
        def fail_database(path, data):
            if path == self.database:
                raise OSError('synthetic interrupted commit')
            original_write(path, data)
        with patch.object(benchmark_importer, 'atomic_json', side_effect=fail_database):
            with self.assertRaises(OSError):
                benchmark_importer.import_images(self.root)
        result = benchmark_importer.import_images(self.root)
        self.assertEqual(result['recovered'], ['CR001'])
        self.assertEqual(result['imported'], [])
        self.image('b.png', 'red')
        self.assertEqual(benchmark_importer.import_images(self.root)['imported'][0]['image_id'], 'CR002')

    def test_unknown_or_ambiguous_names_do_not_guess_category(self):
        self.image('unknown.png')
        self.image('birthday-proposal.png', 'blue')
        benchmark_importer.import_images(self.root)
        for _, record in load_records(self.root):
            self.assertIsNone(record['category'])

    def test_external_symlink_rejected(self):
        outside = self.root / 'outside.png'
        Image.new('RGB', (5, 5)).save(outside)
        (self.images / 'linked.png').symlink_to(outside)
        result = benchmark_importer.import_images(self.root)
        self.assertEqual(len(result['errors']), 1)
        self.assertEqual(result['imported'], [])

    def analysis(self):
        template = read_json(self.root / LIBRARY / 'templates/metadata.json')
        value = {key: template[key] for key in benchmark_importer.ANALYSIS_FIELDS}
        value.update(category='birthday', product_type='marquee-number', scene_type='home-celebration',
                     visual_tags=['product-focused'], why_good=['Clear readable product silhouette'],
                     reusable_rules=['Keep complete digits visible'], avoid=['Decorations obscure digits'])
        value['visual_analysis']['composition'] = 'Product and person side by side'
        return value

    def test_optional_analysis_and_later_enrichment(self):
        self.image('a.png')
        benchmark_importer.import_images(self.root)
        result = benchmark_importer.import_images(self.root, analyzer=lambda path: self.analysis())
        self.assertEqual(result['analyzed'], ['CR001'])
        record = load_records(self.root)[0][1]
        self.assertEqual(record['visual_features']['composition'], 'Product and person side by side')
        self.assertEqual(record['import_info']['semantic_source'], 'image-model-unverified')
        self.assertIsNone(record['teacher_score']['value'])
        self.assertEqual(record['status'], 'pending')
        with patch.object(benchmark_importer, 'apply_analysis') as method:
            benchmark_importer.import_images(self.root, analyzer=lambda path: self.analysis())
            method.assert_not_called()

    def test_analysis_failure_still_imports_pending_without_fake_scores(self):
        self.image('a.png')
        wrong = self.analysis()
        wrong['teacher_score'] = 92
        result = benchmark_importer.import_images(self.root, analyzer=lambda path: wrong)
        self.assertEqual(len(result['errors']), 1)
        self.assertEqual(len(result['imported']), 1)
        record = load_records(self.root)[0][1]
        self.assertIsNone(record['teacher_score']['value'])
        self.assertEqual(record['import_info']['semantic_source'], 'filename-hints-unverified')

    def test_analysis_preserves_manual_review(self):
        self.image('a.png')
        benchmark_importer.import_images(self.root)
        metadata_path = self.root / read_json(self.database)['image_records'][0]
        record = read_json(metadata_path)
        record['why_good'] = ['Human review must survive']
        metadata_path.write_text(json.dumps(record))
        with patch.object(benchmark_importer, 'apply_analysis') as method:
            result = benchmark_importer.import_images(self.root, analyzer=lambda path: self.analysis())
            method.assert_not_called()
        self.assertEqual(result['analysis_skipped'][0]['image_id'], 'CR001')
        self.assertEqual(read_json(metadata_path)['why_good'], ['Human review must survive'])


if __name__ == '__main__':
    unittest.main()
