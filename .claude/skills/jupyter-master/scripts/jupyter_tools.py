#!/usr/bin/env python3
"""
jupyter_tools.py - 분류 경쟁 대회용 Jupyter Notebook 안전 처리 도구

핵심 원칙:
  - Claude는 .ipynb 파일을 절대 직접 편집하지 않는다.
  - 모든 노트북 변환/수정은 반드시 이 스크립트를 통해서만 수행한다.

사용법:
  python jupyter_tools.py convert <source.py> [--output <output.ipynb>]
  python jupyter_tools.py clean   <notebook.ipynb>
"""

import argparse
import subprocess
import sys
from pathlib import Path


def convert_to_ipynb(py_file: str, output: str | None = None) -> Path:
    """
    순수 파이썬 스크립트(.py)를 Jupyter Notebook(.ipynb)으로 변환한다.

    jupytext를 사용하여 변환하므로, JSON 구조가 깨질 위험이 없다.
    Claude가 .ipynb를 직접 수정하는 대신 반드시 이 함수를 사용해야 한다.

    Args:
        py_file:  변환할 .py 파일 경로
        output:   출력 .ipynb 파일 경로 (생략 시 같은 위치에 동일 이름으로 생성)

    Returns:
        생성된 .ipynb 파일의 Path 객체

    Raises:
        FileNotFoundError: 입력 파일이 없을 때
        RuntimeError:      jupytext 실행 실패 시
    """
    source = Path(py_file)
    if not source.exists():
        raise FileNotFoundError(f"입력 파일을 찾을 수 없습니다: {source}")
    if source.suffix.lower() != ".py":
        raise ValueError(f".py 파일만 변환할 수 있습니다. (받은 파일: {source.suffix})")

    # 출력 경로 결정
    dest = Path(output) if output else source.with_suffix(".ipynb")

    # jupytext로 변환 실행
    cmd = ["jupytext", "--to", "notebook", str(source), "--output", str(dest)]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(
            f"jupytext 변환 실패:\n"
            f"  명령어: {' '.join(cmd)}\n"
            f"  stderr: {result.stderr.strip()}"
        )

    print(f"[convert] 변환 완료: {source} → {dest}")
    return dest


def clean_for_submission(notebook_file: str) -> Path:
    """
    대회 제출용으로 노트북의 모든 셀 실행 결과를 초기화한다.

    대회 채점 시스템은 출력이 있는 노트북을 '미실행 간주'하여 감점하는 경우가 있다.
    이 함수는 nbconvert --clear-output을 사용해 안전하게 초기화한다.
    원본 파일을 in-place로 수정한다.

    Args:
        notebook_file: 초기화할 .ipynb 파일 경로

    Returns:
        처리된 .ipynb 파일의 Path 객체

    Raises:
        FileNotFoundError: 파일이 없을 때
        RuntimeError:      nbconvert 실행 실패 시
    """
    notebook = Path(notebook_file)
    if not notebook.exists():
        raise FileNotFoundError(f"노트북 파일을 찾을 수 없습니다: {notebook}")
    if notebook.suffix.lower() != ".ipynb":
        raise ValueError(f".ipynb 파일만 처리할 수 있습니다. (받은 파일: {notebook.suffix})")

    cmd = [
        "jupyter", "nbconvert",
        "--ClearOutputPreprocessor.enabled=True",
        "--to", "notebook",
        "--inplace",
        str(notebook),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(
            f"nbconvert 출력 초기화 실패:\n"
            f"  명령어: {' '.join(cmd)}\n"
            f"  stderr: {result.stderr.strip()}"
        )

    print(f"[clean] 출력 초기화 완료: {notebook}")
    return notebook


def _check_dependencies() -> None:
    """jupytext와 nbconvert 설치 여부를 사전 확인한다."""
    missing = []
    for tool in ("jupytext", "jupyter"):
        result = subprocess.run(
            [tool, "--version"], capture_output=True, text=True
        )
        if result.returncode != 0:
            missing.append(tool)

    if missing:
        pkg_map = {"jupytext": "jupytext", "jupyter": "nbconvert"}
        install_list = " ".join(pkg_map[t] for t in missing)
        print(
            f"[오류] 필수 도구가 설치되어 있지 않습니다: {', '.join(missing)}\n"
            f"  설치 명령어: pip install {install_list}",
            file=sys.stderr,
        )
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="분류 경쟁 대회용 Jupyter Notebook 안전 처리 도구",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  # .py → .ipynb 변환
  python jupyter_tools.py convert solution.py
  python jupyter_tools.py convert solution.py --output submission.ipynb

  # 노트북 출력 초기화 (제출 전 필수)
  python jupyter_tools.py clean submission.ipynb
""",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # convert 하위 명령어
    convert_parser = subparsers.add_parser(
        "convert", help=".py 파일을 .ipynb로 변환"
    )
    convert_parser.add_argument("source", help="변환할 .py 파일 경로")
    convert_parser.add_argument(
        "--output", "-o", default=None, help="출력 .ipynb 파일 경로 (생략 시 자동 결정)"
    )

    # clean 하위 명령어
    clean_parser = subparsers.add_parser(
        "clean", help="노트북 셀 출력 초기화 (제출용)"
    )
    clean_parser.add_argument("notebook", help="초기화할 .ipynb 파일 경로")

    args = parser.parse_args()
    _check_dependencies()

    try:
        if args.command == "convert":
            dest = convert_to_ipynb(args.source, args.output)
            print(f"\n✅ 변환 성공: {dest}")
        elif args.command == "clean":
            result = clean_for_submission(args.notebook)
            print(f"\n✅ 출력 초기화 성공: {result}")
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        print(f"\n❌ 오류: {e}", file=sys.stderr)
        sys.exit(1)

    # 제출 전 최종 경고 (항상 출력)
    print(
        "\n" + "=" * 70 + "\n"
        "✨ 작업 완료! 제출하기 전에 반드시 Google Colab에 업로드하고\n"
        "   '런타임 > 모두 실행'을 눌러 에러가 없는지 확인하세요!\n"
        + "=" * 70
    )


if __name__ == "__main__":
    main()
