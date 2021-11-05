
class Progress:
    def __init__(self, message):
        self.done = " \033[32;1m\N{check mark}\033[0m"
        self.symbols = '|/-\\'
        self.current_index = 0
        self.spaces = '  '

        print(f'\n{message} {self.progress_number()}{self.spaces}', sep='', end='', flush=True)

    def progress_number(self):
        return f'({self.current_index:3})'

    def progress(self):
        # how much is there to delete
        backspaces = '\b' * (len(self.progress_number()) + len(self.spaces))

        self.current_index += 1
        symbol = self.symbols[self.current_index % len(self.symbols)]

        print(f'{backspaces}{self.progress_number()} {symbol}', sep='', end='', flush=True)

    def end(self):
        print(f'\b{self.done}', sep='', flush=True)



