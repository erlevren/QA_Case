#!/usr/bin/env bash
set -euo pipefail

echo "Running K6 REST..."
k6 run ../k6/rest/restcountries-smoke.js

echo "Running K6 GraphQL..."
k6 run ../k6/graphql/rickmorty-characters.js

echo "Running Playwright E2E (Python)..."

cd ../playwright-python 

python -m pip install -U pip
pip install -r requirements.txt
pip install pytest-html
python -m playwright install

python -m pytest -q --html=report.html --self-contained-html