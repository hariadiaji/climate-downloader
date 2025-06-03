# code ini akan mengunduh citra dari BNPB ImageServer untuk wilayah Indonesia, membaginya menjadi beberapa tile, dan menyimpannya sebagai file TIFF.

# Pastikan untuk menginstall library requests dan GDAL sebelum menjalankan kode ini.
# di dalam list image_service_urls, tambahkan URL ImageServer yang ingin diunduh.
# copy url dari website imageserver nya bnpb, dan paste di variabel image_service_url.
# bisa digunakan untuk mengunduh berbagai layer seperti INDEKS_BAHAYA_BANJIRBANDANG, INDEKS_KERENTANAN_TANAH_LONGSOR, dll.

#hariadi aji jj

import requests
from pathlib import Path
from urllib.parse import urljoin, urlparse

# === 1. Daftar URL InaRISK ImageServer TANPA /exportImage ===
image_service_urls = [
    "https://gis.bnpb.go.id/server/rest/services/inarisk/INDEKS_BAHAYA_BANJIR/ImageServer",
    "https://gis.bnpb.go.id/server/rest/services/inarisk/INDEKS_BAHAYA_TANAHLONGSOR/ImageServer",
    "https://gis.bnpb.go.id/server/rest/services/inarisk/layer_bahaya_banjir/ImageServer",
    "https://gis.bnpb.go.id/server/rest/services/inarisk/layer_bahaya_tanah_longsor/ImageServer",
    # Tambahkan URL lain jika perlu
]

# === 2. Parameter untuk exportImage ===
export_params = {
    "bbox": "10576536,-1224895,15698236,673304",  # wilayah Indonesia
    "bboxSR": 3395,
    "size": "15000,4100",
    "imageSR": 3395,
    "format": "tiff",
    "f": "image"
}

# === 3. Proses setiap URL ===
for base_url in image_service_urls:
    # Pastikan URL akhir adalah /exportImage
    export_url = urljoin(base_url + "/", "exportImage")

    # Ambil nama layer setelah /inarisk/
    parsed = urlparse(base_url)
    try:
        layer_name = parsed.path.split("/")[parsed.path.split("/").index("inarisk") + 1]
    except (ValueError, IndexError):
        print(f"❌ URL tidak valid (tidak mengandung '/inarisk/'): {base_url}")
        continue

    # Buat folder output berdasarkan nama layer
    output_folder = Path.cwd() / layer_name
    output_folder.mkdir(parents=True, exist_ok=True)
    output_path = output_folder / f"{layer_name}.tif"

    # Unduh gambar
    print(f"📥 Mengunduh dari: {export_url}")
    try:
        response = requests.get(export_url, params=export_params, stream=True, timeout=60)
        response.raise_for_status()
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        print(f"✅ Berhasil disimpan ke: {output_path}\n")
    except Exception as e:
        print(f"❌ Gagal mengunduh dari {base_url} karena: {e}\n")

print("🚀 Semua proses selesai.")
