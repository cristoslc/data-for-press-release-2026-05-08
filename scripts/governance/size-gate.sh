#!/bin/bash
MAX_SIZE=$((10 * 1024 * 1024))

for f in "$@"; do
    size=$(stat -f%z "$f" 2>/dev/null || stat -c%s "$f" 2>/dev/null)
    if [ "$size" -gt "$MAX_SIZE" ]; then
        if ! git check-attr -a "$f" | grep -q "filter: lfs"; then
            echo "BLOCK: $f is $((size / 1024 / 1024))MB > 10MB threshold and not tracked by Git LFS"
            echo "  Add to .gitattributes: $f filter=lfs diff=lfs merge=lfs -text"
            exit 1
        fi
    fi
done
exit 0
