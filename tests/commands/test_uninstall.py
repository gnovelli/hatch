import os

from click.testing import CliRunner

from hatch.cli import hatch
from hatch.env import get_installed_packages
from hatch.utils import remove_path, temp_chdir
from hatch.venv import VENV_DIR, create_venv, get_new_venv_name, venv
from ..utils import requires_internet


@requires_internet
def test_requirements():
    with temp_chdir() as d:
        runner = CliRunner()
        venv_dir = os.path.join(d, 'venv')
        create_venv(venv_dir)
        with open(os.path.join(d, 'requirements.txt'), 'w') as f:
            f.write('six\n')

        with venv(venv_dir):
            runner.invoke(hatch, ['install', 'six'])
            assert 'six' in get_installed_packages()
            result = runner.invoke(hatch, ['uninstall', '-y'])
            assert 'six' not in get_installed_packages()

        assert result.exit_code == 0


def test_requirements_none():
    with temp_chdir() as d:
        runner = CliRunner()
        venv_dir = os.path.join(d, 'venv')
        create_venv(venv_dir)

        with venv(venv_dir):
            result = runner.invoke(hatch, ['uninstall', '-y'])

        assert result.exit_code == 1
        assert 'Unable to locate a requirements file.' in result.output


@requires_internet
def test_packages():
    with temp_chdir() as d:
        runner = CliRunner()
        venv_dir = os.path.join(d, 'venv')
        create_venv(venv_dir)

        with venv(venv_dir):
            runner.invoke(hatch, ['install', 'six'])
            assert 'six' in get_installed_packages()
            result = runner.invoke(hatch, ['uninstall', '-y', 'six'])
            assert 'six' not in get_installed_packages()

        assert result.exit_code == 0


def test_env_not_exist():
    with temp_chdir():
        runner = CliRunner()

        env_name = get_new_venv_name()
        result = runner.invoke(hatch, ['uninstall', '-y', '-e', env_name, 'six'])

        assert result.exit_code == 1
        assert 'Virtual env named `{}` does not exist.'.format(env_name) in result.output


@requires_internet
def test_env():
    with temp_chdir():
        runner = CliRunner()

        env_name = get_new_venv_name()
        venv_dir = os.path.join(VENV_DIR, env_name)
        create_venv(venv_dir)

        try:
            runner.invoke(hatch, ['install', '-e', env_name, 'six'])
            with venv(venv_dir):
                assert 'six' in get_installed_packages()
            result = runner.invoke(hatch, ['uninstall', '-y', '-e', env_name, 'six'])
            with venv(venv_dir):
                assert 'six' not in get_installed_packages()
        finally:
            remove_path(venv_dir)

        assert result.exit_code == 0
