use core::panic;
use std::rc::Rc;
use std::collections::{HashMap, HashSet};
use antlr_rust::tree::ParseTreeListener;

use crate::libs::clistener::CListener;
use crate::libs::cparser::{self, AdditiveExpressionContextAttrs, AssignmentExpressionContextAll, AssignmentExpressionContextAttrs, AssignmentOperatorContextAll, AssignmentOperatorContextAttrs, CastExpressionContextAttrs, ConditionalExpressionContextAll, EqualityExpressionContextAttrs, MultiplicativeExpressionContextAttrs, PrimaryExpressionContextAttrs, RelationalExpressionContextAttrs, ShiftExpressionContextAttrs, UnaryExpressionContextAll, UnaryExpressionContextAttrs};
use crate::libs::cparser::{CParserContext, CParserContextType};

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
    fn ex_cond(&mut self, _ctx: &ConditionalExpressionContextAll<'input>) -> Option<String> {
        if let Some(ans) = self.ctx2pv.get(&hash_code(_ctx)) {
            return Some(ans.to_owned());
        }
        None
    }

    fn ex_assign(&mut self, left: &UnaryExpressionContextAll<'input>,
                 op: &AssignmentOperatorContextAll<'input>,
                 _expr: &AssignmentExpressionContextAll<'input>) -> Option<String> {
        if let Some(term) = self.ctx2pv.get(&hash_code(left)) {
            if op.Assign().is_some() {
                self.terms.insert(term.clone());
                return Some(format!("new {}", term));
            }

            if self.terms.contains(term) {
                return None;
            }
        }
        panic!("Unsupported sequence of tokens in assignment")
    }

    fn ex_subexprs<T>(&mut self, subexprs: Vec<Rc<T>>) -> Option<String> {
        if subexprs.len() == 1 {
            if let Some(ident) = self.ctx2pv.get(&hash_code(subexprs[0].as_ref())) {
                return Some(ident.to_owned());
            }
        }
        None
    }
}

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

impl<'input> CListener<'input> for SubC2PVListener {
    fn exit_primaryExpression(&mut self, _ctx: &cparser::PrimaryExpressionContext<'input>) {
        // TODO: ;
    }

    fn exit_postfixExpression(&mut self, _ctx: &cparser::PostfixExpressionContext<'input>) {
        // TODO: ;
    }

    fn exit_unaryExpression(&mut self, _ctx: &cparser::UnaryExpressionContext<'input>) {
        let k = hash_code(_ctx);
        if let Some(cast) = _ctx.castExpression() {
            let v = self.ctx2pv.get(&hash_code(cast.as_ref()))
                .unwrap().to_owned();
            self.ctx2pv.insert(k, v);
        }

        if let Some(postfix) = _ctx.postfixExpression() {
            let v = self.ctx2pv.get(&hash_code(postfix.as_ref()))
                .unwrap().to_owned();
            self.ctx2pv.insert(k, v);
        }
        // TODO: ;
    }

    fn exit_castExpression(&mut self, _ctx: &cparser::CastExpressionContext<'input>) {
        let k = hash_code(_ctx);
        if let Some(cast) = _ctx.castExpression() {
            let v = self.ctx2pv.get(&hash_code(cast.as_ref()))
                .unwrap().to_owned();
            self.ctx2pv.insert(k, v);
        }

        if let Some(unary) = _ctx.unaryExpression() {
            let v = self.ctx2pv.get(&hash_code(unary.as_ref()))
                .unwrap().to_owned();
            self.ctx2pv.insert(k, v);
        }
        // TODO: ;
    }

    fn exit_multiplicativeExpression(&mut self, _ctx: &cparser::MultiplicativeExpressionContext<'input>) {
        let k = hash_code(_ctx);
        let subexprs = _ctx.castExpression_all();
        if let Some(v) = self.ex_subexprs(subexprs) {
            self.ctx2pv.insert(k, v);
        }

        // TODO: ;
    }

    fn exit_additiveExpression(&mut self, _ctx: &cparser::AdditiveExpressionContext<'input>) {
        let k = hash_code(_ctx);
        let subexprs = _ctx.multiplicativeExpression_all();
        if let Some(v) = self.ex_subexprs(subexprs) {
            self.ctx2pv.insert(k, v);
        }

        // TODO: ;
    }

    fn exit_shiftExpression(&mut self, _ctx: &cparser::ShiftExpressionContext<'input>) {
        let k = hash_code(_ctx);
        let subexprs = _ctx.additiveExpression_all();
        if let Some(v) = self.ex_subexprs(subexprs) {
            self.ctx2pv.insert(k, v);
        }

        // TODO:;
    }

    fn exit_relationalExpression(&mut self, _ctx: &cparser::RelationalExpressionContext<'input>) {
        let k = hash_code(_ctx);
        let subexprs = _ctx.shiftExpression_all();
        if let Some(v) = self.ex_subexprs(subexprs) {
            self.ctx2pv.insert(k, v);
        }

        // TODO:;
    }

    fn exit_equalityExpression(&mut self, _ctx: &cparser::EqualityExpressionContext<'input>) {
        let k = hash_code(_ctx);
        let subexprs = _ctx.relationalExpression_all();
        if let Some(v) = self.ex_subexprs(subexprs) {
            self.ctx2pv.insert(k, v);
        }

        // TODO:
    }

    fn exit_assignmentExpression(&mut self, _ctx: &cparser::AssignmentExpressionContext<'input>) {
        let ans = match (_ctx.conditionalExpression(), _ctx.unaryExpression(), _ctx.assignmentOperator(), _ctx.assignmentExpression(), _ctx.DigitSequence()) {
            (Some(cond), None, None, None, None) => self.ex_cond(cond.as_ref()),
            (None, Some(left), Some(op), Some(expr), None) => self.ex_assign(left.as_ref(), op.as_ref(), expr.as_ref()),
            (None, None, None, None, Some(_digits)) => None,
            _ => panic!("Malformed parse tree")
        };
        if let Some(v) = ans {
            let k = hash_code(_ctx);
            self.ctx2pv.insert(k, v);
        }
    }
}
