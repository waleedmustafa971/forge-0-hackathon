#!/usr/bin/env bash
# Makes sure the Docker daemon of the docker-in-docker feature is running, or says why not.
# The feature selects legacy iptables, which newer host kernels no longer provide; dockerd then
# fails with "iptables v1.8.9 (legacy): can't initialize iptables table `nat'". If the daemon is
# not up, this switches to the nftables backend and starts it, once the feature's own start gave up.
set -uo pipefail
ready() { timeout 5 docker info > /dev/null 2>&1; }

for _ in $(seq 1 15); do ready && exit 0; sleep 2; done

if [ "$(readlink -f /usr/sbin/iptables)" != "$(readlink -f /usr/sbin/iptables-nft)" ]; then
  echo "Docker is not up yet: switching iptables to its nftables backend"
  sudo update-alternatives --set iptables /usr/sbin/iptables-nft > /dev/null
  sudo update-alternatives --set ip6tables /usr/sbin/ip6tables-nft > /dev/null
fi
for _ in $(seq 1 10); do ready && exit 0; sleep 2; done  # the feature may still be retrying
pgrep -x dockerd > /dev/null || sudo sh -c 'setsid nohup dockerd > /tmp/dockerd.log 2>&1 &'
for _ in $(seq 1 30); do ready && exit 0; sleep 2; done

echo "The Docker daemon did not start. Its log:" >&2
tail -n 40 /tmp/dockerd.log >&2 2> /dev/null || true
exit 1
