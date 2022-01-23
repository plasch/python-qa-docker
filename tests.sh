#!/bin/bash

docker build -t tests .

docker run --name tests_run tests pytest --browser $1 -n $2

docker cp tests_run:/app/allure-report .

allure serve allure-report

docker rm tests_run

# docker run --name tests_run --network selenoid tests \
# && docker cp tests_run:/app/allure-report . \
# && allure serve allure-report
