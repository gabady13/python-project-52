#!/usr/bin/env bash
set -e

# скачать uv
curl --proto '=https' --tlsv1.2 -LsSf https://astral.sh/uv/install.sh -o install_uv.sh

# выполнить установку
sh install_uv.sh

# добавить uv в PATH
source "$HOME/.local/bin/env"

# установка зависимостей и миграции
make install
make collectstatic
make migrate