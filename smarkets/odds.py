from __future__ import absolute_import
"""Odds conversion classes"""

import bisect
import functools
import re
from decimal import Decimal

import six
from babel.numbers import format_percent

from smarkets.utils import memoized_by_args, slots_repr


_RAW_TABLE = {
    (1, 1): (Decimal('50.00'), Decimal('50.00')),
    (20, 21): (Decimal('51.22'), Decimal('48.78')),
    (10, 11): (Decimal('52.38'), Decimal('47.62')),
    (5, 6): (Decimal('54.55'), Decimal('45.45')),
    (4, 5): (Decimal('55.56'), Decimal('44.44')),
    (8, 11): (Decimal('57.89'), Decimal('42.11')),
    (4, 6): (Decimal('60.00'), Decimal('40.00')),
    (8, 13): (Decimal('61.90'), Decimal('38.10')),
    (60, 100): (Decimal('62.50'), Decimal('37.50')),
    (4, 7): (Decimal('63.64'), Decimal('36.36')),
    (8, 15): (Decimal('65.22'), Decimal('34.78')),
    (1, 2): (Decimal('66.67'), Decimal('33.33')),
    (40, 85): (Decimal('68.00'), Decimal('32.00')),
    (4, 9): (Decimal('69.23'), Decimal('30.77')),
    (40, 95): (Decimal('70.37'), Decimal('29.63')),
    (2, 5): (Decimal('71.43'), Decimal('28.57')),
    (4, 11): (Decimal('73.33'), Decimal('26.67')),
    (1, 3): (Decimal('75.00'), Decimal('25.00')),
    (30, 100): (Decimal('76.92'), Decimal('23.08')),
    (2, 7): (Decimal('77.78'), Decimal('22.22')),
    (20, 75): (Decimal('78.95'), Decimal('21.05')),
    (1, 4): (Decimal('80.00'), Decimal('20.00')),
    (20, 85): (Decimal('80.95'), Decimal('19.05')),
    (2, 9): (Decimal('81.82'), Decimal('18.18')),
    (20, 95): (Decimal('82.61'), Decimal('17.39')),
    (1, 5): (Decimal('83.33'), Decimal('16.67')),
    (2, 11): (Decimal('84.62'), Decimal('15.38')),
    (1, 6): (Decimal('85.71'), Decimal('14.29')),
    (2, 13): (Decimal('86.67'), Decimal('13.33')),
    (15, 100): (Decimal('86.96'), Decimal('13.04')),
    (1, 7): (Decimal('87.50'), Decimal('12.50')),
    (2, 15): (Decimal('88.24'), Decimal('11.76')),
    (1, 8): (Decimal('88.89'), Decimal('11.11')),
    (2, 17): (Decimal('89.47'), Decimal('10.53')),
    (1, 9): (Decimal('90.00'), Decimal('10.00')),
    (10, 95): (Decimal('90.48'), Decimal('9.52')),
    (1, 10): (Decimal('90.91'), Decimal('9.09')),
    (1, 11): (Decimal('91.67'), Decimal('8.33')),
    (17, 200): (Decimal('92.17'), Decimal('7.83')),
    (1, 12): (Decimal('92.31'), Decimal('7.69')),
    (8, 100): (Decimal('92.59'), Decimal('7.41')),
    (1, 13): (Decimal('92.86'), Decimal('7.14')),
    (15, 200): (Decimal('93.02'), Decimal('6.98')),
    (1, 14): (Decimal('93.33'), Decimal('6.67')),
    (1, 15): (Decimal('93.75'), Decimal('6.25')),
    (1, 16): (Decimal('94.12'), Decimal('5.88')),
    (1, 17): (Decimal('94.44'), Decimal('5.56')),
    (1, 18): (Decimal('94.74'), Decimal('5.26')),
    (1, 19): (Decimal('95.00'), Decimal('5.00')),
    (1, 20): (Decimal('95.24'), Decimal('4.76')),
    (1, 21): (Decimal('95.45'), Decimal('4.55')),
    (1, 22): (Decimal('95.65'), Decimal('4.35')),
    (1, 23): (Decimal('95.83'), Decimal('4.17')),
    (1, 24): (Decimal('96.00'), Decimal('4.00')),
    (1, 25): (Decimal('96.15'), Decimal('3.85')),
    (1, 26): (Decimal('96.30'), Decimal('3.70')),
    (1, 27): (Decimal('96.43'), Decimal('3.57')),
    (1, 28): (Decimal('96.55'), Decimal('3.45')),
    (1, 29): (Decimal('96.67'), Decimal('3.33')),
    (1, 30): (Decimal('96.77'), Decimal('3.23')),
    (1, 31): (Decimal('96.88'), Decimal('3.13')),
    (1, 32): (Decimal('96.97'), Decimal('3.03')),
    (1, 33): (Decimal('97.06'), Decimal('2.94')),
    (3, 100): (Decimal('97.09'), Decimal('2.91')),
    (1, 34): (Decimal('97.14'), Decimal('2.86')),
    (1, 35): (Decimal('97.22'), Decimal('2.78')),
    (1, 36): (Decimal('97.30'), Decimal('2.70')),
    (1, 37): (Decimal('97.37'), Decimal('2.63')),
    (1, 38): (Decimal('97.44'), Decimal('2.56')),
    (1, 39): (Decimal('97.50'), Decimal('2.50')),
    (1, 40): (Decimal('97.56'), Decimal('2.44')),
    (1, 41): (Decimal('97.62'), Decimal('2.38')),
    (1, 42): (Decimal('97.67'), Decimal('2.33')),
    (1, 43): (Decimal('97.73'), Decimal('2.27')),
    (1, 44): (Decimal('97.78'), Decimal('2.22')),
    (1, 45): (Decimal('97.83'), Decimal('2.17')),
    (1, 46): (Decimal('97.87'), Decimal('2.13')),
    (1, 47): (Decimal('97.92'), Decimal('2.08')),
    (1, 48): (Decimal('97.96'), Decimal('2.04')),
    (1, 49): (Decimal('98.00'), Decimal('2.00')),
    (1, 50): (Decimal('98.04'), Decimal('1.96')),
    (1, 51): (Decimal('98.08'), Decimal('1.92')),
    (1, 52): (Decimal('98.11'), Decimal('1.89')),
    (1, 53): (Decimal('98.15'), Decimal('1.85')),
    (1, 54): (Decimal('98.18'), Decimal('1.82')),
    (1, 55): (Decimal('98.21'), Decimal('1.79')),
    (1, 56): (Decimal('98.25'), Decimal('1.75')),
    (1, 57): (Decimal('98.28'), Decimal('1.72')),
    (1, 58): (Decimal('98.31'), Decimal('1.69')),
    (1, 59): (Decimal('98.33'), Decimal('1.67')),
    (1, 60): (Decimal('98.36'), Decimal('1.64')),
    (1, 61): (Decimal('98.39'), Decimal('1.61')),
    (1, 62): (Decimal('98.41'), Decimal('1.59')),
    (1, 63): (Decimal('98.44'), Decimal('1.56')),
    (1, 64): (Decimal('98.46'), Decimal('1.54')),
    (1, 65): (Decimal('98.48'), Decimal('1.52')),
    (1, 66): (Decimal('98.51'), Decimal('1.49')),
    (3, 200): (Decimal('98.52'), Decimal('1.48')),
    (1, 67): (Decimal('98.53'), Decimal('1.47')),
    (1, 68): (Decimal('98.55'), Decimal('1.45')),
    (1, 69): (Decimal('98.57'), Decimal('1.43')),
    (1, 70): (Decimal('98.59'), Decimal('1.41')),
    (1, 71): (Decimal('98.61'), Decimal('1.39')),
    (1, 72): (Decimal('98.63'), Decimal('1.37')),
    (1, 73): (Decimal('98.65'), Decimal('1.35')),
    (1, 74): (Decimal('98.67'), Decimal('1.33')),
    (1, 75): (Decimal('98.68'), Decimal('1.32')),
    (1, 76): (Decimal('98.70'), Decimal('1.30')),
    (1, 77): (Decimal('98.72'), Decimal('1.28')),
    (1, 78): (Decimal('98.73'), Decimal('1.27')),
    (1, 79): (Decimal('98.75'), Decimal('1.25')),
    (1, 80): (Decimal('98.77'), Decimal('1.23')),
    (1, 81): (Decimal('98.78'), Decimal('1.22')),
    (1, 82): (Decimal('98.80'), Decimal('1.20')),
    (1, 83): (Decimal('98.81'), Decimal('1.19')),
    (1, 84): (Decimal('98.82'), Decimal('1.18')),
    (1, 85): (Decimal('98.84'), Decimal('1.16')),
    (1, 86): (Decimal('98.85'), Decimal('1.15')),
    (1, 87): (Decimal('98.86'), Decimal('1.14')),
    (1, 88): (Decimal('98.88'), Decimal('1.12')),
    (1, 89): (Decimal('98.89'), Decimal('1.11')),
    (1, 90): (Decimal('98.90'), Decimal('1.10')),
    (1, 91): (Decimal('98.91'), Decimal('1.09')),
    (1, 92): (Decimal('98.92'), Decimal('1.08')),
    (1, 93): (Decimal('98.94'), Decimal('1.06')),
    (1, 94): (Decimal('98.95'), Decimal('1.05')),
    (1, 95): (Decimal('98.96'), Decimal('1.04')),
    (1, 96): (Decimal('98.97'), Decimal('1.03')),
    (1, 97): (Decimal('98.98'), Decimal('1.02')),
    (1, 98): (Decimal('98.99'), Decimal('1.01')),
    (1, 99): (Decimal('99.00'), Decimal('1.00')),
    (1, 100): (Decimal('99.01'), Decimal('0.99')),
    (1, 200): (Decimal('99.50'), Decimal('0.50')),
    (1, 300): (Decimal('99.67'), Decimal('0.33')),
    (1, 400): (Decimal('99.75'), Decimal('0.25')),
    (1, 500): (Decimal('99.80'), Decimal('0.20')),
    (1, 600): (Decimal('99.83'), Decimal('0.17')),
    (1, 700): (Decimal('99.86'), Decimal('0.14')),
    (1, 800): (Decimal('99.88'), Decimal('0.12')),
    (1, 900): (Decimal('99.89'), Decimal('0.11')),
    (1, 1000): (Decimal('99.90'), Decimal('0.10')),
    (1, 2000): (Decimal('99.95'), Decimal('0.05')),
    (1, 3000): (Decimal('99.97'), Decimal('0.03')),
    (1, 5000): (Decimal('99.98'), Decimal('0.02')),
    (1, 10000): (Decimal('99.99'), Decimal('0.01')),
}

_RAW_ALL = list(_RAW_TABLE.keys()) + [(k[1], k[0]) for k in _RAW_TABLE.keys()]

# TODO: Add three places of precision to back end

_DEC_TO_PCT = {
    Decimal('1.0001'): Decimal('99.99'),
    Decimal('1.01'): Decimal('99.01'),
    Decimal('1.02'): Decimal('98.04'),
    Decimal('1.03'): Decimal('97.09'),
    Decimal('1.04'): Decimal('96.15'),
    Decimal('1.05'): Decimal('95.24'),
    Decimal('1.06'): Decimal('94.34'),
    Decimal('1.07'): Decimal('93.46'),
    Decimal('1.08'): Decimal('92.59'),
    Decimal('1.09'): Decimal('91.74'),
    Decimal('1.10'): Decimal('90.91'),
    Decimal('1.11'): Decimal('90.09'),
    Decimal('1.12'): Decimal('89.29'),
    Decimal('1.13'): Decimal('88.50'),
    Decimal('1.14'): Decimal('87.72'),
    Decimal('1.15'): Decimal('86.96'),
    Decimal('1.16'): Decimal('86.21'),
    Decimal('1.17'): Decimal('85.47'),
    Decimal('1.18'): Decimal('84.75'),
    Decimal('1.19'): Decimal('84.03'),
    Decimal('1.20'): Decimal('83.33'),
    Decimal('1.21'): Decimal('82.64'),
    Decimal('1.22'): Decimal('81.97'),
    Decimal('1.23'): Decimal('81.30'),
    Decimal('1.24'): Decimal('80.65'),
    Decimal('1.25'): Decimal('80.00'),
    Decimal('1.26'): Decimal('79.37'),
    Decimal('1.27'): Decimal('78.74'),
    Decimal('1.28'): Decimal('78.12'),
    Decimal('1.29'): Decimal('77.52'),
    Decimal('1.30'): Decimal('76.92'),
    Decimal('1.31'): Decimal('76.34'),
    Decimal('1.32'): Decimal('75.76'),
    Decimal('1.33'): Decimal('75.19'),
    Decimal('1.34'): Decimal('74.63'),
    Decimal('1.35'): Decimal('74.07'),
    Decimal('1.36'): Decimal('73.53'),
    Decimal('1.37'): Decimal('72.99'),
    Decimal('1.38'): Decimal('72.46'),
    Decimal('1.39'): Decimal('71.94'),
    Decimal('1.40'): Decimal('71.43'),
    Decimal('1.41'): Decimal('70.92'),
    Decimal('1.42'): Decimal('70.42'),
    Decimal('1.43'): Decimal('69.93'),
    Decimal('1.44'): Decimal('69.44'),
    Decimal('1.45'): Decimal('68.97'),
    Decimal('1.46'): Decimal('68.49'),
    Decimal('1.47'): Decimal('68.03'),
    Decimal('1.48'): Decimal('67.57'),
    Decimal('1.49'): Decimal('67.11'),
    Decimal('1.50'): Decimal('66.67'),
    Decimal('1.51'): Decimal('66.23'),
    Decimal('1.52'): Decimal('65.79'),
    Decimal('1.53'): Decimal('65.36'),
    Decimal('1.54'): Decimal('64.94'),
    Decimal('1.55'): Decimal('64.52'),
    Decimal('1.56'): Decimal('64.10'),
    Decimal('1.57'): Decimal('63.69'),
    Decimal('1.58'): Decimal('63.29'),
    Decimal('1.59'): Decimal('62.89'),
    Decimal('1.60'): Decimal('62.50'),
    Decimal('1.61'): Decimal('62.11'),
    Decimal('1.62'): Decimal('61.73'),
    Decimal('1.63'): Decimal('61.35'),
    Decimal('1.64'): Decimal('60.98'),
    Decimal('1.65'): Decimal('60.61'),
    Decimal('1.66'): Decimal('60.24'),
    Decimal('1.67'): Decimal('59.88'),
    Decimal('1.68'): Decimal('59.52'),
    Decimal('1.69'): Decimal('59.17'),
    Decimal('1.70'): Decimal('58.82'),
    Decimal('1.71'): Decimal('58.48'),
    Decimal('1.72'): Decimal('58.14'),
    Decimal('1.73'): Decimal('57.80'),
    Decimal('1.74'): Decimal('57.47'),
    Decimal('1.75'): Decimal('57.14'),
    Decimal('1.76'): Decimal('56.82'),
    Decimal('1.77'): Decimal('56.50'),
    Decimal('1.78'): Decimal('56.18'),
    Decimal('1.79'): Decimal('55.87'),
    Decimal('1.80'): Decimal('55.56'),
    Decimal('1.81'): Decimal('55.25'),
    Decimal('1.82'): Decimal('54.95'),
    Decimal('1.83'): Decimal('54.64'),
    Decimal('1.84'): Decimal('54.35'),
    Decimal('1.85'): Decimal('54.05'),
    Decimal('1.86'): Decimal('53.76'),
    Decimal('1.87'): Decimal('53.48'),
    Decimal('1.88'): Decimal('53.19'),
    Decimal('1.89'): Decimal('52.91'),
    Decimal('1.90'): Decimal('52.63'),
    Decimal('1.91'): Decimal('52.36'),
    Decimal('1.92'): Decimal('52.08'),
    Decimal('1.93'): Decimal('51.81'),
    Decimal('1.94'): Decimal('51.55'),
    Decimal('1.95'): Decimal('51.28'),
    Decimal('1.96'): Decimal('51.02'),
    Decimal('1.97'): Decimal('50.76'),
    Decimal('1.98'): Decimal('50.51'),
    Decimal('1.99'): Decimal('50.25'),
    Decimal('2.00'): Decimal('50.00'),
    Decimal('2.02'): Decimal('49.50'),
    Decimal('2.04'): Decimal('49.02'),
    Decimal('2.06'): Decimal('48.54'),
    Decimal('2.08'): Decimal('48.08'),
    Decimal('2.10'): Decimal('47.62'),
    Decimal('2.12'): Decimal('47.17'),
    Decimal('2.14'): Decimal('46.73'),
    Decimal('2.16'): Decimal('46.30'),
    Decimal('2.18'): Decimal('45.87'),
    Decimal('2.20'): Decimal('45.45'),
    Decimal('2.22'): Decimal('45.05'),
    Decimal('2.24'): Decimal('44.64'),
    Decimal('2.26'): Decimal('44.25'),
    Decimal('2.28'): Decimal('43.86'),
    Decimal('2.30'): Decimal('43.48'),
    Decimal('2.32'): Decimal('43.10'),
    Decimal('2.34'): Decimal('42.74'),
    Decimal('2.36'): Decimal('42.37'),
    Decimal('2.38'): Decimal('42.02'),
    Decimal('2.40'): Decimal('41.67'),
    Decimal('2.42'): Decimal('41.32'),
    Decimal('2.44'): Decimal('40.98'),
    Decimal('2.46'): Decimal('40.65'),
    Decimal('2.48'): Decimal('40.32'),
    Decimal('2.50'): Decimal('40.00'),
    Decimal('2.52'): Decimal('39.68'),
    Decimal('2.54'): Decimal('39.37'),
    Decimal('2.56'): Decimal('39.06'),
    Decimal('2.58'): Decimal('38.76'),
    Decimal('2.60'): Decimal('38.46'),
    Decimal('2.62'): Decimal('38.17'),
    Decimal('2.64'): Decimal('37.88'),
    Decimal('2.66'): Decimal('37.59'),
    Decimal('2.68'): Decimal('37.31'),
    Decimal('2.70'): Decimal('37.04'),
    Decimal('2.72'): Decimal('36.76'),
    Decimal('2.74'): Decimal('36.50'),
    Decimal('2.76'): Decimal('36.23'),
    Decimal('2.78'): Decimal('35.97'),
    Decimal('2.80'): Decimal('35.71'),
    Decimal('2.82'): Decimal('35.46'),
    Decimal('2.84'): Decimal('35.21'),
    Decimal('2.86'): Decimal('34.97'),
    Decimal('2.88'): Decimal('34.72'),
    Decimal('2.90'): Decimal('34.48'),
    Decimal('2.92'): Decimal('34.25'),
    Decimal('2.94'): Decimal('34.01'),
    Decimal('2.96'): Decimal('33.78'),
    Decimal('2.98'): Decimal('33.56'),
    Decimal('3.00'): Decimal('33.33'),
    Decimal('3.05'): Decimal('32.79'),
    Decimal('3.10'): Decimal('32.26'),
    Decimal('3.15'): Decimal('31.75'),
    Decimal('3.20'): Decimal('31.25'),
    Decimal('3.25'): Decimal('30.77'),
    Decimal('3.30'): Decimal('30.30'),
    Decimal('3.35'): Decimal('29.85'),
    Decimal('3.40'): Decimal('29.41'),
    Decimal('3.45'): Decimal('28.99'),
    Decimal('3.50'): Decimal('28.57'),
    Decimal('3.55'): Decimal('28.17'),
    Decimal('3.60'): Decimal('27.78'),
    Decimal('3.65'): Decimal('27.40'),
    Decimal('3.70'): Decimal('27.03'),
    Decimal('3.75'): Decimal('26.67'),
    Decimal('3.80'): Decimal('26.32'),
    Decimal('3.85'): Decimal('25.97'),
    Decimal('3.90'): Decimal('25.64'),
    Decimal('3.95'): Decimal('25.32'),
    Decimal('4.00'): Decimal('25.00'),
    Decimal('4.1'): Decimal('24.39'),
    Decimal('4.2'): Decimal('23.81'),
    Decimal('4.3'): Decimal('23.26'),
    Decimal('4.4'): Decimal('22.73'),
    Decimal('4.5'): Decimal('22.22'),
    Decimal('4.6'): Decimal('21.74'),
    Decimal('4.7'): Decimal('21.28'),
    Decimal('4.8'): Decimal('20.83'),
    Decimal('4.9'): Decimal('20.41'),
    Decimal('5.0'): Decimal('20.00'),
    Decimal('5.1'): Decimal('19.61'),
    Decimal('5.2'): Decimal('19.23'),
    Decimal('5.3'): Decimal('18.87'),
    Decimal('5.4'): Decimal('18.52'),
    Decimal('5.5'): Decimal('18.18'),
    Decimal('5.6'): Decimal('17.86'),
    Decimal('5.7'): Decimal('17.54'),
    Decimal('5.8'): Decimal('17.24'),
    Decimal('5.9'): Decimal('16.95'),
    Decimal('6.0'): Decimal('16.67'),
    Decimal('6.2'): Decimal('16.13'),
    Decimal('6.4'): Decimal('15.62'),
    Decimal('6.6'): Decimal('15.15'),
    Decimal('6.8'): Decimal('14.71'),
    Decimal('7.0'): Decimal('14.29'),
    Decimal('7.2'): Decimal('13.89'),
    Decimal('7.4'): Decimal('13.51'),
    Decimal('7.6'): Decimal('13.16'),
    Decimal('7.8'): Decimal('12.82'),
    Decimal('8.0'): Decimal('12.50'),
    Decimal('8.2'): Decimal('12.20'),
    Decimal('8.4'): Decimal('11.90'),
    Decimal('8.6'): Decimal('11.63'),
    Decimal('8.8'): Decimal('11.36'),
    Decimal('9.0'): Decimal('11.11'),
    Decimal('9.2'): Decimal('10.87'),
    Decimal('9.4'): Decimal('10.64'),
    Decimal('9.6'): Decimal('10.42'),
    Decimal('9.8'): Decimal('10.20'),
    Decimal('10.0'): Decimal('10.00'),
    Decimal('10.5'): Decimal('9.52'),
    Decimal('11.0'): Decimal('9.09'),
    Decimal('11.5'): Decimal('8.70'),
    Decimal('12.0'): Decimal('8.33'),
    Decimal('12.5'): Decimal('8.00'),
    Decimal('13.0'): Decimal('7.69'),
    Decimal('13.5'): Decimal('7.41'),
    Decimal('14.0'): Decimal('7.14'),
    Decimal('14.5'): Decimal('6.90'),
    Decimal('15.0'): Decimal('6.67'),
    Decimal('15.5'): Decimal('6.45'),
    Decimal('16.0'): Decimal('6.25'),
    Decimal('16.5'): Decimal('6.06'),
    Decimal('17.0'): Decimal('5.88'),
    Decimal('17.5'): Decimal('5.71'),
    Decimal('18.0'): Decimal('5.56'),
    Decimal('18.5'): Decimal('5.41'),
    Decimal('19.0'): Decimal('5.26'),
    Decimal('19.5'): Decimal('5.13'),
    Decimal('20.0'): Decimal('5.00'),
    Decimal('21'): Decimal('4.76'),
    Decimal('22'): Decimal('4.55'),
    Decimal('23'): Decimal('4.35'),
    Decimal('24'): Decimal('4.17'),
    Decimal('25'): Decimal('4.00'),
    Decimal('26'): Decimal('3.85'),
    Decimal('27'): Decimal('3.70'),
    Decimal('28'): Decimal('3.57'),
    Decimal('29'): Decimal('3.45'),
    Decimal('30'): Decimal('3.33'),
    Decimal('32'): Decimal('3.12'),
    Decimal('34'): Decimal('2.94'),
    Decimal('36'): Decimal('2.78'),
    Decimal('38'): Decimal('2.63'),
    Decimal('40'): Decimal('2.50'),
    Decimal('42'): Decimal('2.38'),
    Decimal('44'): Decimal('2.27'),
    Decimal('46'): Decimal('2.17'),
    Decimal('48'): Decimal('2.08'),
    Decimal('50'): Decimal('2.00'),
    Decimal('55'): Decimal('1.82'),
    Decimal('60'): Decimal('1.67'),
    Decimal('65'): Decimal('1.54'),
    Decimal('70'): Decimal('1.43'),
    Decimal('75'): Decimal('1.33'),
    Decimal('80'): Decimal('1.25'),
    Decimal('85'): Decimal('1.18'),
    Decimal('90'): Decimal('1.11'),
    Decimal('95'): Decimal('1.05'),
    Decimal('100'): Decimal('1.00'),
    Decimal('110'): Decimal('0.91'),
    Decimal('120'): Decimal('0.83'),
    Decimal('130'): Decimal('0.77'),
    Decimal('140'): Decimal('0.71'),
    Decimal('150'): Decimal('0.67'),
    Decimal('160'): Decimal('0.62'),
    Decimal('170'): Decimal('0.59'),
    Decimal('180'): Decimal('0.56'),
    Decimal('190'): Decimal('0.53'),
    Decimal('200'): Decimal('0.50'),
    Decimal('210'): Decimal('0.48'),
    Decimal('220'): Decimal('0.45'),
    Decimal('230'): Decimal('0.43'),
    Decimal('240'): Decimal('0.42'),
    Decimal('250'): Decimal('0.40'),
    Decimal('260'): Decimal('0.38'),
    Decimal('270'): Decimal('0.37'),
    Decimal('280'): Decimal('0.36'),
    Decimal('290'): Decimal('0.34'),
    Decimal('300'): Decimal('0.33'),
    Decimal('500'): Decimal('0.20'),
    Decimal('1000'): Decimal('0.10'),
    Decimal('10000'): Decimal('0.01')}

_PCT_TO_DEC = dict((y, x) for x, y, in _DEC_TO_PCT.items())

_DEC_TO_PCT_KEYS = sorted(_DEC_TO_PCT.keys())
_PCT_TO_DEC_KEYS = sorted(_PCT_TO_DEC.keys())


@functools.total_ordering
class OddsTableEntry(object):
    __slots__ = ('numerator', 'denominator', 'percent')

    def __init__(self, numerator, denominator, percent):
        self.numerator = numerator
        self.denominator = denominator
        self.percent = percent

    def __lt__(self, other):
        if hasattr(other, 'percent'):
            return self.percent < other.percent
        else:
            return self.percent < other

    def __eq__(self, other):
        if hasattr(other, 'percent'):
            return self.percent == other.percent
        else:
            return self.percent == other

    @classmethod
    def from_raw(cls, nfrom, nto, nhigh, nlow):
        yield cls(nfrom, nto, nhigh)
        yield cls(nto, nfrom, nlow)


class OddsTable(object):
    __slots__ = ('_table',)

    def __init__(self, raw_table):
        self._table = []
        for key, val in six.iteritems(raw_table):
            num, den = key
            left, right = val
            self.append(num, den, left, right)
        self._table.sort()

    def append(self, nfrom, nto, nhigh, nlow):
        for i in OddsTableEntry.from_raw(nfrom, nto, nhigh, nlow):
            self._table.append(i)

    def from_percent(self, percent):
        """Get the correct odds for a percentile price."""
        if not isinstance(percent, Decimal):
            raise Exception("Percent needs to be a Decimal object")
        i = bisect.bisect_left(self._table, percent)
        if i >= 0 and i < len(self._table):
            return self._table[i]
        elif i < 0:
            return self._table[0]
        else:
            return self._table[-1]


TABLE = OddsTable(_RAW_TABLE)
QUANT = Decimal('0.01')
ONE_HUNDRED = Decimal('100')


class Odds(object):
    __slots__ = ('percent',)

    __repr__ = slots_repr

    def __init__(self, percent):
        """
        :type percent: :class:`decimal.Decimal`
        """
        self.percent = percent

    @property
    def percent_str(self):
        percent = self.percent / 100

        # TODO: This forces a locale of GB
        return format_percent(percent, "#,##0.##%", locale="en_GB")

    @property
    def fractional(self):
        previous = TABLE.from_percent(self.percent)
        return (previous.numerator, previous.denominator)

    @property
    def fractional_str(self):
        # Common Fractional idiom for 1 to 1 is 'Evens'
        if self.fractional[0] == self.fractional[1]:
            return 'Evens'
        return '%s to %s' % self.fractional

    @property
    def decimal(self):
        # Takes a percentage price and returns the appropriate decimal odds
        # we don't snap any more
        try:
            value = _PCT_TO_DEC[self.percent]
        except KeyError:
            value = ONE_HUNDRED / self.percent
        return value

    @classmethod
    def snap_to_decimal(cls, side, odds):
        """Take a percent and snap it to the nearest equal or worse decimal price based on side.

        .. note::

            Equal or worse means equal or higher when buying and equal or lower when selling.

        >>> Odds.snap_to_decimal('buy', Decimal('0.3')).percent
        Decimal('0.33')
        >>> Odds.snap_to_decimal('sell', Decimal('0.3')).percent
        Decimal('0.20')

        :type side: 'buy' or 'sell' string
        :type odds: :class:`decimal.Decimal`
        :rtype: :class:`Odds`
        """
        return Odds.snap_to_decimal_move_out_by(side, odds, 0)

    @classmethod
    def snap_to_decimal_move_out_by(cls, side, odds, move_out_by):
        decimal = cls(odds).decimal
        snapped = False
        if side == 'buy':
            i = bisect.bisect_right(_DEC_TO_PCT_KEYS, decimal)
            if i - 1 - move_out_by >= 0:
                snapped = cls(_DEC_TO_PCT[_DEC_TO_PCT_KEYS[i - 1 - move_out_by]])
        elif side == 'sell':
            i = bisect.bisect_left(_DEC_TO_PCT_KEYS, decimal)
            if i + move_out_by < len(_DEC_TO_PCT_KEYS):
                snapped = cls(_DEC_TO_PCT[_DEC_TO_PCT_KEYS[i + move_out_by]])
        if not snapped:
            return None
        return snapped

    @property
    def decimal_str(self):
        output = str(self.decimal)
        output = re.sub('(\.[0-9])0+$', '\\1', output)
        return output

    @property
    def american(self):
        if self.percent < Decimal(50):
            return (Decimal(10000) / self.percent - Decimal(100)).quantize(Decimal(1))
        return (Decimal(-100) / (Decimal(100) / self.percent - Decimal(1))).quantize(Decimal(1))

    @property
    def american_str(self):
        amer = self.american
        return '+%s' % amer if amer > 0 else '%s' % amer

    @classmethod
    def from_american(cls, snap, american):
        if not isinstance(american, Decimal):
            raise Exception("American odds needs to be a Decimal object")
        if american < 0:
            return cls((Decimal(100) / (Decimal(-100) / american + 1)).quantize(QUANT))
        return cls((Decimal(10000) / (american + Decimal(100))).quantize(QUANT))

    @classmethod
    def from_decimal(cls, snap, dec):
        if Decimal(dec) in _DEC_TO_PCT:
            return cls(_DEC_TO_PCT[Decimal(dec)])
        else:
            pct = (ONE_HUNDRED / dec).quantize(QUANT)
            return cls(pct)
        raise ValueError

    @classmethod
    def from_fractional(cls, num, den):
        dec = Decimal(num) / Decimal(den) + Decimal(1)
        return cls((Decimal(100) / dec).quantize(QUANT))

    @classmethod
    def from_percent(cls, snap, percent):
        return cls(percent)


snap_to_decimal_move_out_by = memoized_by_args('side', 'odds', 'move_out_by')(
    Odds.snap_to_decimal_move_out_by)


_ALL_TICKS = sorted(_PCT_TO_DEC)


def ticks_gt(exact_price):
    """
    Returns a generator for all the ticks above the given price.

    >>> list(ticks_gt(Decimal('97.5')))
    [Decimal('98.04'), Decimal('99.01'), Decimal('99.99')]
    >>> list(ticks_gt(Decimal('98.04')))
    [Decimal('99.01'), Decimal('99.99')]
    >>> list(ticks_gt(Decimal('99.99')))
    []
    """
    first_viable = bisect.bisect_right(_ALL_TICKS, exact_price)
    first_invalid_index, step = len(_ALL_TICKS), 1
    return (_ALL_TICKS[i] for i in range(first_viable, first_invalid_index, step))


def ticks_geq(exact_price):
    """
    Like `'ticks_gt' but if the given price is a tick, it is included as well.

    >>> list(ticks_geq(Decimal('97.5')))
    [Decimal('98.04'), Decimal('99.01'), Decimal('99.99')]
    >>> list(ticks_geq(Decimal('98.04')))
    [Decimal('98.04'), Decimal('99.01'), Decimal('99.99')]
    >>> list(ticks_geq(Decimal('99.99')))
    [Decimal('99.99')]
    >>> list(ticks_geq(Decimal('99.991')))
    []
    """
    first_viable = bisect.bisect_left(_ALL_TICKS, exact_price)
    first_invalid_index, step = len(_ALL_TICKS), 1
    return (_ALL_TICKS[i] for i in range(first_viable, first_invalid_index, step))


def ticks_lt(exact_price):
    """
    Returns a generator for all the ticks below the given price.

    >>> list(ticks_lt(Decimal('0.35')))
    [Decimal('0.34'), Decimal('0.33'), Decimal('0.20'), Decimal('0.10'), Decimal('0.01')]
    >>> list(ticks_lt(Decimal('0.20')))
    [Decimal('0.10'), Decimal('0.01')]
    >>> list(ticks_lt(Decimal('0.0001')))
    []
    """
    first_viable = bisect.bisect_left(_ALL_TICKS, exact_price) - 1
    first_invalid_index, step = -1, -1
    return (_ALL_TICKS[i] for i in range(first_viable, first_invalid_index, step))


def ticks_leq(exact_price):
    """
    Like `'ticks_lt' but if the given price is a tick, it is included as well.

    >>> list(ticks_leq(Decimal('0.35')))
    [Decimal('0.34'), Decimal('0.33'), Decimal('0.20'), Decimal('0.10'), Decimal('0.01')]
    >>> list(ticks_leq(Decimal('0.20')))
    [Decimal('0.20'), Decimal('0.10'), Decimal('0.01')]
    >>> list(ticks_leq(Decimal('0.0001')))
    []
    """
    first_viable = bisect.bisect_right(_ALL_TICKS, exact_price) - 1
    first_invalid_index, step = -1, -1
    return (_ALL_TICKS[i] for i in range(first_viable, first_invalid_index, step))


def is_a_tick(exact_price):
    """
    Is the given price one of the available prices?

    >>> is_a_tick(Decimal('0.32'))
    False
    >>> all(is_a_tick(price) for price in ticks_lt(Decimal('0.35')))
    True
    """
    candidate = bisect.bisect_left(_ALL_TICKS, exact_price)
    return candidate != len(_ALL_TICKS) and _ALL_TICKS[candidate] == exact_price


MIN_TICK, MAX_TICK = next(ticks_gt(0)), next(ticks_lt(100))
