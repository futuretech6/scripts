# fzf 交互式 git checkout：本地 + 远端分支，按最近提交排序，右侧预览提交历史
gco() {
    local branch
    branch=$(
        git branch --all --sort=-committerdate \
            --format='%(if)%(symref)%(then)%(else)%(refname:short)%(end)' 2>/dev/null \
            | grep -v '^$' \
            | fzf --ansi --no-multi \
                  --preview 'git log --oneline --graph --decorate --color=always {} | head -200'
    ) || return
    [ -n "$branch" ] && git checkout "${branch#origin/}"
}
