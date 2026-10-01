"""Smoke-test the built wheel in a separate environment, away from the source checkout."""
from pathlib import Path
import os
import subprocess
import sys
import tempfile
import zipfile


def main():
    repo = Path(__file__).resolve().parents[1]
    wheels = sorted((repo / 'dist').glob('codex_universal_modder-*.whl'))
    if len(wheels) != 1:
        raise ValueError('build exactly one wheel with uv build first')
    wheel = wheels[0]
    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())
        for required in ['um/ps1/WinDrive.ps1', 'um/ps1/ProcLoopback.ps1',
                         'um/blender/render_sprites.py', 'um/fonts/SpaceGrotesk-Bold.ttf',
                         'um/fonts/OFL-SpaceGrotesk.txt', 'um/resources/knowledge/TEMPLATE.md',
                         'um/resources/skills/codex-modder/SKILL.md']:
            assert required in names, required
    with tempfile.TemporaryDirectory(prefix='cmod-wheel-') as directory:
        root = Path(directory)
        subprocess.run(['uv', 'venv', '--python', sys.executable, str(root / 'env')], check=True)
        python = root / ('env/Scripts/python.exe' if os.name == 'nt' else 'env/bin/python')
        subprocess.run(['uv', 'pip', 'install', '--python', str(python), str(wheel)], check=True)
        code = """
from pathlib import Path
from um import kb, doctor
import um
assert all(doctor.report()['required'].values())
root = kb.local_root()
assert root is not None and root.is_relative_to(Path(um.__file__).parent)
assert kb.search(root, ['terraria'])
print('Installed wheel: offline knowledge, modules and runtime assets verified')
"""
        subprocess.run([str(python), '-I', '-c', code], cwd=root, check=True)
        for command in [['--version'], ['doctor', '--json'], ['kb', 'search', 'terraria']]:
            result = subprocess.run([str(python), '-I', '-m', 'um', *command], cwd=root, text=True,
                                    encoding='utf-8', capture_output=True)
            if result.returncode:
                raise RuntimeError(f'{command}: {result.stderr}')
            assert result.stdout.strip(), command
    print('PASS: isolated wheel smoke tests')


if __name__ == '__main__':
    main()
