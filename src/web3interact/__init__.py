from IPython import embed
from traitlets.config import get_config


def main():
    c = get_config()
    c.InteractiveShellEmbed.colors = "Linux"
    embed(config=c)
