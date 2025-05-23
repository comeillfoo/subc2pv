grammar SubC;

// Parser rules
compilationUnit
    : declarationOrDefinition* EOF
    ;

declarationOrDefinition
    : enumDeclaration
    | enumDefinition
    | structOrUnionDeclaration
    | structOrUnionDefinition
    | functionDeclaration
    | functionDefinition
    ;

enumDeclaration
    : 'enum' Identifier ';'
    ;

enumDefinition
    : 'enum' Identifier '{' enumerator (',' enumerator)* ','? '}' ';'
    ;

enumerator
    : Identifier ('=' Constant)?
    ;

structOrUnion
    : 'struct'
    | 'union'
    ;

structOrUnionDeclaration
    : structOrUnion Identifier ';'
    ;

structOrUnionDefinition
    : structOrUnion Identifier '{' field* '}' ';'
    ;

field
    : typeSpecifier Identifier ';'
    ;

enumType
    : 'enum' '{' enumerator (',' enumerator)* ','? '}'
    | 'enum' Identifier
    ;

structOrUnionType
    : structOrUnion '{' field* '}'
    | structOrUnion Identifier
    ;

builtinType
    : 'char'
    | 'short'
    | 'int'
    | 'long' 'long'
    | 'long'
    | '_Bool'
    | 'bool'
    | '__m128'
    | '__m128d'
    | '__m128i'
    ;

typeName
    : builtinType
    | structOrUnionType
    | enumType
    ;

typeSpecifier
    : 'const' typeSpecifier '*' ('restrict' | 'const')?
    | typeSpecifier 'const' '*' ('restrict' | 'const')?
    | typeSpecifier '*' ('restrict' | 'const')?
    | 'const' 'void' '*' ('restrict' | 'const')?
    | 'void' 'const' '*' ('restrict' | 'const')?
    | 'void' '*' ('restrict' | 'const')?
    | typeName
    ;

functionSpecifier
    : 'inline'
    | '_Noreturn'
    | '__inline__' // GCC extension
    | '__stdcall'
    | '__declspec' '(' Identifier ')'
    | 'extern'
    | 'static'
    ;

functionParamsDefinition
    : 'void'
    | typeSpecifier Identifier (',' typeSpecifier Identifier)*
    ;

functionParamsDeclaration
    : typeSpecifier (',' typeSpecifier)*
    | functionParamsDefinition
    ;

functionDeclaration
    : functionSpecifier* 'void' Identifier '('
        functionParamsDeclaration? ')' ';' # voidFunctionDeclaration
    | functionSpecifier* typeSpecifier Identifier '('
        functionParamsDeclaration? ')' ';' # nonVoidFunctionDeclaration
    ;

functionDefinition
    : functionSpecifier* 'void' Identifier '('
        functionParamsDefinition? ')' compoundStatement # voidFunctionDefinition
    | functionSpecifier* typeSpecifier Identifier '('
        functionParamsDefinition? ')' compoundStatement # nonVoidFunctionDefinition
    ;

compoundStatement
    : '{' blockItem* '}'
    ;

blockItem
    : statement
    | variableDeclaration
    | enumDeclaration
    | structOrUnionDeclaration
    | functionDeclaration
    ;

variableDeclaration
    : typeSpecifier Identifier ';'                         # noInitializerVariable
    // | typeSpecifier Identifier '=' compoundInitializer ';' # compoundInitializerVariable
    | typeSpecifier Identifier '=' primaryExpression ';'   # objectDeclarationVariable
    ;

statement
    : compoundStatement
    | assignmentStatement
    ;

assignmentStatement
    : Identifier assignmentOperator expression ';'
    ;

assignmentOperator
    : '='
    | '*='
    | '/='
    | '%='
    | '+='
    | '-='
    | '<<='
    | '>>='
    | '&='
    | '^='
    | '|='
    ;

expression
    : equalityExpression
    ;

equalityExpression
    : relationalExpression '==' equalityExpression # equalExpression
    | relationalExpression '!=' equalityExpression # unequalExpression
    | relationalExpression                         # baseEqualityExpression
    ;

relationalExpression
    : shiftExpression '<' relationalExpression  # lessThanExpression
    | shiftExpression '>' relationalExpression  # greaterThanExpression
    | shiftExpression '<=' relationalExpression # lessOrEqualsExpression
    | shiftExpression '>=' relationalExpression # greaterOrEqualsExpression
    | shiftExpression                           # baseRelationalExpression
    ;

shiftExpression
    : additiveExpression '<<' shiftExpression # leftShiftExpression
    | additiveExpression '>>' shiftExpression # rightShiftExpression
    | additiveExpression                      # baseShiftExpression
    ;

additiveExpression
    : multiplicativeExpression '+' additiveExpression # additionExpression
    | multiplicativeExpression '-' additiveExpression # subtractionExpression
    | multiplicativeExpression                        # baseAdditiveExpression
    ;

multiplicativeExpression
    : castExpression '*' multiplicativeExpression # multiplyExpression
    | castExpression '/' multiplicativeExpression # divisionExpression
    | castExpression '%' multiplicativeExpression # moduloExpression
    | castExpression                              # baseMultiplicativeExpression
    ;

castExpression
    : '(' typeSpecifier ')' castExpression # cast2TypeExpression
    | unaryExpression                      # baseCastExpression
    ;

unaryExpression
    : '&' unaryExpression              # addressOfExpression
    | '*' unaryExpression              # dereferenceExpression
    | '+' unaryExpression              # unaryPlusExpression
    | '-' unaryExpression              # unaryMinusExpression
    | '~' unaryExpression              # bitwiseNotExpression
    | '!' unaryExpression              # logicalNotExpression
    | 'sizeof' '(' unaryExpression ')' # sizeofExpression
    | postfixExpression                # baseUnaryExpression
    ;

postfixExpression
    // | postfixExpression '[' expression ']' # arrayIndexingExpression
    // | postfixExpression '.' Identifier     # memberAccessExpression
    // | postfixExpression '->' Identifier    # memberAccessFromPointerExpression
    : postfixExpression '++'                # postIncrementExpression
    | postfixExpression '--'                # postDecrementExpression
    | Identifier '(' expression* ')'        # functionCallExpression
    | parenthesisExpression                 # basePostfixExpression
    ;

parenthesisExpression
    : '(' expression ')'
    | primaryExpression
    ;

primaryExpression
    : Identifier     # primaryExprIdentifier
    | Constant       # primaryExprConstant
    | StringLiteral+ # primaryExprStringLits
    ;

// Lexer rules
Identifier
    : IdentifierNondigit (IdentifierNondigit | Digit)*
    ;

fragment IdentifierNondigit
    : Nondigit
    | UniversalCharacterName
    //|   // other implementation-defined characters...
    ;

fragment Nondigit
    : [a-zA-Z_]
    ;

fragment Digit
    : [0-9]
    ;

fragment UniversalCharacterName
    : '\\u' HexQuad
    | '\\U' HexQuad HexQuad
    ;

fragment HexQuad
    : HexadecimalDigit HexadecimalDigit HexadecimalDigit HexadecimalDigit
    ;

fragment HexadecimalDigit
    : [0-9a-fA-F]
    ;

StringLiteral
    : EncodingPrefix? '"' SCharSequence? '"'
    ;

fragment EncodingPrefix
    : 'u8'
    | 'u'
    | 'U'
    | 'L'
    ;

fragment SCharSequence
    : SChar+
    ;

fragment SChar
    : ~["\\\r\n]
    | EscapeSequence
    | '\\\n'   // Added line
    | '\\\r\n' // Added line
    ;

fragment EscapeSequence
    : SimpleEscapeSequence
    | OctalEscapeSequence
    | HexadecimalEscapeSequence
    | UniversalCharacterName
    ;

fragment SimpleEscapeSequence
    : '\\' ['"?abfnrtv\\]
    ;

fragment OctalEscapeSequence
    : '\\' OctalDigit OctalDigit? OctalDigit?
    ;

fragment HexadecimalEscapeSequence
    : '\\x' HexadecimalDigit+
    ;

Constant
    : IntegerConstant
    //| FloatingConstant
    //|   EnumerationConstant
    | CharacterConstant
    ;

fragment IntegerConstant
    : DecimalConstant IntegerSuffix?
    | OctalConstant IntegerSuffix?
    | HexadecimalConstant IntegerSuffix?
    | BinaryConstant
    ;

fragment BinaryConstant
    : '0' [bB] [0-1]+
    ;

fragment DecimalConstant
    : NonzeroDigit Digit*
    ;

fragment OctalConstant
    : '0' OctalDigit*
    ;

fragment HexadecimalConstant
    : HexadecimalPrefix HexadecimalDigit+
    ;

fragment HexadecimalPrefix
    : '0' [xX]
    ;

fragment NonzeroDigit
    : [1-9]
    ;

fragment OctalDigit
    : [0-7]
    ;

fragment IntegerSuffix
    : UnsignedSuffix LongSuffix?
    | UnsignedSuffix LongLongSuffix
    | LongSuffix UnsignedSuffix?
    | LongLongSuffix UnsignedSuffix?
    ;

fragment UnsignedSuffix
    : [uU]
    ;

fragment LongSuffix
    : [lL]
    ;

fragment LongLongSuffix
    : 'll'
    | 'LL'
    ;

fragment FloatingConstant
    : DecimalFloatingConstant
    | HexadecimalFloatingConstant
    ;

fragment DecimalFloatingConstant
    : FractionalConstant ExponentPart? FloatingSuffix?
    | DigitSequence ExponentPart FloatingSuffix?
    ;

fragment FloatingSuffix
    : [flFL]
    ;

fragment FractionalConstant
    : DigitSequence? '.' DigitSequence
    | DigitSequence '.'
    ;

fragment ExponentPart
    : [eE] Sign? DigitSequence
    ;

fragment Sign
    : [+-]
    ;

DigitSequence
    : Digit+
    ;

fragment HexadecimalFloatingConstant
    : HexadecimalPrefix (HexadecimalFractionalConstant | HexadecimalDigitSequence) BinaryExponentPart FloatingSuffix?
    ;

fragment HexadecimalFractionalConstant
    : HexadecimalDigitSequence? '.' HexadecimalDigitSequence
    | HexadecimalDigitSequence '.'
    ;

fragment HexadecimalDigitSequence
    : HexadecimalDigit+
    ;

fragment BinaryExponentPart
    : [pP] Sign? DigitSequence
    ;

fragment CharacterConstant
    : '\'' CCharSequence '\''
    | 'L\'' CCharSequence '\''
    | 'u\'' CCharSequence '\''
    | 'U\'' CCharSequence '\''
    ;

fragment CCharSequence
    : CChar+
    ;

fragment CChar
    : ~['\\\r\n]
    | EscapeSequence
    ;

MultiLineMacro
    : '#' (~[\n]*? '\\' '\r'? '\n')+ ~ [\n]+ -> channel (HIDDEN)
    ;

Directive
    : '#' ~ [\n]* -> channel (HIDDEN)
    ;

// ignore the following asm blocks:
/*
    asm
    {
        mfspr x, 286;
    }
 */
AsmBlock
    : 'asm' ~'{'* '{' ~'}'* '}' -> channel(HIDDEN)
    ;

Whitespace
    : [ \t]+ -> channel(HIDDEN)
    ;

Newline
    : ('\r' '\n'? | '\n') -> channel(HIDDEN)
    ;

BlockComment
    : '/*' .*? '*/' -> channel(HIDDEN)
    ;

LineComment
    : '//' ~[\r\n]* -> channel(HIDDEN)
    ;
