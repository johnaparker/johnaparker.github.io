#!/bin/bash

bundle exec jekyll build
cp -r _site/* .local_build
cd .local_build
git add *
git commit -am "built site locally"
git push origin gh-pages --no-verify
