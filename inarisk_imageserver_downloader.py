import requests
import os
from osgeo import gdal

# Set the output directory
output_dir = "D:/temporari/inarisk/INDEKS_BAHAYA_BANJRBANDANG"
os.makedirs(output_dir, exist_ok=True)

# BNPB ImageServer URL
# ditambahkan /exportImage setelah website imageserver nya
#image_service_url = "https://gis.bnpb.go.id/server/rest/services/inarisk/layer_bahaya_tanah_longsor/ImageServer/exportImage"
#image_service_url = "https://gis.bnpb.go.id/server/rest/services/inarisk/layer_risiko_tanah_longsor/ImageServer/exportImage"
#image_service_url = "https://gis.bnpb.go.id/server/rest/services/inarisk/layer_kerentanan_tanah_longsor/ImageServer/exportImage"
#image_service_url = "https://gis.bnpb.go.id/server/rest/services/inarisk/INDEKS_KERENTANAN_TANAH_LONGSOR/ImageServer/exportImage"
#image_service_url = "https://gis.bnpb.go.id/server/rest/services/inarisk/INDEKS_BAHAYA_TANAHLONGSOR/ImageServer/exportImage"
#image_service_url = "https://gis.bnpb.go.id/server/rest/services/inarisk/INDEKS_BAHAYA_BANJIRBANDANG/ImageServer/exportImage"
image_service_url = "https://gis.bnpb.go.id/server/rest/services/inarisk/INDEKS_BAHAYA_BANJIR/ImageServer/exportImage"



# Define the coordinate extent for Indonesia (Modify if needed)
xmin, ymin, xmax, ymax = 94.0, -11.0, 141.0, 6.0  # Indonesia's rough bounding box

# Define tile size (adjust based on server limits)
tile_width = 5.0  # Degrees of longitude
tile_height = 5.0  # Degrees of latitude

# Loop through tiles
tile_id = 0
for x in range(int((xmax - xmin) / tile_width) + 1):
    for y in range(int((ymax - ymin) / tile_height) + 1):
        tile_xmin = xmin + x * tile_width
        tile_xmax = min(tile_xmin + tile_width, xmax)
        tile_ymin = ymin + y * tile_height
        tile_ymax = min(tile_ymin + tile_height, ymax)

        # Define parameters for export request
        params = {
            "bbox": f"{tile_xmin},{tile_ymin},{tile_xmax},{tile_ymax}",
            "bboxSR": "4326",  # WGS 84
            "size": "1500,1500",  # Max rows and cols per tile
            "format": "tiff",  # Output format
            "f": "json"
        }

        # Send request
        response = requests.get(image_service_url, params=params)
        data = response.json()

        # Check for valid image URL
        if "href" in data:
            image_url = data["href"]
            image_path = os.path.join(output_dir, f"tile_{tile_id}.tif")

            # Download the image
            img_data = requests.get(image_url).content
            with open(image_path, "wb") as img_file:
                img_file.write(img_data)

            print(f"Downloaded: {image_path}")
            tile_id += 1
        else:
            print(f"Failed to download tile at {tile_xmin}, {tile_ymin}")

print("All tiles downloaded!")

# OPTIONAL: Merge all downloaded tiles
output_merged = os.path.join(output_dir, "merged_raster.tif")
vrt_path = os.path.join(output_dir, "tiles.vrt")

# Create a VRT (Virtual Raster)
gdal.BuildVRT(vrt_path, [os.path.join(output_dir, f"tile_{i}.tif") for i in range(tile_id)])

# Convert VRT to final merged GeoTIFF
gdal.Translate(output_merged, vrt_path, format="GTiff")

print(f"Merged raster saved as {output_merged}")
