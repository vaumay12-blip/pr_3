"""Повторение RED, GREEN и REFACTOR: python run_checks.py --stage all."""
import argparse
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
IMPLEMENTATIONS = {"red": "stages/red/task_manager.py", "green": "stages/green/task_manager.py", "final": "task_manager.py"}


def run(arguments, stage, name, allowed=(0,)):
    directory = ROOT / "results" / stage
    directory.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, TASK_MANAGER_IMPL=IMPLEMENTATIONS[stage], PYTHONIOENCODING="utf-8",
               PYTHONDONTWRITEBYTECODE="1", PYTEST_DISABLE_PLUGIN_AUTOLOAD="1")
    command = [sys.executable, "-B", *arguments]
    process = subprocess.run(command, cwd=ROOT, env=env, text=True, encoding="utf-8",
                             errors="replace", capture_output=True, timeout=90)
    (directory / (name+".log")).write_text(process.stdout+process.stderr,encoding="utf-8")
    if process.returncode not in allowed:
        raise RuntimeError(f"Сбой {stage}/{name}: см. results/{stage}/{name}.log")
    return process


def check_stage(stage):
    directory = ROOT / "results" / stage
    directory.mkdir(parents=True, exist_ok=True)
    summary = {"stage": stage, "implementation": IMPLEMENTATIONS[stage], "python": platform.python_version(), "pytest": {}}
    allowed = (1,) if stage == "red" else (0,)
    for method in ["tdd", "atdd", "sdd"]:
        xml_path = directory / (method+".xml")
        run(["-m","pytest",f"tests/test_{method}.py","-q","--tb=short","--color=no",
             "-p","no:cacheprovider",f"--junitxml={xml_path}"],stage,method,allowed)
        cases = ET.parse(xml_path).getroot().findall('.//testcase')
        failed = sum(c.find('failure') is not None for c in cases)
        errors = sum(c.find('error') is not None for c in cases)
        skipped = sum(c.find('skipped') is not None for c in cases)
        result = {"total":len(cases),"passed":len(cases)-failed-errors-skipped,"failed":failed,"errors":errors,"skipped":skipped}
        if not cases or errors or skipped or (stage=='red' and failed!=len(cases)):
            raise RuntimeError(f"Неожиданный результат {stage}/{method}: {result}")
        summary['pytest'][method] = result
        print(stage,method,result,flush=True)
    json_path=directory/'bdd.json'
    run(["-m","behave","features","--no-color","-f","json","-o",str(json_path),"-f","plain"],stage,'bdd',allowed)
    features=json.loads(json_path.read_text(encoding='utf-8'))
    scenarios=[s for f in features for s in f.get('elements',[]) if s.get('type')=='scenario']
    statuses={}
    for scenario in scenarios:
        state=scenario['status'];statuses[state]=statuses.get(state,0)+1
        for step in scenario.get('steps',[]):
            if step.get('result',{}).get('status')=='undefined':
                raise RuntimeError('Не определён BDD-шаг')
    if not scenarios or (stage!='red' and statuses != {'passed':len(scenarios)}):
        raise RuntimeError(f'Неожиданный BDD-результат: {statuses}')
    summary['bdd']={'total':len(scenarios),'statuses':statuses}
    (directory/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print(stage,'BDD',statuses,flush=True)
    if stage=='final':
        data=directory/'.coverage'
        run(['-m','coverage','run','--branch',f'--data-file={data}','-m','pytest','-q','-p','no:cacheprovider'],stage,'coverage_run')
        run(['-m','coverage','report',f'--data-file={data}','-m'],stage,'coverage')
        run(['-m','coverage','json',f'--data-file={data}','-o',str(directory/'coverage.json')],stage,'coverage_json')
        run(['-m','coverage','html',f'--data-file={data}','-d',str(directory/'coverage_html')],stage,'coverage_html')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage',choices=['red','green','final','all'],default='final')
    args=parser.parse_args()
    for stage in (['red','green','final'] if args.stage=='all' else [args.stage]):
        check_stage(stage)


if __name__=='__main__':
    main()
