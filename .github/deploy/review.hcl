job "blockbot-[[.environment_slug]]" {
  datacenters = ["aperture"]
  type        = "service"

  meta {
    git_sha = "[[.git_sha]]"
  }

  group "blockbot" {
    count = 1

    task "blockbot-review-[[.git_sha]]" {
      driver = "docker"

      config {
        image = "ghcr.io/redbrick/blockbot:sha-[[.git_sha]]"
      }

      resources {
        cpu    = 500
        memory = 256
      }

      template {
        data        = <<EOF
TOKEN={{ key "blockbot-dev/discord/token" }}
DEBUG=false
LDAP_USERNAME={{ key "blockbot-dev/ldap/username" }}
LDAP_PASSWORD={{ key "blockbot-dev/ldap/password" }}
DISCORD_UID_MAP={{ key "blockbot-dev/discord/uid_map" }}
EOF
        destination = "local/.env"
        env         = true
      }
    }
  }
}
