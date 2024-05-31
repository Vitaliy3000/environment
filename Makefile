test:
	poetry run pytest blanks/http_client/unit_test.py
	poetry run pytest blanks/http_server/unit_test.py
	poetry run pytest blanks/postgres_client/functional_test.py