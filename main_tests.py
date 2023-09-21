import configparser, os, logging, time
# import main

logging.basicConfig(format='{"timestamp":"%(asctime)s", "level":"%(levelname)s", "message": "%(message)s"}', level=logging.INFO)


def getConfig():
    config = configparser.ConfigParser()
    logging.info("Setting environment variables...")
    print(os.getcwd())
    try:
        logging.info("Reading environment variables from config file.")
        config.read('test.ini')
        discordToken = config['discord']['token']
        discordGuild = config['discord']['guild-id']
        nasaKey = config['nasa']['api-key']
        plexKey = config['plex']['token']
    except:
        print("No config file found, Please input environment variables.")
        discordToken = input("Discord Token:")
        discordGuild = input("Discord Guild ID:")
        nasaKey = input("Nasa API-Key:")
        plexKey = input("Plex Token:")

    return discordToken, discordGuild, nasaKey, plexKey

def setEnvars():
    discordToken, discordGuild, nasaKey, plexKey = getConfig()
    os.environ["DISCORD_TOKEN"] = discordToken
    os.environ["DISCORD_GUIDE_ID"] = discordGuild
    os.environ["NASA_KEY"] = nasaKey
    os.environ["PLEX_TOKEN"] = plexKey

# def test():
#     if main:
#         print("tests passed")

# if __name__ == "__main__":
#     setEnvars()
#     time.sleep(5)
#     main