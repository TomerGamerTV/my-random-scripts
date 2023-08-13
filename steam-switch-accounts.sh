#!/bin/bash

# Check if the Steam directory exists
if [ ! -d "$HOME/.steam/steam" ]; then
  echo "Error: Steam directory not found"
  exit 1
fi

# Check if the user provided an account name
if [ -z "$1" ]; then
  echo "Usage: $0 ACCOUNT_NAME"
  exit 1
fi

# Switch to the specified Steam account
echo "Switching to account: $1"
$HOME/.steam/steam/steam.sh -login $1
