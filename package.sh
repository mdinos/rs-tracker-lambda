#!/bin/bash

pipreqs --force ./
pip install -r requirements.txt --target .
zip -r9 ../rs_tracker_lambda.zip .
