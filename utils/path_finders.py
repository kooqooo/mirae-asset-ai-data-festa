import os
from pathlib import Path

def find_project_path(start_path='.'):
    start_path = os.path.abspath(start_path)
    if not os.path.exists(start_path):
        raise ValueError(f"지정된 경로가 존재하지 않습니다: {start_path}")

    for root, dirs, files in os.walk(start_path):
        if '.git' in dirs:
            return os.path.abspath(root)
    return None

def find_project_path_pathlib(start_path='.'):
    start_path = Path(start_path).resolve()
    if not start_path.exists():
        raise ValueError(f"지정된 경로가 존재하지 않습니다: {start_path}")

    for root, dirs, files in os.walk(start_path):
        if '.git' in dirs:
            return str(Path(root).resolve())
    return None

if __name__ == "__main__":
    try:
        project_path = find_project_path()
        if project_path:
            print(f'.git 폴더가 있는 프로젝트 경로: {project_path}')
        else:
            print('.git 폴더를 찾을 수 없습니다.')
        project_path = find_project_path_pathlib()
        if project_path:
            print(f'.git 폴더가 있는 프로젝트 경로: {project_path}')
        else:
            print('.git 폴더를 찾을 수 없습니다.')
    except ValueError as e:
        print(e)