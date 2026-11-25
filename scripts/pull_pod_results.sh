#!/usr/bin/env bash
# Pull a campaign results directory off a RunPod pod.
#
# WHY THIS EXISTS: scp and sftp do NOT work over the ssh.runpod.io proxy, and
# that proxy also requires a PTY and ignores a remote command argument, so the
# obvious approaches all fail. This uses runpodctl's relay transfer, which is
# installed on the pod image already and works from anywhere.
#
# Mac prerequisite (one time):
#   gh release download --repo runpod/runpodctl --pattern runpodctl-darwin-arm64
#   chmod +x runpodctl-darwin-arm64 && mv runpodctl-darwin-arm64 ~/.local/bin/runpodctl
# Homebrew install fails on this Mac: the formula needs a newer Xcode.
#
# Usage:
#   scripts/pull_pod_results.sh <pod-ssh-host> <remote-dir> [dest-dir]
# Example:
#   scripts/pull_pod_results.sh v9bqwu3w8be4pj-64410b31@ssh.runpod.io \
#       /workspace/campaign_sk_enforce ~/Desktop/ka-nova-results
set -euo pipefail

POD="${1:?pod ssh host, e.g. xxxx-yyyy@ssh.runpod.io}"
REMOTE="${2:?remote directory, e.g. /workspace/campaign_sk_enforce}"
DEST="${3:-$HOME/Desktop/ka-nova-results}"
KEY="${SSH_KEY:-$HOME/.ssh/id_ed25519}"
RPC="${RUNPODCTL:-$HOME/.local/bin/runpodctl}"

command -v "$RPC" >/dev/null 2>&1 || { echo "runpodctl not found at $RPC, see header" >&2; exit 1; }
mkdir -p "$DEST"

NAME="$(basename "$REMOTE")"
ARCHIVE="/tmp/${NAME}.tar.zst"

ssh_pod() {
    # The proxy needs a PTY and ignores remote command args, so pipe to stdin.
    printf '%s\nexit\n' "$1" \
      | ssh -tt -o StrictHostKeyChecking=no -o ConnectTimeout=20 "$POD" -i "$KEY" 2>/dev/null
}

echo "[1/4] Archiving $REMOTE on the pod"
ssh_pod "tar -I 'zstd -19 -T0' -cf $ARCHIVE -C $(dirname "$REMOTE") $NAME && ls -la $ARCHIVE" \
  | grep -E "\.tar\.zst" || { echo "archive step produced no output, check the pod" >&2; exit 1; }

echo "[2/4] Starting transfer and reading the one-time code"
CODE="$(ssh_pod "rm -f /tmp/send.log; nohup runpodctl send $ARCHIVE > /tmp/send.log 2>&1 & sleep 7; cat /tmp/send.log" \
        | tr -d '\r' | sed -n 's/.*Code is: *\([0-9a-z][0-9a-z-]*\).*/\1/p' | head -1)"
[ -n "$CODE" ] || { echo "could not read a transfer code, check /tmp/send.log on the pod" >&2; exit 1; }
echo "      code: $CODE"

echo "[3/4] Receiving into $DEST"
( cd "$DEST" && "$RPC" receive "$CODE" )

echo "[4/4] Extracting and verifying"
# macOS tar is bsdtar, where -I means --include, not a compressor. bsdtar
# auto-detects zstd, GNU tar does not, so try plain extract then fall back.
( cd "$DEST" \
  && { tar -xf "${NAME}.tar.zst" 2>/dev/null \
       || zstd -dc "${NAME}.tar.zst" | tar -xf - ; } \
  && rm -f "${NAME}.tar.zst" )
echo
echo "Files pulled into $DEST/$NAME:"
find "$DEST/$NAME" -type f | wc -l | tr -d ' ' | sed 's/$/ files/'
du -sh "$DEST/$NAME"
echo
echo "Reminder: analysis tooling reads KA_NOVA_RESULTS_DIR."
echo "  KA_NOVA_RESULTS_DIR=$DEST/$NAME python3 -m analysis.kpi"
