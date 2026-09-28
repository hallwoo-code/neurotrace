"""Exercise deployed demo and real model paths, using only supplied sample data."""
import json
import os
from pathlib import Path
import sys
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from neurotrace.engine import exports, investigate, load_samples, review

MODEL = 'modelscope.cn/unsloth/Qwen3.8-27B-GGUF:latest'
BASE = 'http://127.0.0.1:11434'
os.environ.setdefault('OLLAMA_TIMEOUT', '180')


def main():
    corpus = load_samples()
    question = '情绪唤醒度是否会影响 LPC 振幅？'
    demo = investigate(question, corpus)
    assert demo['cards'] and not demo['error']
    review(demo, demo['cards'][0]['card_id'], 'rejected')
    assert len(demo['finding']['active_card_ids']) == len(demo['cards']) - 1
    assert set(exports(demo)) == {'md', 'json', 'csv'}
    print('DEMO_PASS', flush=True)
    request = urllib.request.Request(BASE + '/api/chat', data=json.dumps({
        'model': MODEL, 'stream': False, 'think': False, 'format': 'json',
        'options': {'num_predict': 64, 'num_ctx': 8192, 'temperature': 0},
        'messages': [{'role': 'user', 'content': 'Return only this JSON object: {"service_ready": true}'}],
    }).encode(), headers={'Content-Type': 'application/json'})
    started = time.perf_counter()
    with urllib.request.urlopen(request, timeout=300) as response:
        warm = json.load(response)
    assert json.loads(warm['message']['content'])['service_ready'] is True
    print(json.dumps({'warmup_seconds': round(time.perf_counter()-started, 2), 'model': warm.get('model')}), flush=True)
    case = investigate(question, corpus, 'ollama', BASE, MODEL, lambda e: print(json.dumps(e, ensure_ascii=False), flush=True))
    if case['error']:
        raise RuntimeError(case['error'])
    assert len(case['relations']) == len(case['cards']) > 0
    assert case['finding']['is_demo']  # Model is real; supplied evidence remains unverified.
    assert all(exports(case).values())
    results = {
        'demo_passed': True, 'real_model_passed': True,
        'model': case['model'], 'elapsed_seconds': case['elapsed_seconds'],
        'cards': len(case['cards']), 'relations': len(case['relations']),
        'usage': case.get('model_usage'), 'finding_status': case['finding']['status'],
        'note': 'Real inference on handoff sample evidence, not a scientific accuracy evaluation.',
    }
    output = ROOT / 'runtime'
    output.mkdir(exist_ok=True)
    (output / 'deployment_smoke.json').write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(results, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
