"""Read-only metadata validation, retrieval and human-score calculation."""
import argparse
import hashlib
import json
import math
from pathlib import Path

from PIL import Image
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError, SchemaError

ROOT = Path(__file__).resolve().parents[1]
LIBRARY = Path('case-library/visual-benchmark-library')
WEIGHTS = dict(product_prominence=30, composition=20, lighting_realism=15,
               human_realism=15, lifestyle_authenticity=10, color_harmony=10)


def read_json(path):
    def reject_constant(value):
        raise ValueError(f'Non-finite JSON number: {value}')
    return json.loads(Path(path).read_text(), parse_constant=reject_constant)


def local_path(root, relative):
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise ValueError('Expected repository-relative path')
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('Path escapes repository')
    return path


def validate_metadata(record, root=ROOT):
    schema = read_json(root / LIBRARY / 'schemas/image-metadata.schema.json')
    Draft202012Validator(schema).validate(record)
    ratio = record['visual_features']['product_ratio']
    if ratio['value'] is not None and not (ratio['measurement'] and ratio['evidence']):
        raise ValueError('Measured product_ratio requires method and evidence')
    if record['status'] != 'active':
        return
    teacher = record['teacher_score']
    score = teacher['value']
    level = 'S' if score is not None and 90 <= score <= 92 else (
        'A' if score is not None and 86 <= score <= 89 else None)
    if level is None or level != record['score_level']:
        raise ValueError('Teacher score does not match S 90–92 / A 86–89')
    if not all(teacher[k] for k in ['reviewer', 'source', 'reviewed_at']):
        raise ValueError('Active image requires teacher-score provenance')
    facts = record['product_facts']
    if facts['material'] != 'KT-board' or not facts['source']:
        raise ValueError('Active image requires confirmed KT-board scope and source')
    provenance = record['provenance']
    if (provenance['rights_status'] != 'internal-reference-authorized'
            or provenance['evidence_level'] != 'teacher-reviewed'
            or not provenance['source']):
        raise ValueError('Active image requires authorized, teacher-reviewed source')
    asset = record['asset']
    if not all(asset.values()):
        raise ValueError('Active image requires asset dimensions, path and SHA-256')
    path = local_path(root, asset['path'])
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != asset['sha256']:
        raise ValueError('Asset missing or SHA-256 mismatch')
    with Image.open(path) as image:
        if image.size != (asset['width_px'], asset['height_px']):
            raise ValueError('Asset dimensions do not match metadata')
        image.verify()
    if not record['why_good'] or not record['redesign_required']:
        raise ValueError('Active image requires visual rationale and redesign boundaries')
    policy = record['policy_review']
    if policy['status'] == 'verified_for_main' and not all(
            policy[k] for k in ['source', 'reviewed_at', 'category_scope']):
        raise ValueError('Main-image review requires official source, date and scope')


def load_records(root=ROOT):
    database = read_json(root / LIBRARY / 'database.json')
    if database.get('library_version') != '0.1' or not isinstance(database.get('image_records'), list):
        raise ValueError('Invalid database version or image_records')
    records, ids, hashes, paths = [], set(), set(), set()
    for relative in database['image_records']:
        path = local_path(root, relative)
        if path.name != 'metadata.json' or not path.is_relative_to((root / 'case-library/benchmark-cases').resolve()):
            raise ValueError('Image metadata must reside under benchmark-cases')
        if path in paths:
            raise ValueError('Duplicate metadata path')
        paths.add(path)
        record = read_json(path)
        validate_metadata(record, root)
        identity = record['image_id']
        if not identity or identity in ids:
            raise ValueError('Missing or duplicate image_id')
        ids.add(identity)
        if record['status'] == 'active':
            digest = record['asset']['sha256']
            if digest in hashes:
                raise ValueError('Duplicate active asset SHA-256')
            hashes.add(digest)
        records.append((relative, record))
    return records


def retrieve(records, query, limit=5):
    missing = [key for key in ['product_type', 'category', 'age', 'usage', 'lighting', 'size_cm', 'goal']
               if query.get(key) is None]
    matches, excluded = [], []
    for path, record in records:
        reason = None
        if record['status'] != 'active':
            reason = 'not_active'
        elif query.get('product_type') and query['product_type'] != record['product_type']:
            reason = 'product_type_mismatch'
        elif query.get('category') and query['category'] not in [record['category'], *record['category_tags']]:
            reason = 'occasion_mismatch'
        elif query.get('usage') == 'amazon-main-image' and record['policy_review']['status'] != 'verified_for_main':
            reason = 'main_image_policy_unverified'
        if reason:
            excluded.append({'image_id': record['image_id'], 'reason': reason})
            continue
        facts = record['product_facts']
        checks = [
            ('product_type', 30, query.get('product_type') == record['product_type']),
            ('category', 25, query.get('category') in [record['category'], *record['category_tags']]),
            ('usage', 15, query.get('usage') == record['usage']),
            ('age', 10, query.get('age') in record['age_segments']),
            ('lighting', 10, query.get('lighting') == facts['light_color']),
            ('size_cm', 5, query.get('size_cm') is not None and facts['height_cm'] is not None
             and abs(query['size_cm'] - facts['height_cm']) <= 1),
            ('goal', 5, query.get('goal') in record['visual_goals']),
        ]
        exact = [key for key, _, equal in checks if query.get(key) is not None and equal]
        differences = [key for key, _, equal in checks if query.get(key) is not None and not equal]
        score = sum(weight for key, weight, equal in checks if query.get(key) is not None and equal)
        state = 'conditional' if missing or differences else 'primary'
        if not query.get('product_type') or not query.get('category'):
            state = 'technique_only'
        matches.append(dict(image_id=record['image_id'], metadata_path=path,
                            asset_path=record['asset']['path'], score_level=record['score_level'],
                            teacher_score=record['teacher_score']['value'], match_score=score,
                            matching_status=state, reasons=exact, differences=differences,
                            why_good=record['why_good'], avoid=record['avoid'],
                            redesign_required=record['redesign_required']))
    matches.sort(key=lambda x: (-x['match_score'], -x['teacher_score'], x['image_id']))
    return dict(library_version='0.1', status='matched' if matches else 'no_match',
                incomplete_query=missing, query=query, recommendations=matches[:limit], excluded=excluded)


def evaluate(data):
    for key in ['image_id', 'reviewer', 'reviewed_at', 'check_conditions']:
        if not data.get(key):
            raise ValueError(f'Missing evaluation field: {key}')
    if data.get('image_observed') is not True:
        raise ValueError('Image must actually be observed before scoring')
    hard = data.get('hard_constraints')
    if hard not in ['pass', 'fail', 'pending']:
        raise ValueError('Invalid hard_constraints')
    dimensions = data.get('dimensions', {})
    if set(dimensions) != set(WEIGHTS):
        raise ValueError('Exactly six dimensions are required')
    applicable, scored, weighted, missing = 0, 0, 0, []
    for key, weight in WEIGHTS.items():
        entry = dimensions[key]
        state, value = entry.get('status'), entry.get('score')
        if state not in ['scored', 'pending', 'unknown', 'not_applicable'] or not entry.get('evidence'):
            raise ValueError(f'Invalid dimension state or missing evidence: {key}')
        if state != 'not_applicable':
            applicable += weight
        if state == 'scored':
            if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value) or not 0 <= value <= 100:
                raise ValueError(f'Invalid score: {key}')
            scored += weight
            weighted += weight * value
        elif value is not None:
            raise ValueError('Unscored dimensions must have null score')
        if state in ['pending', 'unknown']:
            missing.append(key)
    total = round(weighted / scored, 1) if scored else None
    complete = applicable > 0 and applicable == scored
    return dict(rubric_version='visual-benchmark-v0.1', image_id=data['image_id'],
                reviewer=data['reviewer'], reviewed_at=data['reviewed_at'],
                check_conditions=data['check_conditions'], dimensions=dimensions,
                applicable_weight=applicable, scored_weight=scored,
                evidence_coverage=round(100 * scored / applicable, 1) if applicable else None,
                visual_quality_score=total if complete else None,
                partial_visual_quality_score=total if not complete else None,
                missing_dimensions=missing, hard_constraints=hard,
                review_status='blocked' if hard == 'fail' else (
                    'eligible_for_review' if complete and hard == 'pass' else 'needs_review'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('validate')
    search = commands.add_parser('retrieve')
    for key in ['product-type', 'category', 'age', 'usage', 'lighting', 'goal']:
        search.add_argument('--' + key)
    search.add_argument('--size-cm', type=float)
    search.add_argument('--limit', type=int, default=5)
    scoring = commands.add_parser('evaluate')
    scoring.add_argument('--input', required=True)
    args = parser.parse_args()
    try:
        if args.command == 'evaluate':
            result = evaluate(read_json(args.input))
        else:
            records = load_records()
            if args.command == 'validate':
                validate_metadata(read_json(ROOT / LIBRARY / 'templates/metadata.json'))
                result = dict(status='valid', registered_images=len(records),
                              active_images=sum(r['status'] == 'active' for _, r in records))
            else:
                if args.limit <= 0 or (args.size_cm is not None and (not math.isfinite(args.size_cm) or args.size_cm <= 0)):
                    raise ValueError('limit and size-cm must be positive and finite')
                query = {k: v for k, v in vars(args).items() if k not in ['command', 'limit']}
                result = retrieve(records, query, args.limit)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, OSError, KeyError, TypeError, ValidationError, SchemaError) as exc:
        parser.exit(1, f'Validation failed: {exc}\n')


if __name__ == '__main__':
    main()
