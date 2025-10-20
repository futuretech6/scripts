#!/bin/bash
BASE_DIR=$(pwd)

find "$BASE_DIR" -type d -name ".git" | while read git_dir; do
    repo_dir=$(dirname "$git_dir")
    if [[ -n $(git -C "$repo_dir" status --porcelain) ]]; then
        echo "Repository with uncommitted changes: $repo_dir"
    fi
done

cd $BASE_DIR
