set -euo pipefail

cd "$HOME/agentic-chatbot"
test -f .env || { echo "Missing $HOME/agentic-chatbot/.env" >&2; exit 1; };

DOCKER_CONFIG="$(mktemp -d)"
export DOCKER_CONFIG
trap 'rm -f "$DOCKER_CONFIG/config.json"; rmdir "$DOCKER_CONFIG"' EXIT

printf '%s' "$GHCR_TOKEN" | docker login ghcr.io --username "$GHCR_USERNAME" --password-stdin
unset GHCR_TOKEN

APP_IMAGE="$IMAGE" docker compose pull app
APP_IMAGE="$IMAGE" docker compose up --detach --no-build --pull never --remove-orphans --wait --wait-timeout 300
