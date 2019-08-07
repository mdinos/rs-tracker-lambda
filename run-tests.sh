#!/usr/bin/env bash

export username=woofythedog
export bucket=fake-bucket

pytest ./rs_tracker_lambda_tests.py

if [[ $? -eq 0 ]]; then 
  echo "SUCCESS"
else
  echo "FAILURE"
  exit 1
fi

if [ "$1" = "publish" ]; then
  echo "PUBLISHING"
  PWD=$(pwd)
  ${PWD}/package.sh
else
  echo "NOT PUBLISHING"
fi