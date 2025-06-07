PIP3=pip3
ANTLR4=antlr4

PARSERDIR=libs

PARSER_FILES=SubC.interp SubC.tokens SubCLexer.interp subclexer.rs SubCLexer.tokens \
	subclistener.rs subcparser.rs SubCLexer.py SubCListener.py SubCParser.py

TESTSDIR=tests
TESTS=LUTBasicDirectivesTestCase TranslatorBasicTestCase \
	EnumsDeclarationsAndDefinitionsTestCase \
	UnionsOrStructsDeclarationsAndDefinitionsTestCase \
	FunctionsDeclarationsTestCase FunctionDefinitionsTestCase \
	AssignmentsTestCase BranchingTestCase ExpressionsTestCase \
	LoopsTestCase

all: SubC.g4
	$(ANTLR4) -o $(PARSERDIR) -Dlanguage=Python3 $<

update-deps:
	pip3 freeze > ./requirements.txt

test: $(TESTS)

$(TESTS):
	python3 -m unittest $(addsuffix .py,$(addprefix $(TESTSDIR)/,$@))

clean:
	@rm -f $(addprefix $(PARSERDIR)/,$(PARSER_FILES))

clean-junk:
	@rm -rf ./__pycache__
	@rm -rf $(PARSERDIR)/__pycache__
	@rm -rf tests/__pycache__
	@rm -rf listeners/__pycache__

.PHONY: clean update-requirements clean-junk test $(TESTS)
