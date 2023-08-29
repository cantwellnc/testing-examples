from reversal import rev
from hypothesis import given, example
import hypothesis.strategies as st


def test_rev():
    result = rev("abc")
    expected = "cba"
    assert result == expected


# should preserve length of string
@given(input_str=st.text())
def test_rev_length_preserving(input_str):
    assert len(input_str) == len(rev(input_str))


# should actually return a  string
@given(input_str=st.text())
def test_rev_returns_string(input_str):
    assert isinstance(rev(input_str), str)


# should produce the original string when applied twice
@given(input_str=st.text())
def test_rev_is_self_inverse(input_str):
    assert rev(rev(input_str)) == input_str
