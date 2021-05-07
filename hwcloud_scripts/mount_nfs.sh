#!/usr/bin/bash

for i in {1..30}
do
	echo "mount nfs kunpeng-compute-node${i}"
	ssh root@dxwind-compute-node${i} mount -t nfs -o vers=3,timeo=600,nolock 192.168.0.98:/ /home/op/share
	#umount -v /home/op/share
done
