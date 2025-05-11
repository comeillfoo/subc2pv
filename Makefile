PIP3=pip3
ANTLR4=antlr4

PARSERDIR=libs

PARSER_FILES=SubC.interp SubC.tokens SubCLexer.interp subclexer.rs SubCLexer.tokens \
	subclistener.rs subcparser.rs

all: SubC.g4
	$(ANTLR4) -o $(PARSERDIR) -Dlanguage=Python3 $<

update-deps:
	pip3 freeze > ./requirements.txt

clean:
	@rm -f $(addprefix $(PARSERDIR)/,$(PARSER_FILES))

.PHONY: clean update-requirements
