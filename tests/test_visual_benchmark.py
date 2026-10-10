"""Synthetic inputs exercise rules; these are not benchmark image cases."""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image
from scripts.visual_benchmark import ROOT, LIBRARY, WEIGHTS, evaluate, retrieve, validate_metadata


class BenchmarkTests(unittest.TestCase):
    def evaluation(self):
        return dict(image_id='TEST_ONLY', reviewer='test', reviewed_at='test-time',
                    image_observed=True, check_conditions='synthetic calculation input',
                    hard_constraints='pass', dimensions={
                        key: dict(status='scored', score=80, evidence='synthetic evidence')
                        for key in WEIGHTS})

    def record(self):
        value = json.loads((ROOT / LIBRARY / 'templates/metadata.json').read_text())
        value.update(image_id='TEST_ONLY', title='Temporary test input', status='active',
                     category='birthday', product_type='marquee-number', score_level='A',
                     usage='secondary-image', age_segments=['senior'],
                     visual_goals=['family-celebration'], why_good=['test rationale'],
                     redesign_required=['Recalculate scale'])
        value['teacher_score'].update(value=88, reviewer='test', source='test-source', reviewed_at='test-time')
        value['product_facts'].update(material='KT-board', source='test-source', height_cm=122,
                                      light_color='warm-yellow', characters='60')
        value['provenance'].update(source='test-source', rights_status='internal-reference-authorized',
                                   evidence_level='teacher-reviewed')
        return value

    def test_template_and_active_score_boundaries(self):
        validate_metadata(json.loads((ROOT / LIBRARY / 'templates/metadata.json').read_text()))
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            schema = root / LIBRARY / 'schemas/image-metadata.schema.json'
            schema.parent.mkdir(parents=True)
            schema.write_bytes((ROOT / LIBRARY / 'schemas/image-metadata.schema.json').read_bytes())
            asset = root / 'test-asset.png'
            Image.new('RGB', (1, 1), 'white').save(asset)
            record = self.record()
            record['asset'].update(path=asset.name, sha256=hashlib.sha256(asset.read_bytes()).hexdigest(),
                                   width_px=1, height_px=1)
            for score, level in [(86, 'A'), (89, 'A'), (90, 'S'), (92, 'S')]:
                record['teacher_score']['value'], record['score_level'] = score, level
                validate_metadata(record, root)
            for score in [85, 93]:
                record['teacher_score']['value'] = score
                with self.assertRaises(ValueError):
                    validate_metadata(record, root)
            record['teacher_score']['value'], record['score_level'] = 90, 'A'
            with self.assertRaises(ValueError):
                validate_metadata(record, root)
            record['score_level'] = 'S'
            asset.write_bytes(b'changed bytes')
            with self.assertRaises(ValueError):
                validate_metadata(record, root)

    def test_empty_library_returns_no_match(self):
        self.assertEqual(retrieve([], {})['status'], 'no_match')

    def test_match_and_scale_difference(self):
        record = self.record()
        query = dict(product_type='marquee-number', category='birthday', age='senior',
                     usage='secondary-image', lighting='warm-yellow', size_cm=122,
                     goal='family-celebration')
        result = retrieve([('test/metadata.json', record)], query)['recommendations'][0]
        self.assertEqual((result['matching_status'], result['match_score']), ('primary', 100))
        query['size_cm'] = 91
        result = retrieve([('test/metadata.json', record)], query)['recommendations'][0]
        self.assertEqual(result['matching_status'], 'conditional')
        self.assertIn('size_cm', result['differences'])

    def test_main_image_and_wrong_occasion_excluded(self):
        record = self.record()
        for query in [dict(usage='amazon-main-image'), dict(category='proposal')]:
            self.assertEqual(retrieve([('test/metadata.json', record)], query)['status'], 'no_match')

    def test_weighted_score(self):
        data = self.evaluation()
        data['dimensions']['product_prominence']['score'] = 100
        self.assertEqual(evaluate(data)['visual_quality_score'], 86)

    def test_missing_not_scored_as_zero(self):
        data = self.evaluation()
        data['dimensions']['human_realism'].update(status='pending', score=None)
        result = evaluate(data)
        self.assertIsNone(result['visual_quality_score'])
        self.assertEqual(result['partial_visual_quality_score'], 80)
        self.assertEqual(result['evidence_coverage'], 85)

    def test_not_applicable_and_hard_gate(self):
        data = self.evaluation()
        data['dimensions']['human_realism'].update(status='not_applicable', score=None)
        result = evaluate(data)
        self.assertEqual((result['visual_quality_score'], result['applicable_weight']), (80, 85))
        data['hard_constraints'] = 'fail'
        self.assertEqual(evaluate(data)['review_status'], 'blocked')

    def test_unobserved_and_invalid_scores_rejected(self):
        data = self.evaluation()
        data['image_observed'] = False
        with self.assertRaises(ValueError):
            evaluate(data)
        data['image_observed'] = True
        for score in [101, -1, True, float('nan')]:
            invalid = copy.deepcopy(data)
            invalid['dimensions']['composition']['score'] = score
            with self.assertRaises(ValueError):
                evaluate(invalid)


if __name__ == '__main__':
    unittest.main()
