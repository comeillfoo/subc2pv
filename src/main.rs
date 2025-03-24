use std::process::ExitCode;
use antlr_rust::common_token_stream::CommonTokenStream;
use antlr_rust::input_stream::ByteStream;

mod libs;
mod subc2pv;

use crate::libs::subclexer::SubCLexer;
use crate::libs::subcparser::SubCParser;
use crate::subc2pv::SubC2PVListener;

fn usage(selfarg: String) -> u8 {
    println!(r#"Usage: {} [options] <path-to-file>

Options:

-h,--help Prints this help message and exits"#, selfarg);
    22
}

fn extract_proto(path: String) -> u8 {
    match std::fs::read(path) {
        Ok(content) => {
            let lexer = SubCLexer::new(ByteStream::new(&content));
            let token_source = CommonTokenStream::new(lexer);

            let mut parser = SubCParser::new(token_source);
            parser.add_parse_listener(Box::new(SubC2PVListener::new()));
            let result = parser.compilationUnit();

            assert!(result.is_ok());
            0
        },
        Err(e) => e.raw_os_error().unwrap_or(1) as u8
    }
}

fn main() -> ExitCode {
    let mut args: Vec<String> = std::env::args().collect();
    let selfarg = args[0].clone();
    args.remove(0);

    let mut it = args.into_iter().peekable();
    while let Some(arg) = it.peek() {
        match arg.as_str() {
            "-h" | "--help" => return ExitCode::from(usage(selfarg)),
            _ => break
        }
    }

    ExitCode::from(match it.next() {
        Some(path) => extract_proto(path),
        None => usage(selfarg)
    })
}
