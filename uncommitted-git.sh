#!/bin/bash
BASE_DIR=~

find "$BASE_DIR" -name ".git" | while read gitdir; do
    repo_dir=$(dirname "$gitdir")
    cd "$repo_dir"
    if [[ -n $(git status --porcelain) ]]; then
        echo "Repository with uncommitted changes: $repo_dir"
    fi
done
