import configparser
import os


def buildconfig():
    path = '{}/{}'.format(os.path.dirname(os.path.realpath(__file__)), 'config.cfg')
    config = configparser.ConfigParser()
    config.read(path)
    return config
