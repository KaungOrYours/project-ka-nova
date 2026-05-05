#!/bin/bash

RUNPOD_HOST="203.57.40.176"
RUNPOD_PORT="10002"
RUNPOD_KEY="~/.ssh/id_ed25519"
TG_TOKEN="8611499938:AAER1U_lj9BU0yb5iccLyrkXgjX3Nxu-gZM"
TG_CHAT="1096527379"

send_telegram() {
    curl -s -X POST "https://api.telegram.org/bot${TG_TOKEN}/sendMessage" \
        -d chat_id="${TG_CHAT}" \
        -d text="$1" > /dev/null
}

echo "=== Ka-Nova Auto Monitor ==="
send_telegram "Ka-Nova monitor started - watching RunPod for completion..."

while true; do
    IS_RUNNING=$(ssh -p $RUNPOD_PORT -i $RUNPOD_KEY -o StrictHostKeyChecking=no \
        root@$RUNPOD_HOST "ps aux | grep 'python3 run.py' | grep -v grep | wc -l" 2>/dev/null)

    if [ "$IS_RUNNING" = "0" ]; then
        echo "Simulation finished! $(date)"
        send_telegram "Ka-Nova simulation COMPLETE! Downloading results..."

        mkdir -p ~/Desktop/ka-nova/results_phase2
        scp -P $RUNPOD_PORT -i $RUNPOD_KEY -r \
            root@$RUNPOD_HOST:/workspace/ka-nova/results/ \
            ~/Desktop/ka-nova/results_phase2/

        scp -P $RUNPOD_PORT -i $RUNPOD_KEY \
            root@$RUNPOD_HOST:/workspace/ka-nova/output_phase2.log \
            ~/Desktop/ka-nova/output_phase2.log

        SUMMARY=$(tail -15 ~/Desktop/ka-nova/output_phase2.log)
        send_telegram "Results downloaded! Summary: ${SUMMARY} -- Go to runpod.io and STOP your pod now!"

        osascript -e 'display notification "Ka-Nova done! Stop RunPod!" with title "Ka-Nova" sound name "Glass"'
        echo "Done! Check Telegram."
        break
    else
        echo "$(date '+%H:%M:%S') - Still running... checking in 60s"
        sleep 60
    fi
done