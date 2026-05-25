variable "aws_access_key" { type = string }
variable "aws_secret_key" { type = string }

provider "aws" {
  region     = "eu-central-1"
  access_key = var.aws_access_key
  secret_key = var.aws_secret_key
}

variable "instance_count" {
  type    = number
  default = 1
}

variable "bots_per_instance" {
  type    = string
  default = "1"
}


variable "bbb_url" { type = string }
variable "bbb_secret" { type = string }
variable "video_url"      { type = string }

variable "docker_image" {
  type    = string
  default = "knsz/bbb-bot:latest" # Obraz z Docker Hub - można budować samodzielnie, źródła też dodaje
}

# --- SECURITY GROUP (Firewall) ---
resource "aws_security_group" "allow_ssh_bot" {
  name        = "bbb_stress_sg"
  description = "Pozwol na SSH i ruch wychodzacy"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

variable "instance_type" {
  type    = string
  default = "c5.2xlarge"
}

# --- INSTANCJE SPOT (Tanie serwery) ---
resource "aws_spot_instance_request" "bot_cluster" {
  count = var.instance_count

  # Ubuntu 24.04 LTS (x86_64) w regionie eu-central-1
  ami           = "ami-0084a47cc718c111a"


  instance_type = var.instance_type # Mapowanie zmiennej do atrybutu

  # Cena maksymalna. Jeśli cena rynkowa skoczy powyżej, AWS wyłączy maszynę.
  spot_price           = "10.40"
  wait_for_fulfillment = true
  spot_type            = "one-time"

  security_groups = [aws_security_group.allow_ssh_bot.name]

  # TU WPISZ NAZWĘ KLUCZA, KTÓRY STWORZYŁEŚ W KROKU 1
  key_name        = "bbb-test-key"

  # Skrypt startowy (uruchamia się sam po starcie maszyny)
  user_data = <<-EOF
              #!/bin/bash
              # 1. Instalacja narzędzi
              apt-get update
              apt-get install -y docker.io ffmpeg wget python3

              # 2. Przygotowanie mediów
              mkdir -p /home/ubuntu/media
              cd /home/ubuntu/media
              wget "${var.video_url}" -O input.mp4
              ffmpeg -i input.mp4 -pix_fmt yuv420p -r 24 -s 1280x720 video.y4m

              # 3. Skrypt DASHBOARDU (Generuje HTML co 5 sekund)
              cat << 'DASH' > /home/ubuntu/monitor.sh
              while true; do
                {
                  echo "<html><head><meta http-equiv='refresh' content='5'><style>body{font-family:monospace;background:#121212;color:#00ff00;padding:20px;}pre{background:#000;padding:15px;border:1px solid #333;border-radius:5px;overflow:auto;}h2{color:#fff;border-bottom:1px solid #333;}</style></head><body>"
                  echo "<h1>🚀 Serwer: $(hostname) | IP: $(curl -s ifconfig.me)</h1>"
                  echo "<h2>📈 ZUŻYCIE SYSTEMU</h2><pre>$(top -b -n 1 | head -n 5)</pre>"
                  echo "<h2>🐳 STATYSTYKI DOCKERA (Wszystkie kontenery)</h2><pre>$(docker stats --no-stream)</pre>"
                  echo "<h2>📋 OSTATNIE LOGI (bbb-stress-test)</h2><pre>$(docker logs --tail 50 bbb-stress-test 2>&1)</pre>"
                  echo "</body></html>"
                } > /home/ubuntu/index.html
                sleep 5
              done
              DASH

              # 4. Start usług monitorujących w tle
              chmod +x /home/ubuntu/monitor.sh
              nohup bash /home/ubuntu/monitor.sh &
              nohup python3 -m http.server 8080 --directory /home/ubuntu &

              # 5. Uruchomienie bota
              docker run -d \
                --restart always \
                --network host \
                --name bbb-stress-test \
                -v /home/ubuntu/media:/app/media \
                -e BBB_URL="${var.bbb_url}" \
                -e BBB_SECRET="${var.bbb_secret}" \
                -e BOTS="${var.bots_per_instance}" \
                -e DURATION="3600" \
                ${var.docker_image}
              EOF
}

output "monitoring_links" {
  description = "Links to monitoring dashboards"
  value       = [for ip in aws_spot_instance_request.bot_cluster[*].public_ip : "http://${ip}:8080"]
}