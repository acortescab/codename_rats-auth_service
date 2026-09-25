set -e

mkdir -p ~/codename_rats-auth_service
cd ~/codename_rats-auth_service

aws ecr get-login-password --region eu-west-1 | docker login --username AWS --password-stdin "$ECR_REGISTRY"

# backup
if [ -f docker-compose-prod.yml ] && [ -f .current-image-tag ]; then
  BACKUP_DIR="backups"
  mkdir -p "$BACKUP_DIR"
  BACKUP_FILE="$BACKUP_DIR/db_backup_$(date +%s).sql"
  echo "Creating database backup at $BACKUP_FILE"
  if docker compose -f docker-compose-prod.yml exec -T db pg_dump -U "$DB_USER" -d "$DB_NAME" > "$BACKUP_FILE" 2>/dev/null; then
    echo "$BACKUP_FILE" > .last-backup-file
  fi
fi

echo "$IMAGE_TAG" > .current-image-tag
echo "Info: Downloading latest docker-compose-prod.yml"

curl -fsSL "https://raw.githubusercontent.com/acortescab/codename_rats-auth_service/refs/heads/main/docker-compose-prod.yml" -o docker-compose-prod.yml
docker compose -f docker-compose-prod.yml up -d