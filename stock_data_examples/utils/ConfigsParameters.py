import configparser
import os

def get_configs():
    config_filepath = os.path.join(os.path.dirname(__file__), '../..', "config/config.ini")
    Config = configparser.ConfigParser()
    Config.read(config_filepath)
    configs1 = ConfigSectionMap(Config, "Internal")
    configs2 = ConfigSectionMap(Config, "ExternalAPI")
    configs = dict(list(configs1.items()) + list(configs2.items()))

    return configs

# loads configuration section and returns properties as dictionary
def ConfigSectionMap(Config, section):
    dict1 = {}
    options = Config.options(section)
    for option in options:

        # if config should be a string with working directory path as prefix
        if option in ["stocks_filepath",
                        "persisted_objects_folderpath",
                        "output_folderpath"
                        ]:
            try:
                dict1[option] = os.path.join(os.path.dirname(__file__), '../..', Config.get(section, option))
            except:
                print("exception on %s!" % option)
                dict1[option] = None

        # if it shall be an absolute filepath / string
        elif option in ["alpha_vantage_key",
                        ]:
            try:
                dict1[option] = Config.get(section, option)
                if dict1[option] == -1:
                    print("skip: %s" % option)
            except:
                print("exception on %s!" % option)
                dict1[option] = None

        # if should be a boolean
        elif option in ["save_to_database",
                        "save_to_filesystem"]:
            try:
                dict1[option] = Config.getboolean(section, option)
            except:
                print("exception on %s!" % option)
                dict1[option] = None

        # in all other cases: just return full string
        else:
            try:
                dict1[option] = Config.get(section, option)
                if dict1[option] == -1:
                    print("skip: %s" % option)
            except:
                print("exception on %s!" % option)
                dict1[option] = None
    return dict1

configs = get_configs()