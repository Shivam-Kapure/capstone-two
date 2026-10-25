# Progress — capstone-two (D:\claude-two)

Fresh build, separate from the finished capstone in `D:\claude study` (left untouched).
Naming: images `*:capstone-two`, containers `capstone-two-*` / `payment-live-two`, Minikube profile `capstone-two`,
Jenkins job `capstone-two-pipeline`, GitHub repo `capstone-two`, ports 38180/38181/30199.

## Phase 0 — audit (read-only) — PASS
- `D:\claude-two` existed, empty, not inside a Git repo (`git status` exit 128).
- Python 3.12.4, Docker 29.7.2, Compose v5.4.0, kubectl v1.36.1, minikube v1.39.0 (`MINIKUBE_HOME=D:\minikube-home`), Terraform v1.16.6, Java 25.0.3.
- WSL: Ubuntu (WSL 2, stopped) has ansible core 2.16.3; pip3 missing; sudo needs a password.
- Jenkins 2.572 at localhost:8080 (HTTP 200), service `Jenkins` Running as LocalSystem; earlier job `capstone-simple-pipeline` #1 ran `docker build` → SUCCESS.
- Kube current context `minikube` (left unchanged). Minikube profiles: `capstone-simple`, `minikube` (both stopped).
- Free RAM 2.8 GB of 15.3 GB; Docker VM 12 CPUs / 7.4 GiB.
- Ports: see PORTS.md.

## Phase 1 — files — PASS
All files created in `D:\claude-two` (see structure in the final report).

## Phase 2 — local verification — PASS
- `python -m venv .venv` + `pip install -r backend\requirements-dev.txt` → exit 0; `pytest -v` → **9 passed** (exit 0).
- Jenkins Build & Test lines run in `cmd` (with `|| exit /b 1`) → 9 passed, exit 0; `.ci-venv` removed afterwards.
- `docker build -t payment-engine:capstone-two .` → exit 0. `docker run -d --name payment-live-two payment-engine:capstone-two` →
  status `Exited (0)`, `docker logs payment-live-two` → `Payment Gateway Running`.
- `docker compose up -d --build` → exit 0; `capstone-two-backend` healthy on 38181, `capstone-two-frontend` healthy on 38180.
- Through `http://localhost:38180`: `/health` 200 `{"status":"healthy","version":"1.0.0"}`; `/api/payments` 200 (3 seeds);
  valid POST → 201 (id 4); invalid POST → 422 with 3 field errors; `/api/payments/999` → 404 `{"detail":"Payment 999 not found"}`;
  `/api/notifications` newest first.
- Built-in browser at `http://localhost:38180`: badge "Backend healthy · v1.0.0"; form submit → "Payment #5 created.", row #5 and its
  notification appear, stats total 5.

## Phase 3 — Minikube — PASS
- `minikube start -p capstone-two --driver=docker --cpus=2 --memory=2048 --keep-context` → exit 0; node `capstone-two` Ready,
  v1.37.0, containerd, IP 192.168.76.2. Default context still `minikube` (unchanged).
- `minikube -p capstone-two image load payment-backend:capstone-two` / `payment-frontend:capstone-two` → exit 0; both listed by `image ls`.
- NodePort 30199: no Service in the cluster uses it.
- `kubectl --context capstone-two apply --dry-run=server -f capstone-stack.yaml` → 4 resources "created (server dry run)", exit 0.
- After user approval: `apply` → 4 resources created, exit 0; `rollout status` → both deployments "successfully rolled out", exit 0.
- `get deployments` → capstone-deployment 2/2, capstone-frontend 1/1; 3 pods Running, 0 restarts.
- `get svc` → capstone-backend ClusterIP 8000; capstone-nodeport NodePort `80:30199`. EndpointSlices: backend 10.244.0.3,10.244.0.5:8000;
  nodeport 10.244.0.4:80. `get all -l tier=backend` → 2 pods, service, deployment, replicaset.
- Backend logs: uvicorn on 0.0.0.0:8000, `GET /health 200` probes. Frontend pod: `BACKEND_URL=http://capstone-backend:8000`,
  rendered nginx `proxy_pass http://capstone-backend:8000;`.
- NodePort: `minikube -p capstone-two ssh -- curl http://192.168.76.2:30199/health` → `{"status":"healthy",...}` HTTP 200; `/` HTTP 200.
  From Windows, `curl http://localhost:30199/health` → HTTP 000 / exit 7 (expected — Docker-driver node ports aren't published to the host).
- Tunnel: `minikube -p capstone-two service capstone-nodeport --url` (background) → `http://127.0.0.1:63152` (owner: ssh.exe).
  `/` 200, `/health` 200, `/api/payments` 200, POST 201 (id 4); 5 repeated GETs all return 4 payments (ClientIP affinity works).
- Built-in browser at the tunnel URL: form submit → payment #5 "Cluster Browser → Bakery", still present after page reload; badge healthy.
- Default kubectl context still `minikube`.

## Phase 5a — Git (run by user, verified read-only) — PASS
- Remote `origin` = `https://github.com/Shivam-Kapure/capstone-two.git`.
- `git log --oneline --graph --all --decorate` → `8c002c3 (HEAD -> main, tag: v1.0.0-final, origin/release-v1.0, origin/main, release-v1.0)
  chore: finalize release v1.0` on top of `bd1af88 feat: payment and notification engine ...` (fast-forward merge, linear).
- `git branch -a -vv` → main tracks origin/main; release-v1.0 and origin/release-v1.0 at 8c002c3.
- `git tag -n` → `v1.0.0-final    Final Capstone Release`; `git cat-file -t v1.0.0-final` → `tag` (annotated).
- `git ls-remote --heads --tags origin` → heads main and release-v1.0 at 8c002c3; tag object 81e0a4f peeling to 8c002c3; exit 0.
- `git status` → clean, up to date with origin/main. 25 tracked files (24 + version.txt = `v1.0-prod-bundle`);
  no capstone.env, tfstate, .terraform/ or .venv/ tracked.

## Phase 5b — Jenkins `capstone-two-pipeline` build #1 (created and triggered by user) — PASS
Read from `C:\ProgramData\Jenkins\.jenkins\jobs\capstone-two-pipeline\builds\1\log`:
- Checkout SCM: revision `8c002c3` (refs/remotes/origin/main), "chore: finalize release v1.0".
- Build & Test: venv + pip install + pytest, each line with `|| exit /b 1` → `collected 9 items`, **`9 passed`**, then
  `Building Payment and Notification Services... Test PASSED`.
- Docker Packaging: `docker build -t payment-engine:capstone-two .`, `payment-backend:capstone-two backend`,
  `payment-frontend:capstone-two frontend`; inspect printed `Image [payment-engine:capstone-two] sha256:64f86cdf…`,
  `Image [payment-backend:capstone-two] sha256:02c26777…`, `Image [payment-frontend:capstone-two] sha256:af9af17a…`.
- Deploy Cluster: `Applying Kubernetes Deployment manifests to cluster...`.
- Post: `if exist .ci-venv rmdir /s /q .ci-venv` (workspace has no .ci-venv afterwards). **`Finished: SUCCESS`**.

## Phase 5c — Jira — PASS (user-reported)
- User reported: sprint with the 3 tasks completed, all moved to Done after evidence was verified, burndown/sprint report screenshot taken.
  Not observable from this machine.

## Phase 6 — final report — PASS
- Re-checked before writing: root Dockerfile byte-exact (52 bytes); Jenkinsfile 3 stages, 0 `sh`; manifest 4 resources;
  1 Terraform resource, `plan -detailed-exitcode` exit 0; Compose both healthy, `/health` 200; `payment-live-two` Exited (0);
  k8s 2/2 + 1/1 Running; tunnel 127.0.0.1:63152 `/health` 200; default context still `minikube`.
- Report: [FINAL_REPORT.md](FINAL_REPORT.md).

## Phase 4 — Terraform & Ansible — PASS
Terraform v1.16.6 (already installed via winget, on PATH):
- `terraform fmt -check` → exit 0; `init` → installed hashicorp/local v2.9.1, exit 0; `validate` → "The configuration is valid.", exit 0.
- `apply -auto-approve` → "Resources: 1 added", exit 0; `terraform state list` → `local_file.capstone_env` (only resource).
- `capstone.env` = 59 bytes, byte-identical to `PAYMENT_GATEWAY_URL=http://localhost:30199\nSTATUS=DEPLOYED\n` (LF endings).
- `plan -detailed-exitcode` → "No changes", exit 0.

Ansible core 2.16.3 in WSL Ubuntu (already installed, no sudo needed), via script `bash ansible-validate.sh` from `/mnt/d/claude-two`:
- `ansible localhost -m command -a "cat capstone.env" -c local` → rc=0, prints both lines.
- `ansible-playbook -i localhost, validate.yml --syntax-check` → exit 0.
- Real run (app_url `http://localhost:38180`) → `ok=12 changed=0 failed=0`, exit 0; 5 payments, healthy v1.0.0.
- Negative `-e app_url=http://localhost:38999` (port verified free) → `GET /health` FAILED "Connection refused", `failed=1`, exit 2 (expected).
