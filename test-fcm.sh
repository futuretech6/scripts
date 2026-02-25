#!/bin/bash
trap 'echo; exit 130' INT
port=5228
hosts=(mtalk.google.com alt{1..8}-mtalk.google.com)
max_len=$(($(printf '%s\n' "${hosts[@]}" | awk '{print length}' | sort -nr | head -1) + ${#port} + 4))
for host in "${hosts[@]}"; do
    host_port="${host}:${port}"
    dots=$(printf '%*s' $((max_len - ${#host_port})) '' | tr ' ' '.')
    echo -n "Testing ${host_port} ${dots} "
    start=$(date +%s%3N)
    if timeout 3 bash -c "echo >/dev/tcp/${host}/${port}" 2>/dev/null; then
        elapsed=$(($(date +%s%3N) - start))
        echo "✓ Connected (${elapsed}ms)"
    else
        echo "✗ Failed"
    fi
done
