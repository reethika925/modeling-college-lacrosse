# Collector fixture provenance

`ncaa_championship_2025.json` is a small **real-response test fixture**, copied
without modification from the NCAA daily JSON probe retrieved November 9, 2026
(America/New_York):

https://data.ncaa.com/casablanca/scoreboard/lacrosse-men/d1/2025/05/26/scoreboard.json

It contains the one actual championship game. Unit tests make explicitly
labeled in-memory mutations to test cancellation, missing scores, invalid
scores, overtime, and bad winner flags. These mutations are test-only scenarios;
they are never saved to the real dataset or raw-response cache.

`ncaa_duplicate_records_2025.json` contains only the actual game `6311207`
extracted from these two original responses, with no statistical changes:

- https://data.ncaa.com/casablanca/scoreboard/lacrosse-men/d1/2025/02/22/scoreboard.json
- https://data.ncaa.com/casablanca/scoreboard/lacrosse-men/d1/2025/02/23/scoreboard.json

`ncaa_history_2025_excerpt.html` is the actual 2025 table row extracted from
https://www.ncaa.com/history/lacrosse-men/d1 and wrapped in a minimal table for
testing. The original page and retrieval metadata remain in the raw cache.
