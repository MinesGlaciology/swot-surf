#!/bin/bash
# Zachary Katz
# zachary_katz@mines.ed
# 22 May 2025

# Setup virtual environment on cryocloud

uv sync
source .venv/bin/activate
python -m ipykernel install --user --name swot-surf --display-name "(uv) swot-surf"
