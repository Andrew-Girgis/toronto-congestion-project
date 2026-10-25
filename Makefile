# Congestion Cordon pipeline. Each target is reproducible from public data.
PY := uv run python
SUMO_HOME := $(shell .venv/bin/python -c "import sumo;print(sumo.SUMO_HOME)")
export SUMO_HOME
export PATH := $(CURDIR)/.venv/bin:$(PATH)

.PHONY: all data geometry coverage network demand assign sim model web check serve present present-check present-pdf

all: data geometry coverage network demand assign model web

data:            ## dated snapshots of City open data + manifest
	$(PY) -m cordon.ingest
	$(PY) -m cordon.ingest.nyc

geometry:        ## candidate boundaries and their road crossings
	$(PY) -m cordon.geometry.cordons

coverage:        ## City count coverage at each crossing
	$(PY) -m cordon.observed.coverage

network:         ## OSM extract -> SUMO network
	$(PY) -m cordon.network.osm
	netconvert --osm-files $$(ls data/raw/osm/*/study_area.osm.xml | tail -1) \
	  --output-file sim/net/study_area.net.xml.gz --geometry.remove --ramps.guess \
	  --junctions.join --tls.guess-signals --tls.discard-simple --tls.join --roundabouts.guess \
	  --remove-edges.isolated --keep-edges.by-vclass passenger --osm.oneway-spread-right \
	  --output.street-names --output.original-names --proj.utm --no-turnarounds.except-deadend

demand:          ## counts -> calibration targets -> calibrated baseline routes
	$(PY) -m cordon.demand.turncounts
	$(PY) $(SUMO_HOME)/tools/randomTrips.py -n sim/net/study_area.net.xml.gz \
	  -o sim/demand/candidates.trips.xml -r sim/demand/candidates.rou.xml -b 0 -e 3600 -p 0.04 \
	  --fringe-factor 20 --min-distance 400 --validate --remove-loops --seed 42 --vehicle-class passenger
	$(PY) $(SUMO_HOME)/tools/routeSampler.py -r sim/demand/candidates.rou.xml \
	  -t sim/demand/turns_calibration.xml -d sim/demand/edges_calibration.xml \
	  -o sim/demand/baseline.rou.xml --mismatch-output sim/demand/mismatch_calibration.xml \
	  --seed 42 --attributes 'type="car"'

assign:          ## S0-S3 street-level results (static equilibrium assignment; used by the demo)
	$(PY) -m cordon.assign

sim:             ## S0-S3 in SUMO mesoscopic (experimental: deadlocks on this network, see docs)
	$(PY) -m cordon.sim.scenarios S0 S1 S2 S3

model:           ## behavioural ranges + 10-year finance
	$(PY) -m cordon.finance.cashflow

web:             ## export web layers and metrics
	$(PY) -m cordon.export.web
	$(PY) -m cordon.export.nyc
	$(PY) -m cordon.export.figures
	$(PY) -m cordon.export.references

serve:           ## run the demo locally
	cd web && npm install && npx astro dev

check:           ## data and model sanity tests
	$(PY) -m pytest -q tests

present:         ## export deck figures and build the site (deck at /present)
	$(PY) -m cordon.export.figures
	$(PY) -m cordon.export.references
	cd web && npx astro build

present-check: present  ## deck numbers match figures.json; slides render at 1920x1080 and 1280x720
	$(PY) scripts/present/check_figures.py
	$(PY) scripts/present/render_check.py

present-pdf:     ## PDF backup of the deck (needs the dev server: make serve)
	$(PY) scripts/present/export_pdf.py
