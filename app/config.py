import os

if os.path.exists('.env'):
    print('Importing environment from .env...')
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]


class Config(object):

    def __init__(self):
        self.data = {}
        self.data['VERSION'] = os.getenv('VERSION', 'v1')
        self.data['SERVER'] = os.getenv('SERVER', '127.0.0.1')
        self.data['PORT'] = int(os.getenv('PORT', 8000))
        self.data['PROTOCOL'] = os.getenv('PROTOCOL', 'http')

    def __getitem__(self, key):
        return self.data[key]
