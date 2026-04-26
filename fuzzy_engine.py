"""
fuzzy_engine.py
Lokasi: scholarcheck/fuzzy_engine.py

Perubahan v3:
- Membership function IPK, penghasilan, tanggungan direvisi agar lebih realistis
- Output membership lebih tersebar (tidak numpuk di bawah)
- Threshold kategori disesuaikan
- IPK tinggi + penghasilan rendah = Sangat Layak meski tanpa prestasi
"""

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

BOBOT_TINGKAT = {'lokal': 20, 'provinsi': 40, 'nasional': 70, 'internasional': 100}
BOBOT_JUARA   = {1: 1.00, 2: 0.75, 3: 0.50, 'harapan': 0.25}


def hitung_skor_prestasi(prestasi_list: list) -> float:
    if not prestasi_list:
        return 0.0
    scores = []
    for p in prestasi_list[:3]:
        base = BOBOT_TINGKAT.get(str(p.get('tingkat', '')).lower(), 0)
        juara_key = p.get('juara', 0)
        try:
            juara_key = int(juara_key)
        except (ValueError, TypeError):
            juara_key = str(juara_key).lower()
        mult = BOBOT_JUARA.get(juara_key, 0)
        scores.append(base * mult)
    scores.sort(reverse=True)
    if len(scores) == 1:
        total = scores[0]
    elif len(scores) == 2:
        total = scores[0] + scores[1] * 0.30
    else:
        total = scores[0] + scores[1] * 0.30 + scores[2] * 0.15
    return min(round(total, 2), 100.0)


def normalisasi_penghasilan(v): return min(float(v), 10_000_000)
def normalisasi_tanggungan(v):  return min(int(v), 10)


def build_fuzzy_system():
    ipk         = ctrl.Antecedent(np.arange(0, 4.01, 0.01), 'ipk')
    penghasilan = ctrl.Antecedent(np.arange(0, 10_000_001, 1), 'penghasilan')
    tanggungan  = ctrl.Antecedent(np.arange(0, 11, 1), 'tanggungan')
    prestasi    = ctrl.Antecedent(np.arange(0, 101, 1), 'prestasi')
    kelayakan   = ctrl.Consequent(np.arange(0, 101, 1), 'kelayakan')

    # IPK — batas 'tinggi' mulai dari 3.0 (realistis untuk beasiswa)
    ipk['rendah']  = fuzz.trimf(ipk.universe, [0.00, 0.00, 2.75])
    ipk['sedang']  = fuzz.trimf(ipk.universe, [2.25, 3.00, 3.50])
    ipk['tinggi']  = fuzz.trimf(ipk.universe, [3.00, 4.00, 4.00])

    # Penghasilan — batas 'rendah' sampai 2.5jt (UMR rata2 daerah)
    penghasilan['rendah']  = fuzz.trimf(penghasilan.universe, [0,         0,          2_500_000])
    penghasilan['sedang']  = fuzz.trimf(penghasilan.universe, [1_500_000, 4_000_000,  6_500_000])
    penghasilan['tinggi']  = fuzz.trimf(penghasilan.universe, [5_000_000, 10_000_000, 10_000_000])

    # Tanggungan
    tanggungan['sedikit'] = fuzz.trimf(tanggungan.universe, [0, 0,  3])
    tanggungan['sedang']  = fuzz.trimf(tanggungan.universe, [2, 5,  7])
    tanggungan['banyak']  = fuzz.trimf(tanggungan.universe, [5, 10, 10])

    # Prestasi (0 = tidak ada)
    prestasi['rendah']  = fuzz.trimf(prestasi.universe, [0,  0,  40])
    prestasi['sedang']  = fuzz.trimf(prestasi.universe, [25, 50, 75])
    prestasi['tinggi']  = fuzz.trimf(prestasi.universe, [60, 100, 100])

    # Output — lebih tersebar supaya centroid proporsional
    kelayakan['tidak_layak']   = fuzz.trimf(kelayakan.universe, [0,  0,  20])
    kelayakan['kurang_layak']  = fuzz.trimf(kelayakan.universe, [10, 25, 40])
    kelayakan['cukup_layak']   = fuzz.trimf(kelayakan.universe, [35, 50, 65])
    kelayakan['layak']         = fuzz.trimf(kelayakan.universe, [60, 75, 88])
    kelayakan['sangat_layak']  = fuzz.trimf(kelayakan.universe, [82, 100, 100])

    rules = [
        # === IPK TINGGI ===
        ctrl.Rule(ipk['tinggi'] & penghasilan['rendah'] & tanggungan['banyak']  & prestasi['tinggi'], kelayakan['sangat_layak']),
        ctrl.Rule(ipk['tinggi'] & penghasilan['rendah'] & tanggungan['banyak']  & prestasi['sedang'], kelayakan['sangat_layak']),
        ctrl.Rule(ipk['tinggi'] & penghasilan['rendah'] & tanggungan['banyak']  & prestasi['rendah'], kelayakan['sangat_layak']),
        ctrl.Rule(ipk['tinggi'] & penghasilan['rendah'] & tanggungan['sedang']  & prestasi['tinggi'], kelayakan['sangat_layak']),
        ctrl.Rule(ipk['tinggi'] & penghasilan['rendah'] & tanggungan['sedang']  & prestasi['sedang'], kelayakan['layak']),
        ctrl.Rule(ipk['tinggi'] & penghasilan['rendah'] & tanggungan['sedang']  & prestasi['rendah'], kelayakan['layak']),
        ctrl.Rule(ipk['tinggi'] & penghasilan['rendah'] & tanggungan['sedikit'] & prestasi['tinggi'], kelayakan['layak']),
        ctrl.Rule(ipk['tinggi'] & penghasilan['rendah'] & tanggungan['sedikit'] & prestasi['sedang'], kelayakan['layak']),
        ctrl.Rule(ipk['tinggi'] & penghasilan['rendah'] & tanggungan['sedikit'] & prestasi['rendah'], kelayakan['cukup_layak']),
        ctrl.Rule(ipk['tinggi'] & penghasilan['sedang'] & tanggungan['banyak']  & prestasi['tinggi'], kelayakan['layak']),
        ctrl.Rule(ipk['tinggi'] & penghasilan['sedang'] & tanggungan['banyak']  & prestasi['sedang'], kelayakan['layak']),
        ctrl.Rule(ipk['tinggi'] & penghasilan['sedang'] & tanggungan['banyak']  & prestasi['rendah'], kelayakan['cukup_layak']),
        ctrl.Rule(ipk['tinggi'] & penghasilan['sedang'] & tanggungan['sedang']  & prestasi['tinggi'], kelayakan['cukup_layak']),
        ctrl.Rule(ipk['tinggi'] & penghasilan['sedang'] & tanggungan['sedang']  & prestasi['sedang'], kelayakan['cukup_layak']),
        ctrl.Rule(ipk['tinggi'] & penghasilan['sedang'] & tanggungan['sedang']  & prestasi['rendah'], kelayakan['kurang_layak']),
        ctrl.Rule(ipk['tinggi'] & penghasilan['sedang'] & tanggungan['sedikit'] & prestasi['tinggi'], kelayakan['cukup_layak']),
        ctrl.Rule(ipk['tinggi'] & penghasilan['sedang'] & tanggungan['sedikit'] & prestasi['sedang'], kelayakan['kurang_layak']),
        ctrl.Rule(ipk['tinggi'] & penghasilan['sedang'] & tanggungan['sedikit'] & prestasi['rendah'], kelayakan['kurang_layak']),
        ctrl.Rule(ipk['tinggi'] & penghasilan['tinggi'] & tanggungan['banyak']  & prestasi['tinggi'], kelayakan['cukup_layak']),
        ctrl.Rule(ipk['tinggi'] & penghasilan['tinggi'] & tanggungan['banyak']  & prestasi['sedang'], kelayakan['kurang_layak']),
        ctrl.Rule(ipk['tinggi'] & penghasilan['tinggi'] & tanggungan['banyak']  & prestasi['rendah'], kelayakan['kurang_layak']),
        ctrl.Rule(ipk['tinggi'] & penghasilan['tinggi'] & tanggungan['sedang']  & prestasi['tinggi'], kelayakan['kurang_layak']),
        ctrl.Rule(ipk['tinggi'] & penghasilan['tinggi'] & tanggungan['sedang']  & prestasi['sedang'], kelayakan['tidak_layak']),
        ctrl.Rule(ipk['tinggi'] & penghasilan['tinggi'] & tanggungan['sedang']  & prestasi['rendah'], kelayakan['tidak_layak']),
        ctrl.Rule(ipk['tinggi'] & penghasilan['tinggi'] & tanggungan['sedikit'] & prestasi['tinggi'], kelayakan['kurang_layak']),
        ctrl.Rule(ipk['tinggi'] & penghasilan['tinggi'] & tanggungan['sedikit'] & prestasi['sedang'], kelayakan['tidak_layak']),
        ctrl.Rule(ipk['tinggi'] & penghasilan['tinggi'] & tanggungan['sedikit'] & prestasi['rendah'], kelayakan['tidak_layak']),
        # === IPK SEDANG ===
        ctrl.Rule(ipk['sedang'] & penghasilan['rendah'] & tanggungan['banyak']  & prestasi['tinggi'], kelayakan['layak']),
        ctrl.Rule(ipk['sedang'] & penghasilan['rendah'] & tanggungan['banyak']  & prestasi['sedang'], kelayakan['cukup_layak']),
        ctrl.Rule(ipk['sedang'] & penghasilan['rendah'] & tanggungan['banyak']  & prestasi['rendah'], kelayakan['cukup_layak']),
        ctrl.Rule(ipk['sedang'] & penghasilan['rendah'] & tanggungan['sedang']  & prestasi['tinggi'], kelayakan['cukup_layak']),
        ctrl.Rule(ipk['sedang'] & penghasilan['rendah'] & tanggungan['sedang']  & prestasi['sedang'], kelayakan['cukup_layak']),
        ctrl.Rule(ipk['sedang'] & penghasilan['rendah'] & tanggungan['sedang']  & prestasi['rendah'], kelayakan['kurang_layak']),
        ctrl.Rule(ipk['sedang'] & penghasilan['rendah'] & tanggungan['sedikit'] & prestasi['tinggi'], kelayakan['cukup_layak']),
        ctrl.Rule(ipk['sedang'] & penghasilan['rendah'] & tanggungan['sedikit'] & prestasi['sedang'], kelayakan['kurang_layak']),
        ctrl.Rule(ipk['sedang'] & penghasilan['rendah'] & tanggungan['sedikit'] & prestasi['rendah'], kelayakan['kurang_layak']),
        ctrl.Rule(ipk['sedang'] & penghasilan['sedang'] & tanggungan['banyak']  & prestasi['tinggi'], kelayakan['cukup_layak']),
        ctrl.Rule(ipk['sedang'] & penghasilan['sedang'] & tanggungan['banyak']  & prestasi['sedang'], kelayakan['kurang_layak']),
        ctrl.Rule(ipk['sedang'] & penghasilan['sedang'] & tanggungan['banyak']  & prestasi['rendah'], kelayakan['kurang_layak']),
        ctrl.Rule(ipk['sedang'] & penghasilan['sedang'] & tanggungan['sedang']  & prestasi['tinggi'], kelayakan['kurang_layak']),
        ctrl.Rule(ipk['sedang'] & penghasilan['sedang'] & tanggungan['sedang']  & prestasi['sedang'], kelayakan['tidak_layak']),
        ctrl.Rule(ipk['sedang'] & penghasilan['sedang'] & tanggungan['sedang']  & prestasi['rendah'], kelayakan['tidak_layak']),
        ctrl.Rule(ipk['sedang'] & penghasilan['sedang'] & tanggungan['sedikit'] & prestasi['tinggi'], kelayakan['kurang_layak']),
        ctrl.Rule(ipk['sedang'] & penghasilan['sedang'] & tanggungan['sedikit'] & prestasi['sedang'], kelayakan['tidak_layak']),
        ctrl.Rule(ipk['sedang'] & penghasilan['sedang'] & tanggungan['sedikit'] & prestasi['rendah'], kelayakan['tidak_layak']),
        ctrl.Rule(ipk['sedang'] & penghasilan['tinggi'] & tanggungan['banyak']  & prestasi['tinggi'], kelayakan['kurang_layak']),
        ctrl.Rule(ipk['sedang'] & penghasilan['tinggi'] & tanggungan['banyak']  & prestasi['sedang'], kelayakan['tidak_layak']),
        ctrl.Rule(ipk['sedang'] & penghasilan['tinggi'] & tanggungan['banyak']  & prestasi['rendah'], kelayakan['tidak_layak']),
        ctrl.Rule(ipk['sedang'] & penghasilan['tinggi'] & tanggungan['sedang']  & prestasi['tinggi'], kelayakan['tidak_layak']),
        ctrl.Rule(ipk['sedang'] & penghasilan['tinggi'] & tanggungan['sedang']  & prestasi['sedang'], kelayakan['tidak_layak']),
        ctrl.Rule(ipk['sedang'] & penghasilan['tinggi'] & tanggungan['sedang']  & prestasi['rendah'], kelayakan['tidak_layak']),
        ctrl.Rule(ipk['sedang'] & penghasilan['tinggi'] & tanggungan['sedikit'] & prestasi['tinggi'], kelayakan['tidak_layak']),
        ctrl.Rule(ipk['sedang'] & penghasilan['tinggi'] & tanggungan['sedikit'] & prestasi['sedang'], kelayakan['tidak_layak']),
        ctrl.Rule(ipk['sedang'] & penghasilan['tinggi'] & tanggungan['sedikit'] & prestasi['rendah'], kelayakan['tidak_layak']),
        # === IPK RENDAH ===
        ctrl.Rule(ipk['rendah'] & penghasilan['rendah'] & tanggungan['banyak']  & prestasi['tinggi'], kelayakan['cukup_layak']),
        ctrl.Rule(ipk['rendah'] & penghasilan['rendah'] & tanggungan['banyak']  & prestasi['sedang'], kelayakan['kurang_layak']),
        ctrl.Rule(ipk['rendah'] & penghasilan['rendah'] & tanggungan['banyak']  & prestasi['rendah'], kelayakan['kurang_layak']),
        ctrl.Rule(ipk['rendah'] & penghasilan['rendah'] & tanggungan['sedang']  & prestasi['tinggi'], kelayakan['kurang_layak']),
        ctrl.Rule(ipk['rendah'] & penghasilan['rendah'] & tanggungan['sedang']  & prestasi['sedang'], kelayakan['tidak_layak']),
        ctrl.Rule(ipk['rendah'] & penghasilan['rendah'] & tanggungan['sedang']  & prestasi['rendah'], kelayakan['tidak_layak']),
        ctrl.Rule(ipk['rendah'] & penghasilan['rendah'] & tanggungan['sedikit'] & prestasi['tinggi'], kelayakan['kurang_layak']),
        ctrl.Rule(ipk['rendah'] & penghasilan['rendah'] & tanggungan['sedikit'] & prestasi['sedang'], kelayakan['tidak_layak']),
        ctrl.Rule(ipk['rendah'] & penghasilan['rendah'] & tanggungan['sedikit'] & prestasi['rendah'], kelayakan['tidak_layak']),
        ctrl.Rule(ipk['rendah'] & penghasilan['sedang'] & tanggungan['banyak']  & prestasi['tinggi'], kelayakan['kurang_layak']),
        ctrl.Rule(ipk['rendah'] & penghasilan['sedang'] & tanggungan['banyak']  & prestasi['sedang'], kelayakan['tidak_layak']),
        ctrl.Rule(ipk['rendah'] & penghasilan['sedang'] & tanggungan['banyak']  & prestasi['rendah'], kelayakan['tidak_layak']),
        ctrl.Rule(ipk['rendah'] & penghasilan['sedang'] & tanggungan['sedang']  & prestasi['tinggi'], kelayakan['tidak_layak']),
        ctrl.Rule(ipk['rendah'] & penghasilan['sedang'] & tanggungan['sedang']  & prestasi['sedang'], kelayakan['tidak_layak']),
        ctrl.Rule(ipk['rendah'] & penghasilan['sedang'] & tanggungan['sedang']  & prestasi['rendah'], kelayakan['tidak_layak']),
        ctrl.Rule(ipk['rendah'] & penghasilan['sedang'] & tanggungan['sedikit'] & prestasi['tinggi'], kelayakan['tidak_layak']),
        ctrl.Rule(ipk['rendah'] & penghasilan['sedang'] & tanggungan['sedikit'] & prestasi['sedang'], kelayakan['tidak_layak']),
        ctrl.Rule(ipk['rendah'] & penghasilan['sedang'] & tanggungan['sedikit'] & prestasi['rendah'], kelayakan['tidak_layak']),
        ctrl.Rule(ipk['rendah'] & penghasilan['tinggi'] & tanggungan['banyak']  & prestasi['tinggi'], kelayakan['tidak_layak']),
        ctrl.Rule(ipk['rendah'] & penghasilan['tinggi'] & tanggungan['banyak']  & prestasi['sedang'], kelayakan['tidak_layak']),
        ctrl.Rule(ipk['rendah'] & penghasilan['tinggi'] & tanggungan['banyak']  & prestasi['rendah'], kelayakan['tidak_layak']),
        ctrl.Rule(ipk['rendah'] & penghasilan['tinggi'] & tanggungan['sedang']  & prestasi['tinggi'], kelayakan['tidak_layak']),
        ctrl.Rule(ipk['rendah'] & penghasilan['tinggi'] & tanggungan['sedang']  & prestasi['sedang'], kelayakan['tidak_layak']),
        ctrl.Rule(ipk['rendah'] & penghasilan['tinggi'] & tanggungan['sedang']  & prestasi['rendah'], kelayakan['tidak_layak']),
        ctrl.Rule(ipk['rendah'] & penghasilan['tinggi'] & tanggungan['sedikit'] & prestasi['tinggi'], kelayakan['tidak_layak']),
        ctrl.Rule(ipk['rendah'] & penghasilan['tinggi'] & tanggungan['sedikit'] & prestasi['sedang'], kelayakan['tidak_layak']),
        ctrl.Rule(ipk['rendah'] & penghasilan['tinggi'] & tanggungan['sedikit'] & prestasi['rendah'], kelayakan['tidak_layak']),
    ]
    engine = ctrl.ControlSystem(rules)
    return ctrl.ControlSystemSimulation(engine)


def hitung_kelayakan(ipk_val, penghasilan_val, tanggungan_val, prestasi_list=None):
    if prestasi_list is None:
        prestasi_list = []
    skor_prestasi = hitung_skor_prestasi(prestasi_list)
    pgh_norm = normalisasi_penghasilan(penghasilan_val)
    tg_norm  = normalisasi_tanggungan(tanggungan_val)

    system = build_fuzzy_system()
    system.input['ipk']         = float(ipk_val)
    system.input['penghasilan'] = float(pgh_norm)
    system.input['tanggungan']  = float(tg_norm)
    system.input['prestasi']    = float(skor_prestasi)
    system.compute()
    skor = round(system.output['kelayakan'], 2)

    if skor >= 82:
        kategori, warna = "Sangat Layak", "#10b981"
    elif skor >= 60:
        kategori, warna = "Layak", "#34d399"
    elif skor >= 35:
        kategori, warna = "Cukup Layak", "#fbbf24"
    elif skor >= 10:
        kategori, warna = "Kurang Layak", "#f97316"
    else:
        kategori, warna = "Tidak Layak", "#f87171"

    return {"skor": skor, "kategori": kategori, "warna": warna, "skor_prestasi": skor_prestasi}


if __name__ == "__main__":
    cases = [
        (3.78, 1_000_000, 2, [], 'IPK 3.78 | Pgh 1jt | Tg 2 | No Prestasi'),
        (3.78, 1_000_000, 2, [{'nama':'Olimpiade','tingkat':'nasional','juara':1}], 'IPK 3.78 | Pgh 1jt | Tg 2 | Nasional J1'),
        (3.90, 800_000,   7, [{'nama':'Intl','tingkat':'internasional','juara':1}], 'IPK 3.90 | Pgh 800rb | Tg 7 | Intl J1'),
        (2.50, 3_000_000, 3, [], 'IPK 2.50 | Pgh 3jt | Tg 3'),
        (1.80, 8_000_000, 1, [], 'IPK 1.80 | Pgh 8jt | Tg 1'),
        (3.78, 5_000_000, 2, [], 'IPK 3.78 | Pgh 5jt | Tg 2'),
        (2.00, 500_000,  12, [], 'IPK 2.00 | Pgh 500rb | Tg 12'),
    ]
    print(f"{'Kasus':<45} {'Skor':>6}  Kategori")
    print('-'*65)
    for ipk, pgh, tg, pr, label in cases:
        r = hitung_kelayakan(ipk, pgh, tg, pr)
        print(f"{label:<45} {r['skor']:>6}  {r['kategori']}")