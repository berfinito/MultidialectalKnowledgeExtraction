from scripts.kg_weighting import compute_stats

def test_pmi_small_example():
    topics = [
        ["a","b","c"],   # ab, ac, bc
        ["a","b","d"],   # ab, ad, bd
        ["a","c","d"],   # ac, ad, cd
    ]
    _, edge_w, T = compute_stats(topics, "pmi")
    def pmi(u,v):
        return edge_w.get(tuple(sorted([u,v])), None)
    assert T == 3
    assert abs(pmi("a","b") - 0.0) < 1e-9
    assert abs(pmi("a","c") - 0.0) < 1e-9
    assert abs(pmi("a","d") - 0.0) < 1e-9
    assert pmi("b","c") < 0.0
    assert pmi("b","d") < 0.0
    assert pmi("c","d") < 0.0