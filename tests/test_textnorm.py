import pytest
from mdke.utils.textnorm import normalize_text

@pytest.mark.parametrize("inp,expect", [
    ("Merhaba\u00A0dünya", "merhaba dünya"),      # NBSP -> boşluk, lowercase
    ("“Akıllı” ‘tirnak’", '"akıllı" \'tirnak\''), # akıllı tırnak -> düz, lowercase
    (" Çok   boşluk\tvar \n ", "çok boşluk var"), # whitespace sıkıştırma, lowercase
    ("A… B? C! D.", "a... b? c! d."),             # ellipsis NFKC -> "..."
])
def test_normalize_basic(inp, expect):
    assert normalize_text(inp, "tr") == expect