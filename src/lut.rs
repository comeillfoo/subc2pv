use std::{collections::HashMap, io::{BufRead, BufReader}};

enum LutParserStates {
    NoDirectives,
    Process,
    Mappings
}

pub struct LookupTable {
    mappings: HashMap<String, String>,
    preamble: Option<String>
}

fn parse_file(file: std::fs::File) -> Option<LookupTable> {
    let mut reader = BufReader::new(file);
    let mut preamble = None;
    let mut mappings = HashMap::new();
    let mut state = LutParserStates::NoDirectives;
    let mut buffer = String::new();
    let mut rows = 1;
    buffer.clear();
    while let Some(_) = reader.read_line(&mut buffer).ok() {
        state = match state {
            LutParserStates::NoDirectives => match buffer.as_str() {
                "%P" => LutParserStates::Process,
                "%L" => LutParserStates::Mappings,
                _ => {
                    println!("fatal: invalid line '{}' at {}", buffer, rows);
                    return None;
                }
            },
            LutParserStates::Mappings => match buffer.as_str() {
                "%%" => LutParserStates::NoDirectives,
                _ => {
                    // TODO: parse mappings
                    println!("fatal: invalid line '{}' at {}", buffer, rows);
                    return None;
                }
            },
            LutParserStates::Process => match buffer.as_str() {
                "%%" => LutParserStates::NoDirectives,
                _ => {
                    preamble = preamble.and_then(|mut prev: String| {
                        prev.push_str(buffer.as_str());
                        Some(prev)
                    }).or(Some(buffer.clone()));
                    LutParserStates::Process
                }
            }
        };
        buffer.clear();
        rows += 1;
    }
    Some(LookupTable {
        mappings,
        preamble
    })
}

impl LookupTable {
    pub fn new(path: String) -> Option<Self> {
        let file = std::fs::File::open(path).ok()?;
        parse_file(file)
    }
}
