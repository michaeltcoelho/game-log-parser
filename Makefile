
.PHONY: install
install:
	@pip install -r requirements.txt

.PHONY: server
server:
	@python api.py

.PHONY: test
test:
	@pytest -s
