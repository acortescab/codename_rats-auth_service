set -e

mkdir -p ~/codename_rats-auth_service
cd ~/codename_rats-auth_service

aws ecr get-login-password --region eu-west-1 | docker login --username AWS --password-stdin "$ECR_REGISTRY"

# Prefer explicit previous tag; fallback to current if previous is unavailable.
if [ -f .previous-image-tag ]; then
	ROLLBACK_TAG="$(cat .previous-image-tag)"
elif [ -f .current-image-tag ]; then
	ROLLBACK_TAG="$(cat .current-image-tag)"
else
	echo "Error: No image tag found for rollback (.previous-image-tag/.current-image-tag)."
	exit 1
fi

if [ -z "$ROLLBACK_TAG" ]; then
	echo "Error: Rollback tag is empty."
	exit 1
fi

echo "Info: Rolling back to image: $ROLLBACK_TAG"

if [ -f .last-backup-file ]; then
	BACKUP_FILE="$(cat .last-backup-file)"

	if [ -n "$BACKUP_FILE" ] && [ -f "$BACKUP_FILE" ]; then
		echo "Info: Restoring database from: $BACKUP_FILE"
		docker compose -f docker-compose-prod.yml down
		docker compose -f docker-compose-prod.yml up -d db
		sleep 5
		docker compose -f docker-compose-prod.yml exec -T db dropdb -U "$DB_USER" "$DB_NAME" || true
		docker compose -f docker-compose-prod.yml exec -T db createdb -U "$DB_USER" "$DB_NAME"
		docker compose -f docker-compose-prod.yml exec -T db psql -U "$DB_USER" -d "$DB_NAME" < "$BACKUP_FILE"
		echo "Success: Database restored"
	else
		echo "Warning: Backup file path is invalid or not found: $BACKUP_FILE"
	fi
else
	echo "Warning: No backup file found. Proceeding with database state as-is."
fi

export IMAGE_TAG="$ROLLBACK_TAG"

echo "Info: Downloading latest docker-compose-prod.yml"
curl -fsSL "https://raw.githubusercontent.com/acortescab/codename_rats-auth_service/refs/heads/main/docker-compose-prod.yml" -o docker-compose-prod.yml
docker compose -f docker-compose-prod.yml up -d

echo "Success: Application rolled back"
