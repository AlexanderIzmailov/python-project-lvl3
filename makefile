install:
	poetry install

page-loader:
	poetry run page-loader

build:
	poetry build

publish:
	poetry publish --dry-run

package-install:
	python3 -m pip install --user dist/*.whl

lint:
	poetry run flake8 page_loader

test:
	poetry run pytest

test-cov:
	poetry run pytest --cov=page-loader --cov-report xml tests/