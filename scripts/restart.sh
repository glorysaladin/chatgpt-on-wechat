#! /bin/bash

WK_DIR="$(cd "$(dirname "$0")"; pwd -P)"
echo $WK_DIR

sh $WK_DIR/shutdown.sh
sleep 5s
sh $WK_DIR/start.sh
