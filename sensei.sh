#!/bin/bash
# Sensei Munin plugin

case $1 in
    config)
    echo "graph_category sensors"
    echo "graph_title Basement measurements"
    echo "graph_args --base 1000 -l 0"
    echo "graph_scale no"
    echo "rh.label Humidity"
    echo "rh.type GAUGE"
    echo "rh.draw LINE1"
    echo "temp.label Temperature"
    echo "temp.type GAUGE"
    echo "temp.draw LINE1"
    echo "plug.label Plug State"
    echo "plug.type GAUGE"
    echo "plug.draw AREA"
    echo "graph_info Graph of Dehumidifier State and Sensors"
    exit 0;;
    esac

latest=`cat /var/log/munin/sensei.out`

temp=`echo $latest | cut -d ' ' -f 2`
rh=`echo $latest | cut -d ' ' -f 3`
state=`echo $latest | cut -d ' ' -f 7`

echo "temp.value $temp"
echo "rh.value $rh"
echo "plug.value $((state * 10))"
