import re
import math
from lark import Lark, InlineTransformer, Token


grammar = Lark(
    r"""
?start  : assign* comp?
?assign: NAME "=" comp
?comp  : expr ">" expr  -> gt
       | expr ">=" expr -> ge
       | expr "<" expr  -> lt
       | expr "<=" expr -> le
       | expr "!=" expr -> ne
       | expr "==" expr -> eq
       | expr
?expr  : expr "+" term  -> add
       | expr "-" term  -> sub
       | term
?term  : term "*" pow   -> mul
       | term "/" pow   -> div
       | pow
?pow   : atom "^" pow   -> exp
       | atom
?atom  : NUMBER                        -> number
       | NAME "(" expr ")"             -> function_call
       | NAME "(" expr ("," expr)* ")" -> function_call
       | NAME                          -> var
       | "(" expr ")"
NAME   : /[-+]?\w+/
NUMBER : /-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?/
%ignore /\s+/
%ignore /\#.*/
"""
)

exprs = ["sin", "pi"]

for exp in exprs:
    tree = grammar.parse(exp)
    print(exp)
    print(tree.pretty())
    print('-' * 40)


class CalcTransformer(InlineTransformer):
    from operator import add, sub, mul, truediv as div, pow as exp, gt, ge, lt, ne, eq, le

    def __init__(self):
        super().__init__()
        self.variables = {k: v for k, v in vars(math).items() if not k.startswith("_")}
        self.variables.update(max=max, min=min, abs=abs)
        self.env = {}

    def start(self, *args):
        return args[-1]
    
    def assign(self, name, value):
        self.env[name] = value
        return self.env[name]

    def const(self, token):
        value = self.variables[token]
        return value
    
    def number(self, token):
        try:
            return int(token)
        except:
            return float(token)
    
    def function_call(self, name, *args):
        name = str(name)
        fn = self.variables[name.split('-')[-1]]
        if name[0] == '-':
            return -fn(*args)
        return fn(*args)
        
    def var(self, token):
        if token in self.variables:
            return self.variables[token]
        elif token[0] == "-" and token[1:] in self.variables:
            return -self.variables[token[1:]]
        else:
            return self.env[token]