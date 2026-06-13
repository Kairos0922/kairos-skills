.PHONY: install test showcase clean

install:
	@echo "Checking Python version..."
	@python3 --version
	@echo "Running smoke test..."
	cd kairos-wechat-typeset && python3 scripts/check_all.py --smoke
	@echo "Running design system verification..."
	cd kairos-visual-generator && python3 scripts/verify_design_system.py
	@echo "Install check passed."

test:
	cd kairos-wechat-typeset && python3 scripts/check_all.py
	cd kairos-visual-generator && python3 scripts/verify_design_system.py
	python3 -m json.tool skills.json > /dev/null
	@echo "All tests passed."

showcase:
	cd kairos-wechat-typeset && python3 scripts/render.py --theme song --input fixtures/song-style-system.md --output goldens/song-style.html
	cd kairos-wechat-typeset && python3 scripts/render.py --theme wending --input fixtures/wending-style-system.md --output goldens/wending-style.html
	cd kairos-wechat-typeset && python3 scripts/render.py --theme tech --input fixtures/tech-style-system.md --output goldens/tech-style.html
	cd kairos-wechat-typeset && python3 scripts/render.py --theme wisme --input fixtures/wisme-style-system.md --output goldens/wisme-style.html
	@echo "Golden files regenerated."

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "Cleaned."
