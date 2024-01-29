job "blockbot" {
  datacenters = ["aperture"]
  type        = "service"

  meta {
    git_sha = "[[.git_sha]]"
  }

  group "blockbot" {
    count = 1

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
DEBUG=false
EOF
        destination = "local/.env"
        env         = true
      }
    }
  }
}
