#!/bin/bash

#test only, not used in production.
export FLASK_APP=app/__init__.py
export FLASK_DEBUG=1
flask run