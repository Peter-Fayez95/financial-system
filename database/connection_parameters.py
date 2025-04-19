import configparser


def get_database_parameters(file_name):
    config = configparser.ConfigParser()
    config.read(file_name)

    return config
