#!/bin/sh

path="/mnt/DroboFS/Shares/DroboApps/"

${path}speedtest/speedtest-cli --server 6696 > ${path}speedtest/log/$(date +"%d_%m_%Y--%H_%M").log &
