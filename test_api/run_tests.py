#!/usr/bin/env python3
"""
测试运行脚本

提供多种测试执行方式：
- 运行所有测试
- 按标记运行
- 生成Allure报告
- 分布式执行
"""
import os
import sys
import argparse
import subprocess
from pathlib import Path
from datetime import datetime


def run_command(cmd: list, description: str = ""):
    """运行命令"""
    if description:
        print(f"\n{'='*60}")
        print(f"{description}")
        print(f"{'='*60}")
    
    print(f"执行命令: {' '.join(cmd)}")
    result = subprocess.run(cmd, shell=False)
    return result.returncode


def run_all_tests(args):
    """运行所有测试"""
    cmd = [
        sys.executable, "-m", "pytest",
        "testcases",
        "-v",
        f"--alluredir={args.allure_dir}"
    ]
    
    if args.clean:
        cmd.append("--clean-alluredir")
    
    if args.parallel > 1:
        cmd.extend(["-n", str(args.parallel)])
    
    if args.reruns > 0:
        cmd.extend(["--reruns", str(args.reruns)])
    
    return run_command(cmd, "运行所有测试")


def run_smoke_tests(args):
    """运行冒烟测试"""
    cmd = [
        sys.executable, "-m", "pytest",
        "testcases",
        "-v",
        "-m", "smoke",
        f"--alluredir={args.allure_dir}"
    ]
    
    if args.clean:
        cmd.append("--clean-alluredir")
    
    return run_command(cmd, "运行冒烟测试")


def run_regression_tests(args):
    """运行回归测试"""
    cmd = [
        sys.executable, "-m", "pytest",
        "testcases",
        "-v",
        "-m", "regression",
        f"--alluredir={args.allure_dir}"
    ]
    
    if args.clean:
        cmd.append("--clean-alluredir")
    
    if args.parallel > 1:
        cmd.extend(["-n", str(args.parallel)])
    
    return run_command(cmd, "运行回归测试")


def run_by_marker(marker: str, args):
    """按标记运行测试"""
    cmd = [
        sys.executable, "-m", "pytest",
        "testcases",
        "-v",
        "-m", marker,
        f"--alluredir={args.allure_dir}"
    ]
    
    if args.clean:
        cmd.append("--clean-alluredir")
    
    return run_command(cmd, f"运行标记为 '{marker}' 的测试")


def run_by_keyword(keyword: str, args):
    """按关键字运行测试"""
    cmd = [
        sys.executable, "-m", "pytest",
        "testcases",
        "-v",
        "-k", keyword,
        f"--alluredir={args.allure_dir}"
    ]
    
    return run_command(cmd, f"运行匹配关键字 '{keyword}' 的测试")


def generate_allure_report(args):
    """生成Allure报告"""
    report_dir = Path(args.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成报告
    cmd = [
        "allure", "generate",
        args.allure_dir,
        "-o", str(report_dir),
        "--clean"
    ]
    
    result = run_command(cmd, "生成Allure报告")
    
    if result == 0:
        print(f"\n报告已生成: {report_dir.absolute()}")
        print(f"使用以下命令查看报告:")
        print(f"  allure open {report_dir}")
    
    return result


def serve_allure_report(args):
    """启动Allure报告服务"""
    cmd = [
        "allure", "serve",
        args.allure_dir,
        "-p", str(args.port)
    ]
    
    return run_command(cmd, f"启动Allure报告服务 (端口: {args.port})")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="StudyStride API测试运行工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 运行所有测试
  python run_tests.py all
  
  # 运行冒烟测试
  python run_tests.py smoke
  
  # 运行回归测试（并行执行）
  python run_tests.py regression -n 4
  
  # 按标记运行
  python run_tests.py marker -m "auth and smoke"
  
  # 按关键字运行
  python run_tests.py keyword -k "login"
  
  # 生成Allure报告
  python run_tests.py report
  
  # 启动Allure报告服务
  python run_tests.py serve -p 8080
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 全局参数
    parser.add_argument(
        "--allure-dir",
        default="reports/allure-results",
        help="Allure结果目录"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="清理Allure结果目录"
    )
    parser.add_argument(
        "-n", "--parallel",
        type=int,
        default=1,
        help="并行执行数"
    )
    parser.add_argument(
        "--reruns",
        type=int,
        default=2,
        help="失败重试次数"
    )
    
    # all 命令
    subparsers.add_parser("all", help="运行所有测试")
    
    # smoke 命令
    subparsers.add_parser("smoke", help="运行冒烟测试")
    
    # regression 命令
    subparsers.add_parser("regression", help="运行回归测试")
    
    # marker 命令
    marker_parser = subparsers.add_parser("marker", help="按标记运行测试")
    marker_parser.add_argument("-m", "--marker", required=True, help="测试标记")
    
    # keyword 命令
    keyword_parser = subparsers.add_parser("keyword", help="按关键字运行测试")
    keyword_parser.add_argument("-k", "--keyword", required=True, help="测试关键字")
    
    # report 命令
    report_parser = subparsers.add_parser("report", help="生成Allure报告")
    report_parser.add_argument(
        "--report-dir",
        default="reports/allure-report",
        help="报告输出目录"
    )
    
    # serve 命令
    serve_parser = subparsers.add_parser("serve", help="启动Allure报告服务")
    serve_parser.add_argument(
        "-p", "--port",
        type=int,
        default=8080,
        help="服务端口"
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # 确保结果目录存在
    Path(args.allure_dir).mkdir(parents=True, exist_ok=True)
    
    # 执行命令
    commands = {
        "all": run_all_tests,
        "smoke": run_smoke_tests,
        "regression": run_regression_tests,
        "marker": lambda a: run_by_marker(a.marker, a),
        "keyword": lambda a: run_by_keyword(a.keyword, a),
        "report": generate_allure_report,
        "serve": serve_allure_report
    }
    
    func = commands.get(args.command)
    if func:
        return func(args)
    else:
        print(f"未知命令: {args.command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
