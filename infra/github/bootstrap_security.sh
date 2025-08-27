#!/usr/bin/env bash
set -euo pipefail

REPO="${REPO:-tapish331/VaayuTrade}"

echo "Enabling Advanced Security features on $REPO ..."
gh api -X PATCH "repos/${REPO}" \
  -F "security_and_analysis[advanced_security][status]=enabled" \
  -F "security_and_analysis[dependabot_alerts][status]=enabled" \
  -F "security_and_analysis[dependabot_security_updates][status]=enabled" \
  -F "security_and_analysis[secret_scanning][status]=enabled" \
  -F "security_and_analysis[secret_scanning_push_protection][status]=enabled"

echo "Protecting main branch with required reviews and status checks ..."
# Adjust required status checks below to match CI job names if different
jq -n '{
  required_status_checks: {
    strict: true,
    contexts: [
      "CodeQL",
      "CI"   # replace with actual CI check name if needed (from Task 04)
    ]
  },
  enforce_admins: true,
  required_pull_request_reviews: {
    required_approving_review_count: 1,
    require_code_owner_reviews: true,
    dismiss_stale_reviews: false
  },
  restrictions: null,
  allow_force_pushes: false,
  allow_deletions: false,
  required_linear_history: true
}' > /tmp/protection.json

gh api -X PUT "repos/${REPO}/branches/main/protection" \
  --header "Accept: application/vnd.github+json" \
  --input /tmp/protection.json

echo "Done. Verify branch protection and security settings in repository settings."
