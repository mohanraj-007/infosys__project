import ast
class ErrorFinder(ast.NodeVisitor):
    def __init__(self):
        self.errors = []
        self.def_var = {}
        self.use_var = set()
    def visit_Assign(self, node):
        for tar in node.targets:
            if isinstance(tar, ast.Name):
                self.def_var[tar.id] = node.lineno
        self.generic_visit(node)
    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.use_var.add(node.id)
        self.generic_visit(node)
    def find_unused_variables(self):
        for var, line in self.def_var.items():
            if var not in self.use_var:
                self.errors.append({
                    "type": "UnusedVariable",
                    "message": f"Variable '{var}' is never used",
                    "suggestion": f"Remove '{var}' or use it somewhere",
                    "severity": "Warning",
                    "line": line
                })
        return self.errors
def detect_errors(code_string):
    try:
        tree = ast.parse(code_string)
        finder = ErrorFinder()
        finder.visit(tree)
        errors = finder.find_unused_variables()
        return {
            "success": True,
            "errors": errors,
            "error_count": len(errors)
        }
    except SyntaxError:
        return {
            "success": False
        }
