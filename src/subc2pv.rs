use std::collections::{HashMap, HashSet};
use antlr_rust::tree::{ParseTree, ParseTreeListener};

use crate::libs::subcparser::{self, FunctionCallExpressionContextAttrs, SubCParserContext, SubCParserContextType, VariableDeclarationContextAttrs};
use crate::libs::subclistener::SubCListener;

fn hash_code<T: Sized>(obj: &T) -> usize {
    core::ptr::from_ref(obj) as usize
}

pub struct SubC2PVListener {
    ctx2pv: HashMap<usize, String>,
    terms: HashSet<String>
}

impl SubC2PVListener {
    pub fn new() -> Self {
        Self {
            ctx2pv: HashMap::new(),
            terms: HashSet::new()
        }
    }

}

impl<'input> SubC2PVListener {
}

impl<'input> ParseTreeListener<'input, SubCParserContextType> for SubC2PVListener {
    fn enter_every_rule(&mut self, ctx: &dyn SubCParserContext<'input>) {
        println!(
            "rule entered {}",
            subcparser::ruleNames
                .get(ctx.get_rule_index())
                .unwrap_or(&"error")
        )
    }
}

impl<'input> SubCListener<'input> for SubC2PVListener {
    fn exit_variableDeclaration(&mut self, _ctx: &subcparser::VariableDeclarationContext<'input>) {
        let k = hash_code(_ctx);
        if let Some(ident) = _ctx.Identifier() {
            let pattern = ident.get_text();
            if _ctx.functionCallExpression().is_none() {
                self.ctx2pv.insert(k, format!("new {};", pattern));
                return;
            }

            if let Some(fcall) = _ctx.functionCallExpression() {
                if let Some(term) = self.ctx2pv.get(&hash_code(fcall.as_ref())) {
                    self.ctx2pv.insert(k, format!("let {} = {} in", pattern, term));
                    return;
                }
            }
        }
    }
}
