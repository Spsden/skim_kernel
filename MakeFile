.SILENT:


help:
	echo "Available commands:"
	echo ""
	awk 'BEGIN {FS=":.*##"} \
	/^[a-zA-Z_-]+:.*##/ { printf "  %-20s %s\n", $$1, $$2 }' $(MAKEFILE_LIST)


## Format code
fmt: ## Format python code using black
	uv run ./scripts/format_code.py

## Generate DB migrations (usage: make gen-db NAME="desc")
gen-db: ## Generate alembic migration
	alembic revision --autogenerate -m "$(NAME)"

## Apply DB migrations
apply-db: ## Apply latest database migrations
	alembic upgrade head

## Generate requirements.txt
gen-req: ## Generate requirements.txt from uv environment
	uv pip freeze > requirements.txt
 
## Create Python virtual environment
create_venv: ## Create virtual environment using uv
	uv venv

## Run RSS feed service
run-rss: ## Run RSS feed service (kalinga)
	uv run ./main.py kalinga

## Run scraping service
run-scrap: ## Run scraping service (bundelkhand)
	uv run ./main.py bundelkhand

## Run summarization service
run-summ: ## Run summarization service (amarkantak)
	uv run ./main.py amarkantak

## Run all services
run-all: ## Run all services together (mahabharat)
	uv run ./main.py mahabharat





# # .SILENT:

# help:



# # to  generate migrations
# #  param Name for migration desc
# gen-db:
# 	alembic revision --autogenerate -m "$(NAME)"
	

# # to apply migrations 
# apply-db:
# 	alembic upgrade head
	

# # to generate requirements 
# gen-req:
# 	uv pip freeze > requirements.txt

# # create virtual environment for python
# create_venv:
# 	uv venv


# # run rss-feed service
# run-rss:
# 	uv run ./main.py kalinga

# # run scraping service
# run-scrap:
# 	uv run ./main.py bundelkhand

# # run summarization service
# run-summ:
# 	uv run ./main.py amarkantak

# # run all services at ones
# run-all:
# 	uv run ./main.py mahabharat


