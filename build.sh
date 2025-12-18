#!/usr/bin/env bash
# скачиваем uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env

# команду установки зависимостей, сборки статики, применения миграций и другие
make install && make collectstatic && make migrate