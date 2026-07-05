#!/bin/bash

# Find the running llama-server process
# We look for the binary path
PROCESS_INFO=$(ps aux | grep "llama-server" | grep -v grep | head -n 1)

if [ -z "$PROCESS_INFO" ]; then
    echo "Error: No running llama-server process found."
    exit 1
fi

# Extract the path to the binary. 
# Usually, the command starts at the beginning of the line or after the user/pid/cpu/mem/etc.
# Let's try to find the first string that looks like a path to a binary.
BINARY_PATH=$(echo "$PROCESS_INFO" | awk '{for(i=1;i<=NF;i++) if ($i ~ /^\//) {print $i; break}}')

if [ -z "$BINARY_PATH" ]; then
    echo "Error: Could not identify the llama-server binary path from process list."
    echo "Process info was: $PROCESS_INFO"
    exit 1
fi

if [ ! -x "$BINARY_PATH" ]; then
    echo "Error: Binary path $BINARY_PATH is not executable."
    exit 1
fi

echo "Found llama-server binary at: $BINARY_PATH"
$BINARY_PATH --version
