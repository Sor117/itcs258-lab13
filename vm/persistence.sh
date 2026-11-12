cd ~/apps/gacha-workshop
FILES="--env-file .env -f compose.yml -f compose.production.yml -f compose.proxy.yml"
BEFORE=$(sudo docker compose $FILES ps -q app)
echo "BEFORE=$BEFORE"
sudo docker compose $FILES up -d --force-recreate --wait app
AFTER=$(sudo docker compose $FILES ps -q app)
echo "AFTER=$AFTER"
sudo docker volume ls --format '{{.Name}}' | grep pgdata
echo "HISTORY:"
curl -s http://localhost/backend/api/accounts/6788117/history
echo
