#!/usr/bin/bash

for i in {3..4}
do
	if [ $i -lt 10 ];then
		scontrol update nodename=kunpeng-compute-node0${i} state=resume reason='wakeup node${i}'
	else
		scontrol update nodename=kunpeng-compute-node${i} state=resume reason='wakeup node${i}'
	fi
done


