#!/bin/bash
export pid=`ps -ef | grep 'raspivid' | awk '{print $2}' | sed -n 1p`
kill $pid
export pid=`ps -ef | grep 'raspivid' | awk '{print $2}' | sed -n 1p`
kill $pid
export pid=`ps -ef | grep 'ffmpeg' | awk '{print $2}' | sed -n 2p` 
kill $pid
export pid=`ps -ef | grep 'ffmpeg' | awk '{print $2}' | sed -n 2p` 
kill $pid
