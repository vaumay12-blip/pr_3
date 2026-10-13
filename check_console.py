"""Три проверки реального консольного процесса, отдельно от тестов ядра."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'results' / 'final'

def run(args, text=''):
    result = subprocess.run([sys.executable, 'app.py', *args], input=text,
                            text=True, capture_output=True, cwd=ROOT)
    assert result.returncode == 0, result.stderr
    return result.stdout

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    demo = run(['--demo'])
    assert 'Общая длительность: 8 ч' in demo
    assert 'Расписание сохранено: True' in demo
    (OUT / 'demo.log').write_text(demo, encoding='utf-8')
    flow = run([], '1\nA\nПервая\n2\n1\nB\nВторая\n3\n2\nB\nA\n3\n4\n0\n')
    assert 'A -> B' in flow and 'B | Вторая | 2 | 5' in flow
    (OUT / 'console_flow.log').write_text(flow, encoding='utf-8')
    invalid = run([], '4\n9\n1\nA\nЗадача\nabc\n0\n')
    assert 'Список задач пуст' in invalid
    assert 'Выберите пункт от 0 до 4' in invalid and 'Ошибка:' in invalid
    (OUT / 'console_invalid.log').write_text(invalid, encoding='utf-8')
    message = 'Console checks: 3 passed\n'
    (OUT / 'console_summary.log').write_text(message, encoding='utf-8')
    print(message, end='')

if __name__ == '__main__':
    main()
