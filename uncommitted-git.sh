uncommitted-git() {
    local base_dir="${1:-$(pwd)}"
    find "$base_dir" -type d -name ".git" | while read git_dir; do
        repo_dir=$(dirname "$git_dir")
        if [[ -n $(git -C "$repo_dir" status --porcelain) ]]; then
            echo "Repository with uncommitted changes: $repo_dir"
        fi
    done
}
