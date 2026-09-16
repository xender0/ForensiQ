"""
SECRET SCANNING TEST FIXTURE — DO NOT DEPLOY. DO NOT COPY INTO REAL CODE.

Purpose: verify GitHub secret scanning and push protection behaviour on a
disposable test repository.

Every value in this file is either fabricated or (for BLOCK B) a token you
created with zero scopes. Nothing here grants access to anything.

Commit this on a throwaway branch, record the results, then close the PR and
delete the branch. This file must never reach a default branch of a real repo.

Suggested path: security-tests/secret_scanning_fixture.py
"""

# ---------------------------------------------------------------------------
# BLOCK A — Partner-pattern shaped, fabricated
#
# These have the right prefix and length but are invented, so they will not
# pass a provider validity check. Outcome is genuinely uncertain: GitHub may
# raise an alert and mark it inactive, or may not raise one at all. That
# uncertainty is the point — it shows you how much detection depends on the
# credential being live.
# ---------------------------------------------------------------------------

# AWS's own published documentation placeholder. Widely allowlisted precisely
# because it appears in millions of docs pages. Expect: no alert.
AWS_ACCESS_KEY_ID_DOCS_EXAMPLE = "AKIAIOSFODNN7EXAMPLE"

# Same shape, not a known docs string. Expect: possibly an alert, marked
# inactive. Compare against the line above.
AWS_ACCESS_KEY_ID_FABRICATED = "AKIA4XQ2ZJ7HTVBW9RKD"

# Stripe test-mode key shape. Test keys are non-production by definition.
STRIPE_TEST_KEY = "sk_test_51HqL8vF2mNpQrStUvWxYz0123456789abcdefgh"

# Fabricated private key. The BEGIN header is itself a detected pattern, so
# this one may fire on the header alone despite the body being nonsense.
FAKE_PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
Tk9UQVJFQUxLRVlUSElTSVNBVEVTVEZJWFRVUkVGT1JTRUNSRVRTQ0FOTklORw==
-----END RSA PRIVATE KEY-----"""


# ---------------------------------------------------------------------------
# BLOCK B — Positive control (you must supply this)
#
# This is the only value expected to reliably trigger both push protection and
# a secret scanning alert, because GitHub validates its own tokens.
#
# Generate at: Settings > Developer settings > Personal access tokens >
#              Tokens (classic) > Generate new token
#
#   - Check NO scope boxes. None. An unscoped token grants nothing beyond
#     anonymous access.
#   - Set expiry to 7 days.
#   - Paste below, run the test, then delete the token.
#
# GitHub auto-revokes its own leaked tokens on detection, so this one may die
# on its own. Watching that happen is the clearest demo of why this matters.
# ---------------------------------------------------------------------------

GITHUB_TOKEN = "ghp_REPLACE_WITH_YOUR_ZERO_SCOPE_TOKEN"


# ---------------------------------------------------------------------------
# BLOCK C — Negative control: generic secrets
#
# No provider prefix, no fixed length, no checksum. Detecting these requires
# AI-powered generic secret detection, which is in the paid Secret Protection
# tier. On a free public repo, expect ZERO alerts for this entire block.
#
# This is the important half of the test. These are the shape most real leaks
# actually take — internal service tokens, DB passwords, homegrown auth
# strings — and partner-pattern scanning is blind to all of them.
#
# An AI code reviewer reading the diff should flag every line below. That
# contrast is a direct argument for the reviewer pilot.
# ---------------------------------------------------------------------------

DB_PASSWORD = "SuperSecret123!"
API_KEY = "abc123xyz789"
INTERNAL_SERVICE_TOKEN = "prod-svc-auth-8f3a9c2b"
ADMIN_OVERRIDE = "letmein"

# Credential embedded in a connection string — very common real-world shape.
DATABASE_URL = "postgres://svc_user:Hunter2Password@db.internal.example:5432/app"

# Basic auth in a URL.
WEBHOOK_URL = "https://apiuser:s3cr3tvalue@hooks.example.internal/notify"

# Base64-wrapped credential. Encoding is not protection, but it does defeat
# naive pattern matching.
ENCODED_CREDS = "YWRtaW46U3VwZXJTZWNyZXQxMjMh"  # admin:SuperSecret123!


# ---------------------------------------------------------------------------
# RESULTS — fill this in as you go
#
#   Block  Value                          Push blocked?   Alert raised?
#   -----  -----------------------------  -------------   -------------
#   A      AWS docs example               [ ]             [ ]
#   A      AWS fabricated                 [ ]             [ ]
#   A      Stripe test key                [ ]             [ ]
#   A      Fake private key               [ ]             [ ]
#   B      Zero-scope GitHub PAT          [ ]             [ ]
#   C      All generic secrets            [ ]             [ ]
#
# Test both commit paths, they behave differently:
#   1. Web UI editor  — inline warning in the commit dialog
#   2. git push        — rejection in the terminal with a bypass URL
#
# The terminal path is what your developers will actually hit, so that error
# text is worth reading once before anyone asks you about it.
#
# CLEANUP
#   [ ] Delete the PAT from Developer settings
#   [ ] Close the PR, delete the branch
#   [ ] Add .env, *.pem, *.key to .gitignore
# ---------------------------------------------------------------------------
