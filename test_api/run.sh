#!/bin/bash
# StudyStride API测试运行脚本

# 设置编码
export LANG=en_US.UTF-8

# 默认配置
ALLURE_DIR="reports/allure-results"
REPORT_DIR="reports/allure-report"
PARALLEL=1
RERUNS=2

# 显示帮助信息
show_help() {
    cat << EOF
StudyStride API测试运行脚本

用法: ./run.sh [命令] [选项]

命令:
  all          运行所有测试
  smoke        运行冒烟测试
  regression   运行回归测试
  marker       按标记运行测试 (需指定 -m)
  keyword      按关键字运行测试 (需指定 -k)
  report       生成Allure报告
  serve        启动Allure报告服务
  clean        清理测试报告和日志
  help         显示帮助信息

选项:
  -n NUM       并行执行数 (默认: 1)
  -m MARKER    测试标记
  -k KEYWORD   测试关键字
  -p PORT      服务端口 (默认: 8080)

示例:
  ./run.sh all
  ./run.sh smoke
  ./run.sh regression -n 4
  ./run.sh marker -m "auth and smoke"
  ./run.sh keyword -k "login"
  ./run.sh report
  ./run.sh serve -p 8080
EOF
}

# 运行所有测试
run_all() {
    echo "========================================"
    echo "运行所有测试"
    echo "========================================"
    python -m pytest testcases \
        -v \
        --alluredir="$ALLURE_DIR" \
        --clean-alluredir \
        -n "$PARALLEL" \
        --reruns "$RERUNS"
}

# 运行冒烟测试
run_smoke() {
    echo "========================================"
    echo "运行冒烟测试"
    echo "========================================"
    python -m pytest testcases \
        -v \
        -m "smoke" \
        --alluredir="$ALLURE_DIR" \
        --clean-alluredir
}

# 运行回归测试
run_regression() {
    echo "========================================"
    echo "运行回归测试"
    echo "========================================"
    python -m pytest testcases \
        -v \
        -m "regression" \
        --alluredir="$ALLURE_DIR" \
        --clean-alluredir \
        -n "$PARALLEL"
}

# 按标记运行
run_marker() {
    local marker="$1"
    echo "========================================"
    echo "运行标记为 '$marker' 的测试"
    echo "========================================"
    python -m pytest testcases \
        -v \
        -m "$marker" \
        --alluredir="$ALLURE_DIR" \
        --clean-alluredir
}

# 按关键字运行
run_keyword() {
    local keyword="$1"
    echo "========================================"
    echo "运行匹配关键字 '$keyword' 的测试"
    echo "========================================"
    python -m pytest testcases \
        -v \
        -k "$keyword" \
        --alluredir="$ALLURE_DIR"
}

# 生成报告
generate_report() {
    echo "========================================"
    echo "生成Allure报告"
    echo "========================================"
    mkdir -p "$REPORT_DIR"
    allure generate "$ALLURE_DIR" -o "$REPORT_DIR" --clean
    echo ""
    echo "报告已生成: $REPORT_DIR"
    echo "使用命令查看: allure open $REPORT_DIR"
}

# 启动报告服务
serve_report() {
    local port="${1:-8080}"
    echo "========================================"
    echo "启动Allure报告服务 (端口: $port)"
    echo "========================================"
    allure serve "$ALLURE_DIR" -p "$port"
}

# 清理
clean() {
    echo "========================================"
    echo "清理测试报告和日志"
    echo "========================================"
    rm -rf "$ALLURE_DIR"
    rm -rf "$REPORT_DIR"
    rm -rf logs/*.log
    rm -rf screenshots/*.png
    echo "清理完成"
}

# 确保目录存在
mkdir -p "$ALLURE_DIR"
mkdir -p "$REPORT_DIR"

# 解析命令
COMMAND="${1:-help}"
shift || true

# 解析选项
while getopts "n:m:k:p:" opt; do
    case $opt in
        n) PARALLEL="$OPTARG" ;;
        m) MARKER="$OPTARG" ;;
        k) KEYWORD="$OPTARG" ;;
        p) PORT="$OPTARG" ;;
        *) show_help; exit 1 ;;
    esac
done

# 执行命令
case "$COMMAND" in
    all)
        run_all
        ;;
    smoke)
        run_smoke
        ;;
    regression)
        run_regression
        ;;
    marker)
        if [ -z "$MARKER" ]; then
            echo "错误: 请指定标记 (-m)"
            exit 1
        fi
        run_marker "$MARKER"
        ;;
    keyword)
        if [ -z "$KEYWORD" ]; then
            echo "错误: 请指定关键字 (-k)"
            exit 1
        fi
        run_keyword "$KEYWORD"
        ;;
    report)
        generate_report
        ;;
    serve)
        serve_report "${PORT:-8080}"
        ;;
    clean)
        clean
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "未知命令: $COMMAND"
        show_help
        exit 1
        ;;
esac
