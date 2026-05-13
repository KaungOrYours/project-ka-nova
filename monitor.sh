#!/bin/bash
TG_TOKEN="8611499938:AAHpvM4Ai5wrIc5S5W0zpuFyWLtPWjMTsis"
TG_CHAT="1096527379"

send() {
    curl -s -X POST "https://api.telegram.org/bot${TG_TOKEN}/sendMessage" \
        -d "chat_id=${TG_CHAT}" -d "text=$1" > /dev/null
}

LAST_A=0
LAST_B=0
LAST_C=0

send "Ka-Nova monitor started - tracking A/B/C every 2%"

while true; do
    # Extract progress from logs
    A=$(grep -o '[0-9]*%' /workspace/ka-nova/output_A.log 2>/dev/null | tail -1 | tr -d '%')
    B=$(grep -o '[0-9]*%' /workspace/ka-nova/output_B.log 2>/dev/null | tail -1 | tr -d '%')
    C=$(grep -o '[0-9]*%' /workspace/ka-nova/output_C.log 2>/dev/null | tail -1 | tr -d '%')

    A=${A:-0}; B=${B:-0}; C=${C:-0}

    # Extract ETA
    ETA_A=$(grep -o 'eta=[0-9.]*h' /workspace/ka-nova/output_A.log 2>/dev/null | tail -1)
    ETA_B=$(grep -o 'eta=[0-9.]*h' /workspace/ka-nova/output_B.log 2>/dev/null | tail -1)
    ETA_C=$(grep -o 'eta=[0-9.]*h' /workspace/ka-nova/output_C.log 2>/dev/null | tail -1)

    # Send update every 2%
    if [ "$A" -ge $((LAST_A + 2)) ] || [ "$B" -ge $((LAST_B + 2)) ] || [ "$C" -ge $((LAST_C + 2)) ]; then
        send "Ka-Nova Progress Update
A: ${A}% ${ETA_A}
B: ${B}% ${ETA_B}
C: ${C}% ${ETA_C}
Time: $(date '+%H:%M')"
        [ "$A" -ge $((LAST_A + 2)) ] && LAST_A=$A
        [ "$B" -ge $((LAST_B + 2)) ] && LAST_B=$B
        [ "$C" -ge $((LAST_C + 2)) ] && LAST_C=$C
    fi

    # Check if all done
    A_DONE=$(grep -c "Simulation complete" /workspace/ka-nova/output_A.log 2>/dev/null)
    B_DONE=$(grep -c "Simulation complete" /workspace/ka-nova/output_B.log 2>/dev/null)
    C_DONE=$(grep -c "Simulation complete" /workspace/ka-nova/output_C.log 2>/dev/null)

    if [ "$A_DONE" -gt 0 ] && [ "$B_DONE" -gt 0 ] && [ "$C_DONE" -gt 0 ]; then
        send "Ka-Nova ALL SCENARIOS COMPLETE! Downloading results now..."
        break
    fi

    sleep 60
done
