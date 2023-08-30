SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c


streamlit-dev:
	poetry run streamlit run streamlit_app.py