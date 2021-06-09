#!/bin/bash

func=$1

# python -m pytest ${func}

python -m pytest --cov=. ${func}