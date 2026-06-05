"""
Zero-dependency lookup for the UK Wind Rose Atlas.

Given a lat/lon, finds the nearest weather station and provides access
to its wind rose images hosted on GitHub.

Usage:
    from windrose_lookup import WindRoseAtlas

    atlas = WindRoseAtlas(repo="monsieurpablo/uk-wind-roses")

    # Look up nearest station
    result = atlas.get_images(lat=51.5074, lon=-0.1278)
    print(result["station"]["name"])   # "HEATHROW"
    print(result["distance_km"])       # 5.2
    print(result["images"]["annual"])  # "images/03772_annual.jpg"

    # Download all 5 seasonal images
    atlas.download_images(lat=51.5074, lon=-0.1278, target_dir="./my_site/")
"""
import json
import math
import os
import sys
import urllib.request


def _default_cache_dir():
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
        return os.path.join(base, "windrose-atlas")
    elif sys.platform == "darwin":
        return os.path.expanduser("~/Library/Caches/windrose-atlas")
    else:
        return os.path.expanduser("~/.cache/windrose-atlas")


CACHE_DIR = _default_cache_dir()


class WindRoseAtlas:
    def __init__(self, repo, branch="main", verbose=True):
        self.repo = repo
        self.branch = branch
        self.verbose = verbose
        self._stations = None
        self._base_url = f"https://raw.githubusercontent.com/{repo}/{branch}"

    def _log(self, msg):
        if self.verbose:
            print(msg)

    def _load_index(self):
        if self._stations is not None:
            return

        cache_path = os.path.join(CACHE_DIR, "stations.json")

        if os.path.exists(cache_path):
            with open(cache_path) as f:
                self._stations = json.load(f)
            return

        url = f"{self._base_url}/stations.json"
        os.makedirs(CACHE_DIR, exist_ok=True)
        self._log(f"Fetching {url} ...")
        urllib.request.urlretrieve(url, cache_path)

        with open(cache_path) as f:
            self._stations = json.load(f)

    @staticmethod
    def _haversine_km(lat1, lon1, lat2, lon2):
        R = 6371
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(
            math.radians(lat2)
        ) * math.sin(dlon / 2) ** 2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    def get_images(self, lat, lon):
        """Return the nearest station's metadata, distance, and image paths."""
        self._load_index()

        best = None
        best_dist = float("inf")

        for s in self._stations:
            d = self._haversine_km(lat, lon, s["lat"], s["lon"])
            if d < best_dist:
                best_dist = d
                best = s

        return {
            "station": {
                "src_id": best["src_id"],
                "name": best["name"],
                "county": best["county"],
                "lat": best["lat"],
                "lon": best["lon"],
                "elevation_m": best["elevation_m"],
                "first_year": best["first_year"],
                "last_year": best["last_year"],
                "n_years_valid": best["n_years_valid"],
                "stats": best["stats"],
            },
            "distance_km": round(best_dist, 1),
            "images": best["images"],
            "image_urls": {
                season: f"{self._base_url}/{path}"
                for season, path in best["images"].items()
            },
        }

    def download_images(self, lat, lon, target_dir):
        """Download all seasonal wind rose images for the nearest station."""
        result = self.get_images(lat, lon)
        os.makedirs(target_dir, exist_ok=True)

        downloaded = []
        for season, url in result["image_urls"].items():
            filename = os.path.basename(url)
            dest = os.path.join(target_dir, filename)
            self._log(f"Downloading {url} ...")
            urllib.request.urlretrieve(url, dest)
            downloaded.append(dest)

        return {
            "station": result["station"],
            "distance_km": result["distance_km"],
            "downloaded": downloaded,
        }
