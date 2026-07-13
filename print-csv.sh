pc() {
    local file="$1"
    local lines="$2"
    local cat_cmd="cat"
    [[ "$file" == *.gz ]] && cat_cmd="zcat"
    local less_opts="-#2 -N -S"
    if less --help 2>&1 | grep -q '\-\-header'; then
        less_opts="$less_opts --header 1"
    fi
    if [ -n "$lines" ]; then
        $cat_cmd "$file" | head -n "$lines" | column -s, -t | less $less_opts
    else
        $cat_cmd "$file" | column -s, -t | less $less_opts
    fi
}
