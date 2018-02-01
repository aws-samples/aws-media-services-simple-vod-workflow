#!/usr/bin/env bash
set -e

# Setup virtualenv
virtualenv mediaconvert

# Activate virtualenv
source mediaconvert/bin/activate

# Install dependencies
pip install -r requirements.txt
