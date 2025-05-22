pc() {
    if [ -n "$2" ]; then  # 检查是否传入了第二个参数
        head -n "$2" "$1" | column -s, -t | less -#2 -N -S
    else
        column -s, -t < "$1" | less -#2 -N -S  # 无参数时处理整个文件
    fi
}
