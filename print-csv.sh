pc() {
    local file="$1"
    local lines="$2"
    local cat_cmd="cat"
    [[ "$file" == *.gz ]] && cat_cmd="zcat"
    if [ -n "$lines" ]; then
        $cat_cmd "$file" | head -n "$lines" | column -s, -t | less -#2 -N -S
    else
        $cat_cmd "$file" | column -s, -t | less -#2 -N -S
    fi
}
