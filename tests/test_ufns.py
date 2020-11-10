from opensurfacesim.main import *
import opensurfacesim as oss
import matplotlib as mpl
import pytest
import random
from .variables import *

ITERS = 100
no_wait_param = oss.plot.PlotParams(blocking_wait=0.001)


@pytest.mark.parametrize("Code", CODES)
@pytest.mark.parametrize("errors", get_error_combinations())
@pytest.mark.parametrize(
    "faulty, size, max_rate, extra_keys",
    [
        (False, SIZE_PM, 0.2, []),
        (True, SIZE_FM, 0.05, ["pm_bitflip", "pm_phaseflip"]),
    ],
)
def test_ufns_sim(size, Code, errors, faulty, max_rate, extra_keys):
    """Test initialize function for all configurations."""

    Decoder_module = getattr(oss.decoders, "ufns").sim
    if hasattr(Decoder_module, Code.capitalize()):
        decoder_module = getattr(Decoder_module, Code.capitalize())
        Code_module = getattr(oss.codes, Code).sim
        code_module = getattr(Code_module, "FaultyMeasurements") if faulty else getattr(Code_module, "PerfectMeasurements")
        code = code_module(size)
        code.initialize(*errors)
        decoder = decoder_module(code)
        error_keys = get_error_keys(errors) + extra_keys

        trivial = 0
        for _ in range(ITERS):
            error_rates = {key: random.random() * max_rate for key in error_keys}
            code.random_errors(**error_rates)
            decoder.decode()
            trivial += code.trivial_ancillas

        assert trivial == ITERS

    else:
        assert True


@pytest.mark.plotting
@pytest.mark.parametrize(
    "faulty, size",
    [
        (False, SIZE_PM),
        (True, SIZE_FM),
    ],
)
def test_ufns_plot(faulty, size):
    code, decoder = initialize(
        size,
        "toric",
        "ufns",
        enabled_errors=["pauli"],
        faulty_measurements=faulty,
        initial_states=(0, 0),
        plotting=True,
        plot_params=no_wait_param,
        step_bucket=True,
        step_cluster=True,
        step_node=True,
        step_cycle=True,
        step_peel=True,
    )
    run(code, decoder, error_rates={"p_bitflip": 0.1}, decode_initial=False)
