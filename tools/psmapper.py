import json
import os
import secrets
import string
import sys
import re
from enum import Enum


class PSContextType(Enum):
    MAIN = 0
    FUNCTION = 1
    PARAMS = 2
    COMMENTS = 3


class PSContext:
    def __init__(self, name:str, ctx_type: PSContextType):
        self.last_line = 0
        self.ctx_type = ctx_type
        self.name = name
        self.content = ""
        self.brackets = 0
        self.first_line = 0

    def open_brackets(self, nb=1):
        self.brackets += nb

    def close_brackets(self, nb=1):
        self.brackets -= nb

    def change_context(self, new_context):
        self.ctx_type = new_context


class PSTree:
    def __init__(self, psctx: PSContext):
        self.ctx = [psctx]

    @property
    def current(self) -> PSContext:
        if not self.is_empty():
            return self.ctx[-1]

    @property
    def current_ctx_type(self) -> PSContextType:
        if not self.is_empty():
            return self.ctx[-1].ctx_type

    @property
    def previous(self) -> PSContext:
        self.ctx.pop(-1)
        return self.current

    @property
    def balanced(self) -> bool:
        if not self.is_empty():
            return self.ctx[-1].brackets == 0

    def is_empty(self):
        return len(self.ctx) == 0

    def close(self):
        return self.ctx.pop(-1)

    def add_content(self, value):
        self.current.content += f"\n{value}"

    def open_brackets(self, nb=1):
        self.current.brackets += nb

    def close_brackets(self, nb=1):
        self.current.brackets -= nb

    def change_context(self, ctx_name: str, ctx_type: PSContextType):
        self.ctx.append(PSContext(ctx_name, ctx_type))

    def extract_data(self):
        var_pattern = re.compile(r'\$[\w|_]+')
        matches = [match.group() for match in var_pattern.finditer(self.current.content)]
        _matches = list(set(matches))
        matches = []
        for e in _matches:
            if e.lower() in ["$true", "$false", "$null", "$_"]:
                continue
            matches.append(e)
        matches.sort(key=len)
        return matches[::-1]

def scramble(text):
    new_text = ""
    for char in text:
        if char.islower():
            new_text += secrets.choice(string.ascii_lowercase)
        else:
            new_text += char
    return new_text

def replace_comments(text):
    # Get rid of <# ... #> comments
    _content = text.encode().decode(encoding="windows-1252", errors="replace")
    start = False
    matches = re.finditer(r"<#[^#]+#>", _content, re.MULTILINE)
    for _, match in enumerate(matches, start=1):
        _content = _content.replace(match.group(), "")

    text = _content.split("\n")

    rows = []
    for nr, row in enumerate(text, start=1):
        if row.find("<#") > -1:
            start = True
        if row.find("#>") > -1:
            start = False
        if not start:
            rows.append(row)

    _content = "\n".join(rows)

    # Single Line Comments
    slc_pattern = re.compile(r"#.+")
    matches = slc_pattern.finditer(_content)
    for _, match in enumerate(matches, start=1):
        _content = _content.replace(match.group(), "")
    return _content


with open(sys.argv[1], "r") as ps:
    content = ps.read()

content = replace_comments(content)
content = content.split("\n")

tree = PSTree(
    psctx=PSContext(name="main", ctx_type=PSContextType.MAIN)
)

mapping = {}
function = ""

for n, line in enumerate(content, start=1):
    see_next = False
    tree.current.current_line = n
    function_match = None
    param_match = None
    ob = 0
    cb = 0
    tree.add_content(line)

    if tree.current_ctx_type == PSContextType.MAIN:
        function_match = re.search(r"function\s+([\w|\_|\-]+)\s*\{?", line, re.MULTILINE | re.IGNORECASE)

        if not function_match:
            continue

        function = function_match.groups()[0]
        print(f"Found new function {function} at line: {n}")
        tree.change_context(ctx_name=function, ctx_type=PSContextType.FUNCTION)
        see_next = True
        ob = function_match.group().count("{")
        if ob == 0:
            see_next = True
        cb = function_match.group().count("}")
    elif tree.current_ctx_type == PSContextType.FUNCTION:
        param_match = re.search(r"param[\s|\n|\r|\(]*\(?", line, re.IGNORECASE)

        if param_match:
            tree.change_context(ctx_name=tree.current.name + "-param", ctx_type=PSContextType.PARAMS)
            ob = param_match.group().count("(")
            cb = param_match.group().count(")")
            if ob == 0:
                see_next = True
        else:
            ob = line.count("{")
            cb = line.count("}")
    elif tree.current_ctx_type == PSContextType.PARAMS:
        ob = line.count("(")
        cb = line.count(")")
        if ob == 0 and cb == 0:
            see_next = True

    tree.open_brackets(nb=ob)
    tree.close_brackets(nb=cb)

    if tree.balanced and not see_next:
        if tree.current_ctx_type == PSContextType.PARAMS:
            params = tree.extract_data()
            print(f"  > Found parameters: {params}")
            mapping[function] = params
            # Close parameters context
            tree.close()
            # Close function context
            tree.close()


new_mapping = {}
for k, v in mapping.items():

    new_params = {}
    new_params["original"] = v
    new_params["repl"] = [scramble(param) for param in v]

    new_mapping[k] = {
        "repl": scramble(k),
        "params": new_params
    }

with open('../function_mapping.json', 'w') as outfile:
    json.dump(new_mapping, outfile)


json_formatted = json.dumps(new_mapping, indent=2)
print(json_formatted)
