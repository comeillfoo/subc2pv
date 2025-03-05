use antlr_rust::tree::ParseTreeListener;

use crate::libs::clistener::CListener;
use crate::libs::cparser;
use crate::libs::cparser::{CParserContext, CParserContextType};

pub struct SubC2PVListener;

impl<'input> ParseTreeListener<'input, CParserContextType> for SubC2PVListener {
    fn enter_every_rule(&mut self, ctx: &dyn CParserContext<'input>) {
        println!(
            "rule entered {}",
            cparser::ruleNames
                .get(ctx.get_rule_index())
                .unwrap_or(&"error")
        )
    }
}

impl<'input> CListener<'input> for SubC2PVListener {}
