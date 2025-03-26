job "blockbot-[[.environment_slug]]" {
  datacenters = ["aperture"]
  type        = "service"

  meta {
    git_sha = "[[.git_sha]]"
  }

  group "blockbot" {
    count = 1
    network {
      port "db" {
        to = 5432
      }
    }

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
DEBUG=true

LDAP_USERNAME={{ key "blockbot-dev/ldap/username" }}
LDAP_PASSWORD={{ key "blockbot-dev/ldap/password" }}
DISCORD_UID_MAP={{ key "blockbot-dev/discord/uid_map" }}

AGENDA_TEMPLATE_URL={{ key "blockbot-dev/agenda/template_url" }}

DB_HOST={{ env "NOMAD_ADDR_db" }} # address and port
DB_NAME={{ key "blockbot-dev/db/name" }} # database name
DB_PASSWORD={{ key "blockbot-dev/db/password" }}
DB_USER={{ key "blockbot-dev/db/user" }}

RCON_HOST=vanilla-mc-rcon.service.consul
{{ range service "vanilla-mc-rcon" }}
RCON_PORT={{ .Port }}{{ end }}
RCON_PASSWORD={{ key "blockbot-dev/rcon/password" }}
EOF
        destination = "local/.env"
        env         = true
      }
    }
    task "blockbot-dev-db" {
      driver = "docker"

      config {
        image = "postgres:17-alpine"
        ports = ["db"]

        volumes = [
          "/storage/nomad/blockbot-dev/db:/var/lib/postgresql/data",
        ]
      }

      template {
        data        = <<EOH
POSTGRES_PASSWORD={{ key "blockbot-dev/db/password" }}
POSTGRES_USER={{ key "blockbot-dev/db/user" }}
POSTGRES_NAME={{ key "blockbot-dev/db/name" }}
EOH
        destination = "local/db.env"
        env         = true
      }
    }
  }
}
