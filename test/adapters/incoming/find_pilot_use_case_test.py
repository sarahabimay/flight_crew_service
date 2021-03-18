
import pytest as pt
import os
import arrow

import src.adapters.incoming.usecases.find_pilot_use_case as uc
from src.adapters.incoming.controller import FindCrewRequest

@pt.fixture
def valid_request():
    depart_on = arrow.utcnow()
    return_on = arrow.utcnow().shift(days=2)
    return FindCrewRequest('Nowhere', depart_on, return_on)

def test_no_pilots_found_for_location(valid_request):
    pilot = uc.find_pilot_for(valid_request)
    assert pilot == None

def test_a_pilot_found_for_location(valid_request):
    pilot = uc.find_pilot_for(valid_request)
    assert pilot == {'ID': 123}
