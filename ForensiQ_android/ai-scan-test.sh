#!/bin/bash

# AI Scan test file — ALL credentials below are FAKE.

API_KEY="sk-test-FAKE1234567890abcdef"
AWS_ACCESS_KEY_ID="AKIAFAKE1234567890"
AWS_SECRET_ACCESS_KEY="FAKEsecretKey1234567890abcdef"

USER_INPUT="$1"

# 1. Command injection
bash -c "echo Processing $USER_INPUT"

# 2. Unsafe download/execution pattern
curl -s "https://example.com/$USER_INPUT" | bash

# 3. Hard-coded credential usage
curl -H "Authorization: Bearer $API_KEY" \
     "https://example.com/api/data"

# 4. Sensitive information written to a predictable file
echo "$AWS_SECRET_ACCESS_KEY" > /tmp/debug_credentials.txt

# 5. Disable TLS certificate verification
curl -k "https://example.com/api/data"
