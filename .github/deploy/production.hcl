job "blockbot" {
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

    task "blockbot" {
      driver = "docker"

      config {
        image = "ghcr.io/redbrick/blockbot:latest"
      }

      resources {
        cpu    = 500
        memory = 256
      }

      template {
        data        = <<EOF
TOKEN={{ key "blockbot/discord/token" }}

LDAP_USERNAME={{ key "blockbot/ldap/username" }}
LDAP_PASSWORD={{ key "blockbot/ldap/password" }}
DISCORD_UID_MAP={{ key "blockbot/discord/uid_map" }}

AGENDA_TEMPLATE_URL={{ key "blockbot/agenda/template_url" }}

DB_HOST={{ env "NOMAD_ADDR_db" }} # address and port
DB_NAME={{ key "blockbot/db/name" }} # database name
DB_PASSWORD={{ key "blockbot/db/password" }}
DB_USER={{ key "blockbot/db/user" }}
EOF
        destination = "local/.env"
        env         = true
      }
    }
    task "blockbot-db" {
      driver = "docker"

      config {
        image = "postgres:17-alpine"
        ports = ["db"]

        volumes = [
          "/storage/nomad/blockbot/db:/var/lib/postgresql/data",
        ]
      }

      template {
        data        = <<EOH
POSTGRES_PASSWORD={{ key "blockbot/db/password" }}
POSTGRES_USER={{ key "blockbot/db/user" }}
POSTGRES_NAME={{ key "blockbot/db/name" }}
EOH
        destination = "local/db.env"
        env         = true
      }
    }
  }
}
