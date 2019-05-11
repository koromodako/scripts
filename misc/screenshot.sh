#!/usr/bin/env bash
SCREENSHOTS_DIR=~/screenshots
mkdir -p "${SCREENSHOTS_DIR}"
gnome-screenshot -f "${SCREENSHOTS_DIR}/$(date -Iseconds).png"
