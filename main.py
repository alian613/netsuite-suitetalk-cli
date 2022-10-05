#from prompt_toolkit import prompt
from enum import Enum
from collections import namedtuple
from src.completer import NetSuitePromptCompleter
from src.suitetalk import (SuiteTalk, RESTMethod, HTTPMethod)
import click
import re
import atexit


@click.command()
@click.option('-alg',
              type=click.Choice(
                  ['PS256', 'PS284', 'PS512', 'RS256', 'RS384', 'RS512'], case_sensitive=False),
              required=False,
              default='PS256',
              help='the algorithm used for signing of the token, supports PS256, PS284, PS512, RS256, RS384, or RS512. default is PS256')
@click.option('-kid',
              type=str,
              required=True,
              prompt='Enter your Certificate ID: ',
              help='the Certificate ID generated during OAuth 2.0 Client Credential Setup of NetSuite')
@click.option('-iss',
              type=str,
              required=True,
              prompt='Enter your Integration Client ID: ',
              help='the client ID for the NetSuite Integration')
@click.option('-i',
              type=str,
              required=True,
              prompt='Enter your NetSuite Account ID: ',
              help='is your NetSuite account ID')
@click.option('-pk',
              type=str,
              required=True,
              nargs=2,
              prompt='Enter private key or path of private key file',
              help='''the private part of the certificate: b "-----BEGIN PRIVATE KEY-----\\n..........-----END PRIVATE KEY-----"\nthe path to the private part of the certificate: p "C:\certificat\private-key.pem"''')
@click.option('-p',
              type=str,
              required=False,
              help='the passphrase of the certificate')
@click.option('-cli',
              is_flag=True,
              required=False,
              help='enter interactive command line interface')
@click.option('--copy',
              is_flag=True,
              required=False,
              help='copy access token to clipboard')
@click.option('--get',
              type=str,
              required=False,
              multiple=True,
              help='send a GET request to this url,it can be multiple')
@click.option('--post',
              type=str,
              required=False,
              multiple=True,
              help='send a POST request to this url,it can be multiple')
@click.option('--put',
              type=str,
              required=False,
              multiple=True,
              help='send a PUT request to this url,it can be multiple')
@click.option('--delete',
              type=str,
              required=False,
              multiple=True,
              help='send a DELETE request to this url,it can be multiple')
def cli(alg, kid, iss, i, pk, p, copy, get, post, put, delete, cli):
    CLI_ARGS = namedtuple(
        'cli_args', ['alg', 'kid', 'iss', 'i', 'pk', 'p', 'copy', 'get', 'post', 'put', 'delete'])
    cli_args = CLI_ARGS(alg, kid, iss, i, pk, p, copy, get, post, put, delete)

    suitetalk = SuiteTalk(cli_args)

    api = {
        'method': 'POST',
        'domain': RESTMethod.RESTWEBSERVICE.value,
        'path': '',
        'url': f'http://{suitetalk.cli.i}.{RESTMethod.RESTWEBSERVICE.value}/',
        'token': suitetalk.access_token
    }
    if get:
        for url in get:
            api['method'] = HTTPMethod.GET.value
            api['url'] = url
            suitetalk.request_rest(api)
    if post:
        for url in post:
            api['method'] = HTTPMethod.POST.value
            api['url'] = url
            suitetalk.request_rest(api)
    if put:
        for url in put:
            api['method'] = HTTPMethod.PUT.value
            api['url'] = url
            suitetalk.request_rest(api)
    if delete:
        for url in delete:
            api['method'] = HTTPMethod.DELETE.value
            api['url'] = url
            suitetalk.request_rest(api)

    if (not get and not post and not put and not delete) or cli:
        cmd_prompt(api, suitetalk)


def cmd_prompt(api, suitetalk):
    cmd = ''
    ANSI = namedtuple(
        'ansi', ['GREENBG', 'GRAYBG', 'BOLD', 'RED', 'EOF'])
    ansi = ANSI('\33[42m', '\33[100m', '\033[1m', '\33[91m', '\033[0m')
    while cmd != 'exit':
        cmd = input(
            f'{ansi.BOLD}{ansi.GREENBG}{api["method"]}{ansi.EOF} : http://{suitetalk.cli.i}.{api["domain"]}/{api["path"]}>>> ')

        command = CommandRegex(cmd)
        if command.cd:
            api['path'] = command.get_path(api['path'])
        if command.mode and command.value.upper() in RESTMethod.__members__:
            api['domain'] = RESTMethod[command.value.upper()].value
        if command.method:
            api['method'] = command.get_method(cmd)
        if command.send:
            api['method'] = command.get_method(api['method'])
            api['url'] = f'http://{suitetalk.cli.i}.{api["domain"]}/{api["path"]}'
            suitetalk.request_rest(api)
        if command.ps:
            print(suitetalk.request_prepare(api))
        if command.help:
            help_commands = {
                'cd': 'Change URL/path',
                'mode': 'Change CompanyURL for RESTlet or RESTWebService',
                'get': 'HTTP method set to GET request',
                'post': 'HTTP method set to POST request',
                'put': 'HTTP method set to PUT request',
                'delete': 'HTTP method set to DELETE request',
                'send': 'send request, support http method then grep',
                'ps': 'preview request',
                'help': 'List cli mode commands, actions',
                'exit': 'exit suite prompt'
            }
            print('Command: ')
            for k, v in help_commands.items():
                print(f'    {k}: {v}')

        if not command.cd and not command.mode and not command.method and not command.send and not command.ps and not command.help and cmd != 'exit':
            print(
                f'{ansi.RED}Command is not found, please check{ansi.EOF} {ansi.GRAYBG}help{ansi.EOF}')


class CommandRegex:
    def __init__(self, cmd):
        self._cmd = cmd

    @ property
    def value(self):
        return re.search(r'\s.*', self._cmd).group()[1:] if re.search(r'\s.*', self._cmd) else ''

    @ property
    def cd(self):
        return re.search(r'^cd\s', self._cmd)

    def get_path(self, path):
        if re.search(r'^\.\.$', self.value):
            path = path[:path.rfind('/')]
        elif re.search(r'^\.\./.*', self.value):
            path = path[:path.rfind('/')] + self.value[2:]
        elif re.search(r'^./', self.value):
            path += self.value[1:]
        else:
            path = re.sub(r'^/', '', self.value)
        return path

    @ property
    def mode(self):
        return re.search(r'^mode\s', self._cmd)

    @ property
    def method(self):
        return self._cmd.upper() in HTTPMethod.__members__

    def get_method(self, v):
        return re.search(r'.*\s\|', self._cmd).group().upper()[:-2] if re.search(
            r'.*\s\|', self._cmd) and re.search(r'.*\s\|', self._cmd).group().upper()[:-2] in HTTPMethod.__members__ else v.upper()

    @ property
    def ps(self):
        return re.search(r'(^ps)', self._cmd)

    @ property
    def send(self):
        return re.search(r'(\|\ssend)|(\|send)|(^send)', self._cmd)

    @ property
    def help(self):
        return self._cmd.lower() == 'help'


def main():
    """
    @author alvin_wu
    """
    atexit.register(lambda: print('Adiós ~ '))
    cli()


if __name__ == '__main__':
    main()
