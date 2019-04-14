#!/bin/bash

# ensure pipreqs is installed (will be fine if it is)
pip3.6 install pipreqs

# Get pip requirements
pipreqs --force ./

# install pip requirements in pwd
pip install -r requirements.txt --target .

# zip up folder contents and place them in ../
zip -r9 ../rs_tracker_lambda.zip .

# clean up
rm -rf */
rm six.py*
rm requirements.txt
