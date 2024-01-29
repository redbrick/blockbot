#!/usr/local/bin/bash

echo "${GITHUB_SHA}"
echo "${GITHUB_REF_NAME}"

levant deploy \
  -var git_sha="${GITHUB_SHA}" \
  -var environment_slug="${GITHUB_REF_NAME}" \
  -address "http://nomad.service.consul:4646" \
  tools/templates/blockbot-review.hcl
