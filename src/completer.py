from collections import OrderedDict
from prompt_toolkit.completion import Completer, Completion


ROOT_COMMANDS = OrderedDict([
    ('cd', 'Change URL/path'),
    ('mode', 'Exit HTTP Prompt'),
    ('get', 'Clear console screen'),
    ('post', 'Preview curl command'),
    ('put', 'Print environment'),
    ('delete', 'Clear and load environment from a file'),
    ('send', 'Preview HTTPie command'),
    ('help', 'List commands, actions, and HTTPie options')
])


class NetSuitePromptCompleter(Completer):
    def get_completions(self, document, complete_event):
        for word in ROOT_COMMANDS:
            yield Completion(word, start_position=0)
