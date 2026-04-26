"""
app.py
Lokasi: scholarcheck/app.py

Entry point Flask untuk ScholarCheck.
Jalankan: python app.py  →  http://localhost:5000
"""

from flask import Flask, render_template, request, jsonify
from fuzzy_engine import hitung_kelayakan

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/hitung", methods=["POST"])
def hitung():
    """
    POST JSON:
        ipk          : float  (0.00 – 4.00)
        penghasilan  : float  (tanpa batas, normalisasi otomatis)
        tanggungan   : int    (tanpa batas, normalisasi otomatis)
        prestasi     : list   (OPSIONAL, [] jika tidak ada)
                       [{ nama: str, tingkat: str, juara: int|str }, ...]

    Response JSON:
        skor, kategori, warna, skor_prestasi  |  error
    """
    try:
        data = request.get_json()

        ipk_val         = float(data.get("ipk", 0))
        penghasilan_val = float(data.get("penghasilan", 0))
        tanggungan_val  = int(data.get("tanggungan", 0))
        prestasi_list   = data.get("prestasi", [])

        # Validasi wajib
        if not (0.00 <= ipk_val <= 4.00):
            return jsonify({"error": "IPK harus antara 0.00 hingga 4.00"}), 400
        if penghasilan_val < 0:
            return jsonify({"error": "Penghasilan tidak boleh negatif"}), 400
        if tanggungan_val < 0:
            return jsonify({"error": "Jumlah tanggungan tidak boleh negatif"}), 400

        # Validasi prestasi (opsional, maks 3)
        if not isinstance(prestasi_list, list):
            prestasi_list = []
        prestasi_list = prestasi_list[:3]

        hasil = hitung_kelayakan(ipk_val, penghasilan_val, tanggungan_val, prestasi_list)
        return jsonify(hasil)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)