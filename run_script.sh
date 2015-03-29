#!/bin/bash

# Write the pid to a file so it can be retrieved at a later date
echo "pid: $$" > pid.txt

finish=0
trap 'finish=1' SIGUSR1

# When you want to exit the loop at the next iteration:
# kill -SIGUSR1 pid
# Where pid is the process ID of the script

while (( finish != 1 ))
do
	source android_script.sh apk_list-4.txt
	sleep 5
done
