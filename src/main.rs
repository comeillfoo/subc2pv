use antlr_rust::common_token_stream::CommonTokenStream;
use antlr_rust::input_stream::InputStream;

mod libs;
mod subc2pv;

use crate::libs::clexer::CLexer;
use crate::libs::cparser::CParser;
use crate::subc2pv::SubC2PVListener;

fn main() {
    let input = "int main(void) { printf(\"Hello, World!\\n\"); return 0; }".into();

    let lexer = CLexer::new(InputStream::new(input));
    let token_source = CommonTokenStream::new(lexer);

    let mut parser = CParser::new(token_source);
    parser.add_parse_listener(Box::new(SubC2PVListener {}));
    let result = parser.compilationUnit();

    assert!(result.is_ok());
}
