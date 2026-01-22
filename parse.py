import ast 
def parse_code(code_string):
    try:
        tree=ast.parse(code_string)
        return {
            "success":True,
            "tree":tree
        }
    except SyntaxError as e:
        return{
            "success":False,
            "error":{
                "type":"SyntaxError",
                "line":e.lineno,
                "message":e.msg,
                "text":e.text.strip() if e.text else ""
            }
        }