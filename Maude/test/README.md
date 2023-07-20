# Tests

Assumptions:
- Every `reduce` or `rewrite` command is considered a unit test.
- Each test must result in a term of kind `Bool` (`true` iff the test passes).
- A test is named by the first alphanumeric sequence after the Maude keyword.

For rewrite commands, a convenient way to define the correctness of the result is a boolean predicate on the resulting configuration.

## Running Tests
See [here](../README.md).
