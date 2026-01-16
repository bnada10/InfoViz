# Chess Player Rating Visualizations

This repo contains a D3-based visualization of FIDE rating data, plus a Python
pipeline to process the raw TSV files into the JSON that the visualization uses.

## Dependencies

- Python 3.9+ (for data processing and the local HTTP server)
- Python packages in `requirements.txt`:
  - `pandas`
  - `numpy`
- D3.js (already vendored at `vendor/d3-7.8.5/dist/d3.js`)

## Data Inputs

The visualization reads `viz/chess_data_aggregated.json`.

If you want to regenerate the JSON from raw TSV files, place these files in
`data/`:

- `data/players.tsv`
- `data/ratings.tsv`
- `data/countries.tsv`
- `data/iso3.tsv`

## Setup

```powershell
cd 2025-fide
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## Run the Visualization

Make sure you are inside `2025-fide` when running the command.

```powershell
python run_visualization.py
```

This starts a local server and opens your browser to:
`http://localhost:<PORT>/viz/chess_visualization.html`.

## Regenerate the Visualization Data (Optional)

If you have the raw TSV files and want to rebuild the JSON:

```powershell
python data_processor.py
```

This creates `chess_data.json` and `chess_data_aggregated.json` in the repo
root. The visualization expects the aggregated file at
`viz/chess_data_aggregated.json`, so either:

```powershell
copy chess_data_aggregated.json viz\chess_data_aggregated.json
```

or update the fetch path inside `viz/chess_visualization.html`.

## Troubleshooting

- If the page is blank, confirm `viz/chess_data_aggregated.json` exists and the
  server is running.
- If `run_visualization.py` cannot find a port, close other local servers or
  pick a free port in the script.
