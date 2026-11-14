
from pathlib import Path
import earthaccess
import json

# ==========================================
# MOON / EARTH DUST RESEARCH
# NASA EARTHDATA DOWNLOADER
# ==========================================

OUTPUT = Path("NASA_Earth_Data")
OUTPUT.mkdir(exist_ok=True)

# Initial test region: Sahara Desert
# West, South, East, North
SAHARA_BBOX = (-10, 15, 30, 32)

# Initial test period
START_DATE = "2023-01-01"
END_DATE = "2023-01-31"

MAX_GRANULES = 5

print("\nNASA EARTHDATA LOGIN")
print("Please authenticate using your Earthdata account.")

auth = earthaccess.login()

if not auth.authenticated:
    raise RuntimeError("Earthdata authentication failed.")

# Dataset configuration
DATASETS = [
    {
        "name": "MAIAC_AOD",
        "short_name": "MCD19A2",
        "version": "061",
    },
    {
        "name": "LAND_SURFACE_TEMPERATURE",
        "short_name": "MOD11A1",
        "version": "061",
    },
]

download_report = []

for dataset in DATASETS:

    print("\n================================")
    print("Dataset:", dataset["name"])
    print("================================")

    try:
        results = earthaccess.search_data(
            short_name=dataset["short_name"],
            version=dataset["version"],
            bounding_box=SAHARA_BBOX,
            temporal=(START_DATE, END_DATE),
            count=MAX_GRANULES
        )

        print("Granules found:", len(results))

        if not results:
            print("No granules found.")
            continue

        destination = OUTPUT / dataset["name"]
        destination.mkdir(exist_ok=True)

        files = earthaccess.download(
            results,
            local_path=str(destination)
        )

        print("Downloaded files:", len(files))

        download_report.append({
            "dataset": dataset["name"],
            "granules_found": len(results),
            "files_downloaded": len(files),
            "folder": str(destination)
        })

    except Exception as error:
        print("ERROR:", error)

# Save download report
with open(OUTPUT / "download_report.json", "w") as f:
    json.dump(download_report, f, indent=4)

print("\n================================")
print("DOWNLOAD PROCESS COMPLETED")
print("================================")

for item in download_report:
    print(item)

print("\nFiles are stored in:", OUTPUT.resolve())
