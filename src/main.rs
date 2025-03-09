use antlr_rust::common_token_stream::CommonTokenStream;
use antlr_rust::input_stream::InputStream;

mod libs;
mod subc2pv;

use crate::libs::subclexer::SubCLexer;
use crate::libs::subcparser::SubCParser;
use crate::subc2pv::SubC2PVListener;

fn main() {
    let input = "int main(void) { printf(\"Hello, World!\\n\"); return 0; }".into();

    let lexer = SubCLexer::new(InputStream::new(input));
    let token_source = CommonTokenStream::new(lexer);

    let mut parser = SubCParser::new(token_source);
    parser.add_parse_listener(Box::new(SubC2PVListener::new()));
    let result = parser.compilationUnit();

    assert!(result.is_ok());
}
