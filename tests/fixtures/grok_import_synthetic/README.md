# Synthetic CSV validator fixtures — TEST ONLY

Every row, identifier, measurement and date in this directory is deliberately
synthetic software-test input. These are not NCAA games, player statistics,
sportsbook odds, source observations, or research evidence. Never import these
fixtures into `data/`, join them to lacrosse records, or use them for modeling.

`example.invalid` is a reserved placeholder domain; it does not identify a real
data provider. Passing URL syntax must never imply that this source is genuine.

- `valid.csv`: mechanically valid test records, still UNVERIFIED/unapproved.
- `invalid.csv`: deliberate duplicates, missing values, impossible/ambiguous
  dates, missing timezone, unsafe URL scheme and a short row.
- `schema.json`: test-only schema; it is not an incoming production-data schema.

Additional malformed inputs are explicitly constructed in temporary directories
by `tests/test_validate_incoming.py`. They are never saved as research data.
