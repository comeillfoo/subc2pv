ANTLR4=antlr4

SRCDIR=src/

PARSER_FILES=C.interp C.tokens CLexer.interp clexer.rs CLexer.tokens \
	clistener.rs cparser.rs

all: C.g4
	$(ANTLR4) -o $(SRCDIR) -Dlanguage=Rust $<

clean:
	@rm -f $(addprefix $(SRCDIR),$(PARSER_FILES))

.PHONY: clean
