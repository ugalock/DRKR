#!/bin/bash

echo "Applying Alembic migrations..."
alembic upgrade head
echo "Database migration complete!"