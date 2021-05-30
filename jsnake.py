"""
# JSnake - Convert Python to Javascript as JSnake

# Todo

* Test nibbles.py
  * Add __jsnake_flip back. Need this alternative for exiting
    the do { ... } while (...) game loop.
* Terminal
  * Answer not displayed for SketchyCalculator.py
  * support backspace
  * deploy with term.js
* Develop
  python jsnake.py
  open http://127.0.0.1:5000
* Deploy
  python jsnake.py --translate nibbles.py > nibbles.es6.js
  ../traceur --out nibbles.js --script nibbles.es6.js
  python jsnake.py --deploy
  # FTP copy bin/jsnake to grantjenks.com/free-python-games
"""

import sys
import ast
import argparse
from itertools import count
from flask import Flask, request, Response

parser = argparse.ArgumentParser(description='jsnake to javascript translator')
parser.add_argument('--translate')
parser.add_argument('--deploy', action='store_true')

Counter = count()

class JSnakeVisitor(ast.NodeVisitor):
    def __init__(self, *args, **kwargs):
        super(JSnakeVisitor, self).__init__(*args, **kwargs)
        self._indent = 0
        self._parts = []
        self._counter = Counter

    def result(self):
        return ''.join(self._parts)

    def append(self, value):
        self._parts.append(value)

    def temp(self):
        return '__temp{0}'.format(next(self._counter))

    def indent(self):
        self._parts.append(' ' * self._indent)

    def statement(self, value):
        self.indent()
        self._parts.append(value);

    def visit(self, node):
        """Visit a node."""
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method)
        return visitor(node)

    def visit_Module(self, node):
        self.statement('function* __jsnake_prog() {\n')
        self._indent += 4
        self.generic_visit(node)
        self._indent -= 4
        self.statement('}\n')

    visit_alias = ast.NodeVisitor.generic_visit
    visit_BinOp = ast.NodeVisitor.generic_visit
    visit_Index = ast.NodeVisitor.generic_visit

    def visit_Print(self, node):
        self.statement('__jsnake_lib.print([')
        for value in node.values:
            self.visit(value)
            self.append(', ')
        if node.nl:
            self.append(r'"\r\n"');
        self.append(']);\n')

    def visit_Delete(self, node):
        self.indent()
        subscript = node.targets[0]
        self.visit(subscript.value)
        self.append('.splice(')
        self.visit(subscript.slice)
        self.append(', 1);\n')

    def visit_Expr(self, node):
        self.indent()
        self.generic_visit(node)
        self.append(';\n')

    def visit_ListComp(self, node):
        result = self.temp()
        temp = self.temp()
        self.append('((yield* \n(function* () {{ \nvar {0} = []; \n'.format(result))
        self.append('for (var {0} of '.format(temp))
        assert len(node.generators) == 1
        generator = node.generators[0]
        self._visit_Iterable(generator.iter)
        self.append(') {{ \nif ({0} === undefined){{ yield; }} \nelse {{ '.format(temp))
        self.visit(generator.target)
        self.append(' = {0}; {1}.push('.format(temp, result))
        self.visit(node.elt)
        self.append('); }} }} \nyield {0}; }})()), \n__jsnake_clear())'.format(result))

    def visit_Add(self, node): self.append(' + ')
    def visit_Sub(self, node): self.append(' - ')
    def visit_Mult(self, node): self.append(' * ')
    def visit_Div(self, node): self.append(' / ')
    def visit_Mod(self, node): self.append(' % ')

    def visit_Eq(self, node): self.append(' == ')
    def visit_NotEq(self, node): self.append(' != ')
    def visit_Lt(self, node): self.append(' < ')
    def visit_LtE(self, node): self.append(' <= ')
    def visit_Gt(self, node): self.append(' > ')
    def visit_GtE(self, node): self.append(' >= ')
    def visit_Is(self, node): self.append(' == ')

    def visit_And(self, node): self.append(' && ')
    def visit_Or(self, node): self.append(' || ')

    def visit_Continue(self, node): self.statement('continue;\n')

    def visit_Compare(self, node):
        if isinstance(node.ops[0], ast.In):
            self.append('__jsnake_in(')
            self.visit(node.left)
            self.append(', ')
            self.visit(node.comparators[0])
            self.append(')')
        elif isinstance(node.ops[0], ast.Eq):
            self.append('__jsnake_cmp(')
            self.visit(node.left)
            self.append(', ')
            self.visit(node.comparators[0])
            self.append(', ')
            self.append('__jsnake_op.eq')
            self.append(')')
        else:
            self.generic_visit(node)

    def visit_Subscript(self, node):
        self.visit(node.value)
        self.append('[__jsnake_idx(')
        self.visit(node.value)
        self.append(', ')
        self.visit(node.slice)
        self.append(')]')

    def visit_BoolOp(self, node):
        for idx, value in enumerate(node.values):
            self.append('(')
            self.visit(value)
            self.append(')')
            if idx < len(node.values) - 1:
                self.visit(node.op)

    def visit_Assign(self, node):
        if len(node.targets) == 1 and not isinstance(node.targets[0], ast.Tuple):
            self.indent()
            if isinstance(node.targets[0], ast.Name):
                self.append('var ')
            self.visit(node.targets[0])
            self.append(' = ')
            self.visit(node.value)
            self.append(';\n')
            return

        temp = self.temp()
        self.indent()
        self.append('{0} = '.format(temp))
        self.visit(node.value)
        self.append(';\n')
        for target in reversed(node.targets):
            if isinstance(target, ast.Tuple):
                for idx, name in enumerate(target.elts):
                    self.statement('{0} = {1}[{2}];\n'.format(name.id, temp, idx))
            elif isinstance(target, ast.Name):
                self.statement('{0} = {1};\n'.format(target.id, temp))

    def visit_Num(self, node):
        self.append('{0}'.format(node.n))
        self.generic_visit(node)

    def visit_Call(self, node):
        temp = self.temp()
        self.append('((yield* (function* () {{ for (var {0} of '.format(temp))
        self._visit_Iterable(node)
        self.append((
            ') {{ yield {0}; if ({0} !== undefined) break; '
            '}} }})()), __jsnake_clear())'
        ).format(temp))

    def visit_Attribute(self, node):
        self.visit(node.value)
        self.append('.')
        self.append(node.attr)

    def visit_Name(self, node):
        consts = {
            'None': 'null',
            'False': 'false',
            'True': 'true'
        }
        self.append(consts.get(node.id, node.id))

    def _visit_Iterable(self, node):
        # TODO: Change to _visit_Iterable
        # If func, visit func (as below)
        # Else, visit node
        if isinstance(node, ast.Call):
            self.visit(node.func)
            self.append('(')
            for idx, arg in enumerate(node.args):
                self.visit(arg)
                if idx < len(node.args) - 1:
                    self.append(', ')
            self.append(')')
        else:
            self.visit(node)

    def visit_For(self, node):
        temp = self.temp();
        self.statement('for (var {0} of '.format(temp))
        self._visit_Iterable(node.iter)
        self.append(') {\n')
        self._indent += 4
        self.statement('yield;\n')
        self.statement('if ({0} === undefined) {{ continue; }}\n'.format(temp))
        self.indent()
        self.visit(node.target)
        self.append(' = {0};\n'.format(temp))
        for stmt in node.body:
            self.visit(stmt)
        self.statement('yield;\n')
        self._indent -= 4
        self.statement('}\n')

    def visit_While(self, node):
        temp = self.temp()
        self.statement('while (')
        self.visit(node.test)
        self.append(') {\n')
        self._indent += 4
        self.statement('yield;\n');
        for stmt in node.body:
            self.visit(stmt)
        self.statement('yield;\n')
        self._indent -= 4
        self.statement('}\n')

    def visit_If(self, node):
        self.statement('if (')
        self.visit(node.test)
        self.append(') {\n')
        self._indent += 4
        for stmt in node.body:
            self.visit(stmt)
        self._indent -= 4
        self.statement('} else {\n')
        self._indent += 4
        for stmt in node.orelse:
            self.visit(stmt)
        self._indent -= 4
        self.statement('}\n')

    def visit_Tuple(self, node):
        self.append('[')
        for idx, child in enumerate(node.elts):
            self.visit(child)
            if idx < len(node.elts) - 1:
                self.append(', ')
        self.append(']')

    def visit_Str(self, node):
        self.append(repr(node.s))
        self.generic_visit(node)

    def visit_Import(self, node):
        for alias in node.names:
            self.statement('{0} = __jsnake_lib.{0};\n'.format(alias.name))
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        # todo:
        # from pygame.locals import *
        for alias in node.names:
            name = alias.name if alias.asname is None else alias.asname
            self.statement('{0} = __jsnake_lib.{1}.{2};\n'.format(name, node.module, alias.name))

args = parser.parse_args()

if args.translate:
    with open(args.translate) as fptr:
        module = ast.parse(fptr.read())

    visitor = JSnakeVisitor()

    visitor.visit(module)

    print visitor.result()

    sys.exit(0)

app = Flask(__name__)

games = (
    'nibbles',
    'SketchyCalculator',
)

@app.route('/')
def jsnake_root():
    games_list = ''.join('<li><a href="{0}.html">{0}</a></li>'.format(name)
                         for name in games)
    content = """<!doctype html>
    <html>
      <head>
        <title>JSnake Games</title>
      </head>
      <body>
        <ul>
        {0}
        </ul>
      </body>
    </html>""".format(games_list)
    return content

@app.route('/<name>.html')
def jsnake_html(name):
    assert name in games
    content = [
        '<!doctype html>',
        '<html>',
        '  <head>',
        '    <title>{0}</title>'.format(name.capitalize()),
        '  </head>',
        '  <body>',
        '    <div id="jsnake"></div>',
        '    <script src="//cdnjs.cloudflare.com/ajax/libs/lodash.js/2.4.1/lodash.min.js" type="text/javascript"></script>',
        '    <script src="//cdnjs.cloudflare.com/ajax/libs/jquery/2.1.1/jquery.min.js" type="text/javascript"></script>',
        '    <script src="traceur-runtime.js" type="text/javascript"></script>',
        '    <script src="term.js" type="text/javascript"></script>',
        '    <script src="{0}.js" type="text/javascript"></script>'.format(name),
        '    <script src="jsnake.js" type="text/javascript"></script>',
        '  </body>',
        '</html>',
    ]
    return '\n'.join(content)

@app.route('/<name>.js')
def jsnake_js(name):
    assert name in games
    try:
        with open(name + '.js') as fptr:
            return Response(fptr.read(), mimetype='text/javascript')
    except IOError:
        pass

    with open(name + '.py') as fptr:
        module = ast.parse(fptr.read())
    visitor = JSnakeVisitor()
    visitor.visit(module)

    return Response(visitor.result(), mimetype='text/javascript')


@app.route('/traceur-runtime.js')
def traceur_runtime():
    with open('traceur-runtime.js') as fptr:
        return Response(fptr.read(), mimetype='text/javascript')

@app.route('/jsnake.js')
def jsnake_lib():
    with open('jsnake.js') as fptr:
        return Response(fptr.read(), mimetype='text/javascript')

@app.route('/term.js')
def term_js():
    with open('term.js') as fptr:
        return Response(fptr.read(), mimetype='text/javascript')

if args.deploy:
    import os, shutil

    shutil.rmtree('bin/jsnake', True)
    os.makedirs('bin/jsnake')

    def write_resp(func, name):
        resp = func()
        text = resp if isinstance(resp, str) else resp.get_data()
        with open('bin/jsnake/' + name, 'w') as fptr:
            fptr.write(text)

    write_resp(jsnake_root, 'index.html')
    for name in games:
        write_resp(lambda: jsnake_html(name), name + '.html')
        write_resp(lambda: jsnake_js(name), name + '.js')
    write_resp(jsnake_lib, 'jsnake.js')
    write_resp(traceur_runtime, 'traceur-runtime.js')

    sys.exit(0)

if __name__ == '__main__':
    app.run(debug=True)
