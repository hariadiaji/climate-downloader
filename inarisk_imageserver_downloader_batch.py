# code ini akan mengunduh citra dari BNPB ImageServer untuk wilayah Indonesia, membaginya menjadi beberapa tile, dan menyimpannya sebagai file TIFF.

# Pastikan untuk menginstall library requests dan GDAL sebelum menjalankan kode ini.
# di dalam list image_service_urls, tambahkan URL ImageServer yang ingin diunduh.
# copy url dari website imageserver nya bnpb, dan paste di variabel image_service_url.
# bisa digunakan untuk mengunduh berbagai layer seperti INDEKS_BAHAYA_BANJIRBANDANG, INDEKS_KERENTANAN_TANAH_LONGSOR, dll.

#hariadi aji jj

import requests
from pathlib import Path
from urllib.parse import urljoin, urlparse
from osgeo import gdal

# === 1. Daftar URL InaRISK TANPA /exportImage ===
image_service_urls = [
    "https://gis.bnpb.go.id/server/rest/services/inarisk/INDEKS_BAHAYA_BANJIR/ImageServer",
    "https://gis.bnpb.go.id/server/rest/services/inarisk/INDEKS_BAHAYA_TANAHLONGSOR/ImageServer",
    "https://gis.bnpb.go.id/server/rest/services/inarisk/layer_bahaya_banjir/ImageServer",
    "https://gis.bnpb.go.id/server/rest/services/inarisk/layer_bahaya_tanah_longsor/ImageServer"
]

# === 2. Tile Konfigurasi ===
xmin, ymin, xmax, ymax = 94.0, -11.0, 141.0, 6.0  # bounding box Indonesia
tile_width = 5.0
tile_height = 5.0
tile_size = "1500,1500"  # pixels per tile

# === 3. Proses Setiap URL ===
for base_url in image_service_urls:
    export_url = urljoin(base_url + "/", "exportImage")

    # Tentukan nama folder dari path setelah /inarisk/
    parsed = urlparse(base_url)
    try:
        layer_name = parsed.path.split("/")[parsed.path.split("/").index("inarisk") + 1]
    except (ValueError, IndexError):
        print(f"❌ URL tidak valid (tidak mengandung '/inarisk/'): {base_url}")
        continue

    output_folder = Path.cwd() / layer_name
    output_folder.mkdir(parents=True, exist_ok=True)

    print(f"\n📥 Memproses: {layer_name}")
    tile_id = 0
    tile_paths = []

    for x in range(int((xmax - xmin) / tile_width) + 1):
        for y in range(int((ymax - ymin) / tile_height) + 1):
            tile_xmin = xmin + x * tile_width
            tile_xmax = min(tile_xmin + tile_width, xmax)
            tile_ymin = ymin + y * tile_height
            tile_ymax = min(tile_ymin + tile_height, ymax)

            params = {
                "bbox": f"{tile_xmin},{tile_ymin},{tile_xmax},{tile_ymax}",
                "bboxSR": "4326",
                "size": tile_size,
                "format": "tiff",
                "f": "json"
            }

            try:
                r = requests.get(export_url, params=params, timeout=60)
                data = r.json()

                if "href" in data:
                    href = data["href"]
                    tile_path = output_folder / f"tile_{tile_id}.tif"
                    r2 = requests.get(href, stream=True)
                    with open(tile_path, "wb") as f:
                        for chunk in r2.iter_content(1024):
                            f.write(chunk)
                    print(f"  ✅ Tile {tile_id} disimpan")
                    tile_paths.append(str(tile_path))
                    tile_id += 1
                else:
                    print(f"  ⚠️  Tidak ada 'href' pada tile {tile_id}")
            except Exception as e:
                print(f"  ❌ Gagal tile {tile_id} karena: {e}")

    # === 4. Gabungkan semua tile menjadi satu GeoTIFF ===
    if tile_paths:
        vrt_path = output_folder / "tiles.vrt"
        tif_path = output_folder / f"{layer_name}_merged.tif"
        gdal.BuildVRT(str(vrt_path), tile_paths)
        gdal.Translate(str(tif_path), str(vrt_path), format="GTiff")
        print(f"🧩 Merged TIFF disimpan: {tif_path}")
    else:
        print(f"⚠️  Tidak ada tile yang berhasil untuk {layer_name}")

print("\n🚀 Semua proses selesai.")
