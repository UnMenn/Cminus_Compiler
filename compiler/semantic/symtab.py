class ProgramContext:
    def __init__(self):
        self.globals = {}

        self.functions = {}

        self.current_function = None

        self.scope_stack = [self.globals]

    def push_scope(self, scope=None):
        if scope is None:
            scope = {}
        self.scope_stack.append(scope)
        return scope

    def pop_scope(self):
        if len(self.scope_stack) > 1:
            self.scope_stack.pop()

    def insert(self, name, info):
        """
        Inserts into current scope.
        """
        self.scope_stack[-1][name] = info

    def lookup(self, name):

        for scope in reversed(self.scope_stack):
            if name in scope:
                return scope[name]

        return self.globals.get(name, None)

    def add_function(self, name, info):
        self.functions[name] = info

    def get_function(self, name):
        return self.functions.get(name, None)
