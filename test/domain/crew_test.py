import pytest as pt

def f():
    raise SystemExit(1)


def test_mytest():
    with pt.raises(SystemExit):
        f()
