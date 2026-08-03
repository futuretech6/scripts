# fzf 交互式 git checkout：本地 + 远端分支，按最近提交排序，右侧预览提交历史
# 用法：
#   gco            打开 fzf 交互选择器
#   gco mas        以 mas 作为初始过滤词进入 fzf；若唯一匹配则直接切换
#   gco mas<Tab>   Tab 补全分支名 -> master
gco() {
    local branch
    branch=$(
        git branch --all --sort=-committerdate \
            --format='%(if)%(symref)%(then)%(else)%(refname:short)%(end)' 2>/dev/null \
            | grep -v '^$' \
            | fzf --ansi --no-multi --select-1 --query "$*" \
                  --preview 'git log --oneline --graph --decorate --color=always {} | head -200'
    ) || return
    [ -n "$branch" ] && git checkout "${branch#origin/}"
}

# gco 的 Tab 补全：本地分支 + 去掉远端前缀的远端分支
_gco_complete() {
    local cur branches
    cur="${COMP_WORDS[COMP_CWORD]}"
    branches=$(
        {
            git for-each-ref --format='%(refname:short)' refs/heads 2>/dev/null
            git for-each-ref --format='%(refname:short)' refs/remotes 2>/dev/null \
                | sed 's|^[^/]*/||'
        } | grep -vx 'HEAD' | sort -u
    )
    mapfile -t COMPREPLY < <(compgen -W "$branches" -- "$cur")
}
complete -F _gco_complete gco
