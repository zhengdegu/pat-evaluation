#!/bin/bash
nohup gunicorn -b 0.0.0.0:5000 -w 10 main:app >> /tmp/log 2>&1 &