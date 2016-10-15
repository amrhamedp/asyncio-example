import asyncio
import concurrent.futures
import os
from pathlib import Path
import sys
import time

import click
import aiohttp


@click.command()
@click.argument(
    'py_files',
    nargs=-1,
    type=click.Path(exists=True, dir_okay=False)
)
def main(py_files):
    try:
        linters = discover_flake8_binaries()
    except LookupError as le:
        click.secho(str(le), fg='red', err=True)
        raise click.Abort

    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    tasks = {
        (pf, linter): loop.create_task(get_warnings(pf, linter))
        for pf in py_files
        for linter in linters
    }
    done, pending = loop.run_until_complete(asyncio.wait(tasks.values()))
    assert len(done) == len(tasks)
    for pf, task in tasks.items():
        for warning in task.result():
            print(warning)


def report_usage(coro):
    async def wrapper(*args, **kwargs):
        start = time.time()
        try:
            return await coro(*args, **kwargs)
        finally:
            params = {'args{}'.format(i): arg for i, arg in enumerate(args)}
            params.update({
                'duration': time.time() - start,
            }, **kwargs)
            try:
                with aiohttp.ClientSession() as s, aiohttp.Timeout(2):
                    async with s.get('http://example.com', params=params) as resp:
                        print(resp.url)
            except aiohttp.Timeout:
                print("timeout")
    return wrapper


@report_usage
async def get_warnings(py_file, linter, timeout=60):
    try:
        returncode, stdout, stderr = await run_linter(
            py_file, linter, timeout=timeout
        )
    except TimeoutError:
        return [
            'ERROR:1:1: X001 flake8 timed out linting {}'.format(py_file)
        ]

    result = []
    if stderr:
        for line in stderr.split(b'\n'):
            line = line.strip().decode('utf8', 'ignore')
            result.append('ERROR:1:1: X002 ' + line)
    if stdout:
        for line in stdout.split(b'\n'):
            line = line.strip().decode('utf8', 'ignore')
            result.append(line)
    return result


async def run_linter(py_file, linter, timeout=60):
    proc = await asyncio.create_subprocess_exec(
        linter, py_file,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        # preexec_fn=
    )
    try:
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(),
            timeout=timeout,
        )
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        raise
    return proc.returncode, stdout, stderr


def discover_flake8_binaries():
    path = os.environ['PATH'].split(os.pathsep)
    path.insert(0, Path(sys.argv[0]).parent)
    for d in path:
        directory = Path(d)
        flake8_2 = directory / 'flake8-2'
        flake8_3 = directory / 'flake8-3'
        if flake8_2.is_file() and flake8_3.is_file():
            return str(flake8_2), str(flake8_3)
    raise LookupError("fatal: cannot find flakes on PATH")


if __name__ == '__main__':
    main()
