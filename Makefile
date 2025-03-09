ANTLR4=antlr4

SRCDIR=src
PARSERDIR=$(SRCDIR)/libs

PARSER_FILES=SubC.interp SubC.tokens SubCLexer.interp subclexer.rs SubCLexer.tokens \
	subclistener.rs subcparser.rs

all: SubC.g4
	$(ANTLR4) -o $(PARSERDIR) -Dlanguage=Rust $<

clean:
	@rm -f $(addprefix $(PARSERDIR)/,$(PARSER_FILES))

.PHONY: clean
