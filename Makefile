ANTLR4=antlr4

SRCDIR=src
PARSERDIR=$(SRCDIR)/libs

PARSER_FILES=C.interp C.tokens CLexer.interp clexer.rs CLexer.tokens \
	clistener.rs cparser.rs

all: C.g4
	$(ANTLR4) -o $(PARSERDIR) -Dlanguage=Rust $<

clean:
	@rm -f $(addprefix $(PARSERDIR)/,$(PARSER_FILES))

.PHONY: clean
