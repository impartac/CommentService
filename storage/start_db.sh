#!/bin/bash
docker build -t mypostgres .
docker run -d --name mypostgres -p 5432:5432 mypostgres