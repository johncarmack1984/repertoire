#!/usr/bin/env bash
# An agent-written PR description full of filler: the revision keeps every fact in far fewer words.
set -euo pipefail

cat > pr-draft.md <<'EOF'
## Summary

This PR introduces a number of improvements to the way that our HTTP client handles failed requests. It's worth noting that, previously, transient errors from upstream services were being surfaced directly to callers due to the fact that no retry logic was in place.

## Changes

- Retry logic has been added to `Client::send`
- Exponential backoff, starting at 200 ms
- Now only retries on 502, 503 and 504 responses
- The `max_retries` option was added to `ClientConfig` (defaults to 3)
- 4 new tests

## Details

One of the most important aspects of this change is that it is very careful about which requests are retried. In order to avoid duplicate side effects, POST requests are not retried at all. Retries are only performed for responses that are likely to be transient in nature.

It should be noted that the backoff doubles on each attempt, so the delays are 200 ms, 400 ms and 800 ms respectively.

## Impact

This change should potentially reduce the number of failed requests that users see quite significantly.

Closes #142.

In summary, this PR makes the HTTP client more robust and resilient by adding retries with exponential backoff for transient errors.
EOF
