#!/bin/bash
export pid=`ps -ef | grep 'raspivid' | awk '{print $2}' | sed -n 1p`
kill $pid
export pid=`ps -ef | grep 'raspivid' | awk '{print $2}' | sed -n 1p`
kill $pid
export pid=`ps -ef | grep 'gst-launch-1.0' | awk '{print $2}' | sed -n 2p` 
kill $pid
export pid=`ps -ef | grep 'gst-launch-1.0' | awk '{print $2}' | sed -n 2p` 
kill $pid
