import pytest

from parse_message import parse_message


def test_parse_message_of_correct_text():
    """Test happy path"""
    incoming_message = {"value": "Червяки: Егор 1, Саша 5, Сергей 0, Юля 3"}
    expected_result = ("Червяки", ("Егор", 1), ("Саша", 5), ("Сергей", 0), ("Юля", 3))
    assert parse_message(incoming_message) == expected_result


text_no_colon = "Червяки Егор 1, Саша 5, Сергей 0, Юля 3"
text_no_comma = "Червяки: Егор 1 Саша 5, Сергей 0, Юля 3"
text_no_score = "Червяки: Егор 1, Саша, Сергей 0, Юля 3"
test_data = [
    ({"value": text_no_colon}, ValueError),
    ({"value": text_no_comma}, ValueError),
    ({"value": text_no_score}, ValueError)
]


@pytest.mark.parametrize("text,expected", test_data)
def test_incorrect_text(text, expected):
    """Test message we can't parse"""
    assert text == expected
