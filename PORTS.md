# Ports — capstone-two

Checked with `Get-NetTCPConnection -State Listen -LocalPort <p>` and `docker ps -a` port bindings on 2026-10-25.

| Port | Status when checked | Owner | Purpose in this project |
|---|---|---|---|
| 80 | free | – | Not used on the host (nginx listens on 80 only inside the container) |
| 8000 | free | – | Not used on the host (uvicorn listens on 8000 only inside the container) |
| 8080 | **in use** | `java` pid 5392 = Jenkins service | Jenkins UI (existing, untouched) |
| 30099 | free | – | Reserved by the earlier `D:\claude study` capstone (`capstone-simple` profile); not used here |
| 38080 / 38081 | free | – | Reserved by the earlier `D:\claude study` compose stack; not used here |
| **38180** | free | capstone-two | Compose frontend `capstone-two-frontend` → container 80 |
| **38181** | free | capstone-two | Compose backend `capstone-two-backend` → container 8000 |
| **30199** | free | capstone-two | NodePort `capstone-nodeport` inside Minikube profile `capstone-two` (node IP only) |
| 38999 | free | – | Deliberately unused; target of the Ansible negative test |
| random 127.0.0.1 port (63152 this run) | in use while tunnel runs | `ssh.exe` started by `minikube service --url` | Windows/Docker-driver tunnel to the NodePort (changes every run) |
