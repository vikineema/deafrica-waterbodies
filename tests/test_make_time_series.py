import logging
from pathlib import Path
import re
import sys
import tempfile

from click.testing import CliRunner
import geopandas as gpd
import pytest

from dea_waterbodies.make_time_series import main, RE_IDS_STRING, RE_ID

# Test directory.
HERE = Path(__file__).parent.resolve()
logging.basicConfig(level=logging.INFO)

# Path to Canberra test shapefile.
TEST_SHP = HERE / 'data' / 'waterbodies_canberra.shp'


def setup_module(module):
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    logging.getLogger("").handlers = []


@pytest.fixture
def run_main():
    def _run_cli(
        opts,
        catch_exceptions=False,
        expect_success=True,
        cli_method=main,
        input=None,
    ):
        exe_opts = []
        exe_opts.extend(opts)

        runner = CliRunner()
        result = runner.invoke(cli_method, exe_opts, catch_exceptions=catch_exceptions, input=input)
        if expect_success:
            assert 0 == result.exit_code, "Error for %r. output: %r" % (
                opts,
                result.output,
            )
        return result

    return _run_cli


def test_main(run_main):
    result = run_main([], expect_success=False)
    # TODO(MatthewJA): Make this assert that the output makes sense.
    assert result


def test_id_regex():
    assert RE_ID.match('r3dp84s8n')
    assert not RE_ID.match('r3dp8 4s8n')
    assert not RE_ID.match('r3dp8_s8n')
    assert not RE_ID.match('R3dp84s8n')  # case sensitivity


def test_ids_string_regex():
    assert RE_IDS_STRING.match('r3dp84s8n')
    assert RE_IDS_STRING.match('r3dp84s8n,r3dp84s8n')
    assert RE_IDS_STRING.match('r3dp84s8n,r3dp84s8n,r3dp84s8n')
    assert not RE_IDS_STRING.match('r3dp84s8n-r3dp84s8n-r3dp84s8n')
    assert not RE_IDS_STRING.match('r3dp84s8n r3dp84s8n')
    assert not RE_IDS_STRING.match('r3dp84s8n, r3dp84s8n, r3dp84s8n')
    assert not RE_IDS_STRING.match('r3dp84s8n, r3dp84s8n, r3dp84s8n,')


def test_make_one_csv(tmp_path, run_main):
    ginninderra_id = 'r3dp84s8n'
    result = run_main([
        ginninderra_id,
        '--shapefile', TEST_SHP,
        '--output', tmp_path,
        '-vv',
    ])
    assert result
    expected_out_path = tmp_path / ginninderra_id[:4] / f'{ginninderra_id}.csv'
    assert expected_out_path.exists()
    csv = gpd.pd.read_csv(expected_out_path, sep=',')
    assert csv.columns[0] == 'Observation Date'
    assert csv.columns[1] == 'Wet pixel percentage'
    assert re.match(r'Wet pixel count \(n = \d+\)', csv.columns[2])
    assert csv.columns[2] == 'Wet pixel count (n = 1358)'
    assert csv.iloc[0]['Observation Date'].startswith('2021-03-30')
    assert int(csv.iloc[0]['Wet pixel count (n = 1358)']) == 1200


# def test_make_one_csv_stdin(tmp_path):
#     ginninderra_id = 'r3dp84s8n'
#     result = RUNNER.invoke(main, [
#         '--shapefile', TEST_SHP,
#         '--output', tmp_path,
#     ], input=f'{ginninderra_id}\n', catch_exceptions=False)
#     assert result
#     expected_out_path = tmp_path / ginninderra_id[:4] / f'{ginninderra_id}.csv'
#     assert expected_out_path.exists()
#     csv = gpd.pd.read_csv(expected_out_path, sep=',')
#     assert csv.columns[0] == 'Observation Date'
#     assert csv.columns[1] == 'Wet pixel percentage'
#     assert re.match(r'Wet pixel count (n = \d+)', csv.columns[2])
#     assert csv.columns[2] == 'Wet pixel count (n = 1358)'
#     assert csv.iloc[0]['Observation Date'].startswith('2021-03-30')
#     assert int(csv.iloc[0]['Wet pixel count (n = 1358)']) == 1200
