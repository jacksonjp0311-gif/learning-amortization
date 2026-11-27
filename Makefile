.PHONY: all test example paper markdown clean
all: test example paper markdown

test:
	python -m pytest -q

example:
	python examples/synthetic_toy.py --figure paper/figures/synthetic_curve.pdf
	pdftoppm -png -r 150 -singlefile paper/figures/synthetic_curve.pdf paper/figures/synthetic_curve

paper:
	cd paper && latexmk -pdf -interaction=nonstopmode -halt-on-error whitepaper.tex

markdown: paper
	python scripts/build_markdown.py

clean:
	cd paper && latexmk -C whitepaper.tex
