isa = isinstance
Symbol = str

class Env(dict):
    def __init__(self, parms=(), args=(), outer=None):
        self.update(zip(parms, args))
        self.outer = outer
    def find(self, var):
        return self if var in self else self.outer.find(var)

def add_globals(env):
    "Add some Scheme standard procedures to an environment."
    import math, operator as op
    env.update(vars(math)) # sin, sqrt, ...
    env.update(
     {'+':op.add, '-':op.sub, '*':op.mul, '/':op.div, 'not':op.not_,
      '>':op.gt, '<':op.lt, '>=':op.ge, '<=':op.le, '=':op.eq, 
      'equal?':op.eq, 'eq?':op.is_, 'length':len, 'cons':lambda x,y:[x]+y,
      'car':lambda x:x[0],'cdr':lambda x:x[1:], 'append':op.add,  
      'list':lambda *x:list(x), 'list?': lambda x:isa(x,list), 
      'null?':lambda x:x==[], 'symbol?':lambda x: isa(x, Symbol)})
    return env

global_env = add_globals(Env())

def eval(x, env=global_env):
    # variable reference
    if isa(x, Symbol):
        return env.find(x)[x]
    # constant literal
    elif not isa(x, list):
        return x
    # (quote exp)
    elif x[0] == 'quote':
        (_, exp) = x
        return exp
    # (if test conseq alt)
    elif x[0] == 'if':
        (_, test, conseq, alt) = x
        return eval((conseq if eval(test, env) else alt), env)
    # (set? var exp)
    elif x[0] == 'set!':
        (_, var, exp) = x
        env.find(var)[var] = eval(exp, env)
    # (define var exp)
    # all same with 'set!'
    elif x[0] == 'define':
        (_, var, exp) = x
        env.find(var)[var] = eval(exp, env)
    # (lambda (var*) exp)
    elif x[0] == 'lambda':
        (_, vars, exp) = x
        return lambda *args: eval(exp, Env(vars, args, env))
    # (begin exp*)
    elif x[0] == 'begin':
        for exp in x[1:]:
            val = eval(exp, env)
        return val
    # (proc exp*)
    else:
        exps = [eval(exp, env) for exp in x]
        proc = exps.pop(0)
        return proc(*exps)

def tokenize(s):
    return s.replace('(',' ( ').replace(')', ' ) ').split()

def read_from(tokens):
    if len(tokens) == 0:
        raise SyntaxError("unexpected EOF of tokens")
    token = tokens.pop(0)
    if token == '(':
        L = []
        while tokens[0] != ')':
            L.append(read_from(tokens))
        tokens.pop(0)
        return L
    elif token == ')':
        raise SyntaxError("unexpected")
    else:
        return atom(token)

def atom(token):
    try: return int(token)
    except ValueError:
        try: return float(token)
        except ValueError:
            return str(token)


def read(s):
    return read_from(tokenize(s))
parse = read


def to_string(exp):
    return '(' + ''.join(map(to_string, exp)) + ')' if isa(exp, list) else str(exp)

def repl(prompt='Lis.py>'):
    while True:
        val = eval(parse(raw_input(prompt)))
        if val: print to_string(val)

if __name__ == '__main__':
    repl()

