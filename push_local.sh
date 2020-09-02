#!/bin/bash

bundle exec jekyll build
git checkout gh-pages
git add _site
cp -r _site/* .
git commit -am "built site locally"
git push
git checkout master
