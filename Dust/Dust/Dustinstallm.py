
from pathlib import Path
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import requests
import zipfile
from tqdm import tqdm

# ==========================================
# NASA MOON DATA DOWNLOADER
# LDEX + DIVINER
# ==========================================

ROOT = Path("Moon_Data")
ROOT.mkdir(exist_ok=True)

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "MoonEarthResearch/1.0"
})

# ------------------------------------------
# 1. LDEX - ACTUAL LUNAR DUST MEASUREMENTS
# ------------------------------------------

LDEX_URL = (
    "https://sbnarchive.psi.edu/pds4/ldex/"
    "ladee_ldex_20240411.zip"
)

def download_file(url, destination):

    destination = Path(destination)
    destination.parent.mkdir(
        parents=True, exist_ok=True
    )

    if destination.exists():
        print("Already downloaded:", destination)
        return destination

    print("\nDownloading:", url)

    with SESSION.get(
        url, stream=True, timeout=60
    ) as response:

        response.raise_for_status()

        total = int(
            response.headers.get(
                "content-length", 0
            )
        )

        with open(destination, "wb") as file:
            with tqdm(
                total=total,
                unit="B",
                unit_scale=True,
                desc=destination.name
            ) as progress:

                for chunk in response.iter_content(
                    chunk_size=1024 * 1024
                ):
                    if chunk:
                        file.write(chunk)
                        progress.update(len(chunk))

    return destination


def download_ldex():

    print("\n========== LDEX ==========")

    folder = ROOT / "LDEX"
    archive = folder / "ladee_ldex.zip"

    download_file(LDEX_URL, archive)

    print("Extracting LDEX archive...")

    with zipfile.ZipFile(archive, "r") as z:
        z.extractall(folder / "extracted")

    print("LDEX completed!")


# ------------------------------------------
# 2. DIVINER - LUNAR THERMAL DATA
# ------------------------------------------

DIVINER_ROOT = (
    "https://pds-geosciences.wustl.edu/lro/"
    "urn-nasa-pds-lro_diviner_derived1/"
)

GDR_ROOT = (
    DIVINER_ROOT + "data_derived_gdr_l2/"
)

MAX_DATA_FILES = 20
downloaded = 0
visited = set()


def crawl_diviner(url, destination):

    global downloaded

    if downloaded >= MAX_DATA_FILES:
        return

    if url in visited:
        return

    visited.add(url)

    try:
        response = SESSION.get(
            url, timeout=60
        )
        response.raise_for_status()

        soup = BeautifulSoup(
            response.text, "html.parser"
        )

        links = []

        for a in soup.find_all("a"):
            href = a.get("href")

            if href:
                links.append(urljoin(url, href))

        # Visit subdirectories
        for link in links:

            if downloaded >= MAX_DATA_FILES:
                break

            parsed = urlparse(link)

            if parsed.netloc != urlparse(url).netloc:
                continue

            if not link.startswith(url):
                continue

            if link.endswith("/"):
                name = link.rstrip("/").split("/")[-1]

                if name == "..":
                    continue

                crawl_diviner(
                    link,
                    destination / name
                )

        # Download selected PDS data products
        for link in links:

            if downloaded >= MAX_DATA_FILES:
                break

            name = urlparse(link).path.split("/")[-1]

            if not name:
                continue

            if name.lower().endswith(
                (".tab", ".img", ".csv", ".lbl")
            ):

                target = destination / name

                if target.exists():
                    continue

                try:
                    download_file(link, target)
                    downloaded += 1

                except Exception as error:
                    print("File error:", error)

    except Exception as error:
        print("Directory error:", url, error)


def download_diviner():

    print("\n========== DIVINER ==========")

    folder = ROOT / "Diviner_GDR_L2"
    folder.mkdir(exist_ok=True)

    # Download the product inventory
    inventory = (
        GDR_ROOT +
        "collection_data_derived_gdr_level2_inventory.csv"
    )

    try:
        download_file(
            inventory,
            folder / "inventory.csv"
        )
    except Exception as error:
        print("Inventory error:", error)

    # Download a limited sample of data products
    print("\nDownloading selected GDR Level 2 files...")

    for year in range(2009, 2017):

        if downloaded >= MAX_DATA_FILES:
            break

        year_url = GDR_ROOT + str(year) + "/"

        crawl_diviner(
            year_url,
            folder / str(year)
        )

    print("Diviner files downloaded:", downloaded)


# ------------------------------------------
# 3. RUN DOWNLOADS
# ------------------------------------------

if __name__ == "__main__":

    print("NASA LUNAR DATA DOWNLOAD")
    print("========================")

    try:
        download_ldex()
    except Exception as error:
        print("LDEX failed:", error)

    try:
        download_diviner()
    except Exception as error:
        print("Diviner failed:", error)

    print("\nDOWNLOAD FINISHED")
    print("Data location:", ROOT.resolve())
