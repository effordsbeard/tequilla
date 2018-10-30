import sys
import os, os.path
from pyquery import PyQuery as pq
import re
import importlib


# I hope I won't modify this, I don't understand anything
class Tequilla(object):

    templates = {}

    # folder :str - path to templates folder
    # compiled :str - path to compiled templates folder, where python functions returning renders are saved
    def __init__(self, folder, compiled='compiled'):
        self.folder = folder
        self.compiled_path = os.path.join(folder, compiled)

    def compile(self):
        for dirname, subfolders, files in os.walk(self.folder):
            # walking recursively in templates folder
            if dirname.startswith(self.compiled_path):
                continue # not in compiled folder if it is in templates folder
            for file in files:
                tpl_file_path = os.path.join(dirname, file)
                self.compile_template(tpl_file_path)

    # tpl_path:str path to template in templates folder
    # making mirror path for compiled template using path from html template replacing folder with compiled
    def get_compiled_path(self, tpl_path):
        tpl_path = tpl_path.replace(self.folder, '')
        if tpl_path.startswith('/'):  # in dreams paths to templates folders can be relative
            tpl_path = tpl_path[1:]
        path = os.path.join(self.compiled_path, os.path.splitext(tpl_path)[0] + '.py')
        os.makedirs(os.path.dirname(path), exist_ok=True)  # make the same directory structure for compiled folder
        return path


    # path: str path to template file
    def compile_template(self, path):

        tpl = ''
        with open(path, 'r') as f:
            tpl = f.read()

        #   '#include <tpl rel path>'  handling
        for match in re.findall('#include .+', tpl):
            include_path = match.split(' ', 2)[1]
            with open(os.path.join(os.path.dirname(path), include_path), 'r') as f:
                tpl = tpl.replace(match, f.read())

        d = pq(tpl)
        # difficult scopes should be compiled separately
        scoped_selector = '[loop], [if]'
        d(scoped_selector).attr('scoped', 'true')
        scopes = []
        scope_id = 0

        while True:
            # find scopes with no scopes inside
            elems = d('[scoped]').filter(lambda i, el: not pq(el).find('[scoped]'))
            if not elems:
                break
            # replace scopes with filler
            replacer = pq('<span scope-id="%d"></span>' % scope_id)
            elem = elems[0]
            scopes.append(d(elem).outerHtml())
            d(elem).replaceWith(replacer)
            scope_id += 1
            # do while document has scopes
        scopes.append(d.outerHtml()) # final scope is whole document

        compiled = []

        # and compile scopes with order from small to document
        for scope in scopes:
            _comp = self.compile_scope(scope)
            compiled.append(_comp)

        # replace fillers in the same order
        for i in range(1, len(compiled)):
            for j in range(0, i):
                compiled[i] = compiled[i] \
                    .replace('<span scope-id="%d"></span>' % j, '\' , %s , \'' % compiled[j]) \
                    .replace('<span scope-id="%d"/>' % j, '\' , %s , \'' % compiled[j])

        res = compiled[len(compiled) - 1]
        # save indentation
        res = res.replace('\n', '\\n \\\n')
        # I don't really know for what
        res = '\'' + res[1:-1] + '\''
        # remove template attributes
        res = re.sub(r'loop="[^"]*"', '', res)
        res = re.sub(r'if="[^"]*"', '', res)
        res = re.sub(r'scoped="true"', '', res)
        # and wrap all in lambda and join
        res = 'lambda data: \'\'.join([' + res + '])'

        # get path to file where to save compiled string
        compiled_path = self.get_compiled_path(path)
        with open(compiled_path, 'w') as f:
            f.write(res)

        # add compiled function to memory
        with open(compiled_path, 'r', encoding="utf-8") as f:
            self.templates[path.replace(self.folder + '/', '').replace(self.folder, '')] = eval(f.read())

    # html: str
    # dividing simple text and python code wrapped in '{{}}'
    def expr(self, html):
        parts = html.split('{{')
        result = ''

        for part in parts:
            if not '}}' in part:
                result += '\'%s\'' % part.replace('\'', '\\\'')
            else:
                param, text = part.split('}}')
                result += ', %s, ' % param
                result += '\'%s\'' % text.replace('\'', '\\\'')

        return result

    # html: str
    # for_params: str python 'for' statement for simple 'for' loops
    # handling loop scope
    def loop_scope(self, html, for_params):
        # compile tempalte inside scope
        compiled_expr = self.expr(html)
        # wrap with joins
        return '\'\'.join([\'\'.join([%s]) for %s])' % (compiled_expr, for_params)
        # print(python)

    # html: str
    # if_params: str python 'if' statement
    def if_scope(self, html, if_params):
        compiled_expr = self.expr(html)
        return '\'\'.join([%s]) if %s else \'\'' % (compiled_expr, if_params)

    def compile_scope(self, html):
        s = pq(html)
        _loop = s.attr('loop')
        _if = s.attr('if')

        if _loop:
            return self.loop_scope(html, _loop)

        if _if:
            return self.if_scope(html, _if)

        return self.expr(html)

    def render(self, tpl, data={}):
        return self.templates[tpl](data)

sys.modules[__name__] = Tequilla
