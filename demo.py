"""Synthetic public showcase, created 2026-11-10; not the private engine."""
import json
import sys
from pathlib import Path
from copy import deepcopy

def validate(record):
    issues = []
    if record.get('data_kind') != 'synthetic':
        issues.append('demo_requires_synthetic_data')
    if not record.get('index_embedding') or record.get('index_embedding') != record.get('query_embedding'):
        issues.append('embedding_identity_mismatch')
    retrieved = set(record.get('retrieved_page_ids', []))
    context_ids = [p.get('id') for p in record.get('context_pages', [])]
    if None in context_ids or len(set(context_ids)) != len(context_ids):
        issues.append('duplicate_or_missing_context_id')
    for page in context_ids:
        if page not in retrieved:
            issues.append('context_not_retrieved:' + str(page))
    citations = record.get('answer', {}).get('citation_ids', [])
    if not citations:
        issues.append('missing_citation')
    for citation in citations:
        if citation not in context_ids:
            issues.append('citation_not_in_context:' + str(citation))
    return issues

def self_test(record):
    assert validate(record) == []
    bad = deepcopy(record)
    bad['query_embedding'] = 'different-model'
    assert 'embedding_identity_mismatch' in validate(bad)
    bad = deepcopy(record)
    bad['answer']['citation_ids'] = ['report-A:p5']
    assert 'citation_not_in_context:report-A:p5' in validate(bad)
    bad = deepcopy(record)
    bad['retrieved_page_ids'] = []
    assert 'context_not_retrieved:report-A:p3' in validate(bad)
    bad = deepcopy(record)
    bad['answer']['citation_ids'] = []
    assert 'missing_citation' in validate(bad)
    print('5 checks passed')

if __name__ == '__main__':
    record = json.loads(Path(__file__).with_name('sample.json').read_text(encoding='utf-8'))
    if '--self-test' in sys.argv:
        self_test(record)
    else:
        issues = validate(record)
        print(json.dumps({'data_kind': 'synthetic', 'valid': not issues, 'issues': issues}, ensure_ascii=False, indent=2))
        sys.exit(bool(issues))
