#!/usr/local/bin/bash

levant deploy \
  -var git_sha="${GITHUB_SHA}" \
  -address "http://nomad.service.consul:4646" \
  tools/templates/blockbot-prod.hcl
