
import pytest as pt
import os
import arrow

import src.adapters.incoming.usecases.find_pilot_use_case as uc

def test_no_pilots_found_for_location():
    pilot = uc.find_pilot_for('Nowhere', depart_on, return_on)
    assert pilot = None
