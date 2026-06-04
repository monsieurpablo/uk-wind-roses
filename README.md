# UK Wind Rose Atlas

Wind rose images for 311 UK weather stations (MIDAS Open dataset), with nearest-neighbor lookup by latitude/longitude.

Each station has 5 seasonal wind roses: **annual**, **spring**, **summer**, **autumn**, **winter**.

## Quick Start

```python
from windrose_lookup import WindRoseAtlas

atlas = WindRoseAtlas(repo="monsieurpablo/uk-wind-roses")

# Find the nearest weather station to a site
result = atlas.get_images(lat=51.5074, lon=-0.1278)
print(result["station"]["name"])  # e.g. "HEATHROW"
print(result["distance_km"])      # distance from query point
print(result["images"])           # dict of season -> relative path

# Download wind rose images for the nearest station
atlas.download_images(lat=51.5074, lon=-0.1278, target_dir="./my_site/")
```

## Repository Structure

```
uk-wind-roses/
├── images/                # 1555 wind rose JPGs (311 stations × 5 seasons)
├── stations.json          # Station metadata, statistics, and image paths
├── windrose_lookup.py     # Zero-dependency lookup module
└── README.md
```

## Image Format

- Square JPG, 800×800 pixels
- 8 wind direction sectors
- 0–12 m/s range, 2 m/s speed bins
- Viridis colormap
- No legend or title on the wind rose itself
- Standalone legend available at `images/legend.jpg`

## Station Index (`stations.json`)

Each station entry includes:

| Field | Description |
|-------|-------------|
| `src_id` | MIDAS source ID |
| `name` | Station name |
| `county` | Historic county |
| `lat`, `lon` | Coordinates |
| `elevation_m` | Elevation in metres |
| `first_year`, `last_year` | Data period |
| `n_years_valid` | Years of valid data |
| `stats.mean_wind_speed_ms` | Annual mean wind speed |
| `stats.prevailing_direction_deg` | Predominant wind direction |
| `stats.calm_pct` | Percentage of calm conditions (<1 m/s) |
| `stats.seasonal` | Seasonal breakdown of the above |
| `images` | Relative paths to the 5 seasonal JPGs |

## Data Source

[MIDAS Open](https://archive.ceda.ac.uk/) UK mean wind observations, station metadata processed by Hoare Lea.
