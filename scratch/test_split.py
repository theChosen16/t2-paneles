import re

def test_split(text):
    tokens = re.split(r'(\*\*[^*]+\*\*|\_[^_]+\_|\[[^\]]+\]|\^[^^]+\^)', text)
    print("Tokens:")
    for t in tokens:
        if not t:
            continue
        print(f"  Token: {repr(t)}")

text1 = "• **Coeficientes Térmicos (_α_[_Isc_] y _β_[_Voc_]):\n"
test_split(text1)

text2 = "• **Condiciones de Referencia (SRC):** Se filtraron mediciones instantáneas bajo condiciones estándar (_G_ ≈ 1000 W/m² y temperatura de celda _T_[_c_] ≈ 25°C)."
test_split(text2)
