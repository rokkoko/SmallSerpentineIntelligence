import pytest
from parse_message import parse

def test_parse_message():
  expected_message = 'Червяки: Егор 1, Саша 5, Сергей 0, Юля 3'
  assert parse(expected_message) == ('Червяки', {'Егор': 1, 'Саша': 5, 'Сергей': 0, 'Юля': 3})