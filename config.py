import yaml

with open('config/config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)
