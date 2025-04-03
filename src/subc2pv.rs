use std::collections::{HashMap, HashSet};
use antlr_rust::tree::{ParseTree, ParseTreeListener};

use crate::libs::subcparser::{self, EnumDeclarationContextAttrs, EnumDefinitionContextAttrs, EnumeratorContextAttrs, FunctionDeclarationContextAttrs, SubCParserContext, SubCParserContextType};
use crate::libs::subclistener::SubCListener;

pub fn hash_code<T: Sized>(obj: &T) -> usize {
    core::ptr::from_ref(obj) as usize
}

pub struct SubC2PVListener {
    pub ctx2pv: HashMap<usize, String>,
    terms: HashSet<String>,
    enum_types: HashMap<String, Vec<String>>,
    anon_enum_counter: usize,
    declared_functions: HashMap<String, (Option<String>, Vec<(String, String)>)>,
    defined_functions: HashMap<String, (Option<String>, Vec<(String, String)>)>
}

impl SubC2PVListener {
    pub fn new() -> Self {
        Self {
            ctx2pv: HashMap::new(),
            terms: HashSet::new(),
            enum_types: HashMap::new(),
            anon_enum_counter: 0,
            declared_functions: HashMap::new(),
            defined_functions: HashMap::new()
        }
    }

}

impl<'input> SubC2PVListener {
    fn next_anon_enum_id(&mut self) -> usize {
        // TODO: generate better identifiers
        let ans = self.anon_enum_counter;
        self.anon_enum_counter += 1;
        ans
    }

    fn translate_enumerations(&self) -> String {
        let lines: Vec<_> = self.enum_types.iter()
            .map(|(e_type, e_consts)| if e_consts.is_empty() {
                format!("type {}.", e_type)
            } else {
                format!("type {}.\nconst {}: {}.", e_type, e_consts.join(","), e_type)
            }).collect();
        lines.join("\n")
    }
}

impl<'input> ParseTreeListener<'input, SubCParserContextType> for SubC2PVListener {
    fn enter_every_rule(&mut self, ctx: &dyn SubCParserContext<'input>) {
        println!(
            "dbg: rule entered {}",
            subcparser::ruleNames
                .get(ctx.get_rule_index())
                .unwrap_or(&"error")
        )
    }
}

impl<'input> SubCListener<'input> for SubC2PVListener {
    fn exit_enumDefinition(&mut self, _ctx: &subcparser::EnumDefinitionContext<'input>) {
        let ename = match _ctx.Identifier() {
            Some(name) => name.get_text(),
            None => format!("anon_enum{}", self.next_anon_enum_id())
        };
        if ! self.enum_types.contains_key(&ename) {
            // ignore constants as they are not important in Pi-calculus
            self.enum_types.insert(ename,
                _ctx.enumerator_all().into_iter()
                .map(|rc| rc.Identifier().unwrap().get_text())
                .collect());
            return;
        }
        panic!("Enumeration name {} already defined", ename); // TODO: better handling
    }

    fn exit_enumDeclaration(&mut self, _ctx: &subcparser::EnumDeclarationContext<'input>) {
        if let Some(rc) = _ctx.Identifier() {
            let ename = rc.get_text();
            if ! self.enum_types.contains_key(&ename) {
                self.enum_types.insert(ename, vec![]);
                return;
            }
            panic!("Enumeration name {} already defined", ename); // TODO: better handling
        }
        panic!("Enumeration declaration must have name");
    }

    fn exit_functionDeclaration(&mut self, _ctx: &subcparser::FunctionDeclarationContext<'input>) {
        let function_name = _ctx.Identifier().unwrap().get_text();
        if self.declared_functions.contains_key(&function_name) {
            panic!("Function '{}' already defined", function_name);
        }
        self.declared_functions.insert(function_name, (None, vec![]));
    }

    fn exit_compilationUnit(&mut self, _ctx: &subcparser::CompilationUnitContext<'input>) {
        // output all enumeration types and its constants
        self.ctx2pv.insert(hash_code(_ctx),
            self.translate_enumerations());
    }
}
