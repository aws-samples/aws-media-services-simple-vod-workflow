#!/bin/sh -v

# specific files we want in site-packages
#   lib/python2.7/site-packages/botocore/data/endpoints.json
#   lib/python2.7/site-packages/botocore/data/mediaconvert/*

source mediaconvert/bin/activate

DIR=`pwd`

pushd $VIRTUAL_ENV/lib/python2.7/site-packages/
zip -r $DIR/lambda.zip *
popd

pushd $DIR/7-MediaConvertJobLambda
zip -g $DIR/lambda.zip *.py
popd

