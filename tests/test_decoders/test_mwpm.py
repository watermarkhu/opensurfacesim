from opensurfacesim.main import *
import opensurfacesim as oss
import pytest
import random
from .errors import get_error_combinations, get_error_keys


CODES = oss.codes.CODES
ERRORS = oss.errors.ERRORS
SIZE_PM = 12
SIZE_FM = 4
ITERS = 100


def test_get_blossomv():
    oss.decoders.mwpm.get_blossomv(accept=True)


@pytest.mark.parametrize("Code", CODES)
@pytest.mark.parametrize("use_blossomv", [True, False])
@pytest.mark.parametrize("errors", get_error_combinations())
@pytest.mark.parametrize(
    "faulty, size, max_rate, extra_keys",
    [
        (False, SIZE_PM, 0.2, []),
        (True, SIZE_FM, 0.05, ["pm_bitflip", "pm_phaseflip"]),
    ],
)
def test_decoder_pm(size, Code, use_blossomv, errors, faulty, max_rate, extra_keys):
    """Test initialize function for all configurations."""

    Decoder_module = getattr(oss.decoders, "mwpm").sim
    if hasattr(Decoder_module, Code.capitalize()):
        decoder_module = getattr(Decoder_module, Code.capitalize())
        Code_module = getattr(oss.codes, Code).sim
        code_module = (
            getattr(Code_module, "FaultyMeasurements")
            if faulty
            else getattr(Code_module, "PerfectMeasurements")
        )
        code = code_module(size)
        code.initialize(*errors)
        decoder = decoder_module(code)
        error_keys = get_error_keys(errors) + extra_keys

        trivial = 0
        for _ in range(ITERS):
            error_rates = {key: random.random() * max_rate for key in error_keys}
            code.random_errors(**error_rates)
            decoder.decode(use_blossomv=use_blossomv)
            trivial += code.trivial_ancillas

        assert trivial == ITERS

    else:
        assert True


