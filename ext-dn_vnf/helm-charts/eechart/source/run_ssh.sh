#!/usr/bin/env bash

date "+%H:%M:%S Starting $0..."
IP=$1
USERNAME=$2
SCRIPT=$3
PARAMS=$4

DIR=$(dirname $0)

date "+%H:%M:%S Waiting for $IP to be ready..."
i=5
while !  ssh -T -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=10 -o LogLevel=ERROR "$USERNAME"@"$IP" 'exit' ; do
    date "+%H:%M:%S Error accessing $IP, retrying..."
    sleep 5
    i=$(( $i - 1 ))
    [ $i -ge 0 ] || exit 1
done

date "+%H:%M:%S SSH server is up, sending script '${DIR}/${SCRIPT}'..."
scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ${DIR}/${SCRIPT} "$USERNAME"@"$IP":
if [ $? -ne 0 ]; then
    date "+%H:%M:%S scp error"
    exit 1
fi
date "+%H:%M:%S OK. Setting file permissions"
ssh -T -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=10 -o LogLevel=ERROR "$USERNAME"@"$IP" "chmod a+x $SCRIPT"
if [ $? -ne 0 ]; then
    date "+%H:%M:%S ssh error"
    exit 1
fi

COMMAND="./$SCRIPT"
[ ${#PARAMS} -ge 0 ] || COMMAND="${COMMAND=} $PARAMS"
date "+%H:%M:%S Running '$COMMAND' on $IP..."
ssh -T -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=10 -o LogLevel=ERROR "$USERNAME"@"$IP" "$COMMAND"
if [ $? -ne 0 ]; then
    date "+%H:%M:%S ssh error"
    exit 1
fi

date "+%H:%M:%S End"
exit 0
