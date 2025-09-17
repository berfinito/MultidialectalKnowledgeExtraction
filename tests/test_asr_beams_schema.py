from pathlib import Path
import json

def test_beams_schema_present_if_file_exists():
    # TR demo dosyası varsayılan; yoksa testi es geç
    p = Path("data/interim/asr/whisper_tr_validation_beam4_demo_beams.jsonl")
    if not p.exists():
        return
    with p.open(encoding="utf-8") as f:
        rec = json.loads(next(f))
    # Temel alanlar
    for k in ("utt_id","gt_text","pred_text","alt_hyps","beam_scores","beam_size"):
        assert k in rec
    assert isinstance(rec["alt_hyps"], list)
    assert isinstance(rec["beam_scores"], list)