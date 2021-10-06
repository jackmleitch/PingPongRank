import pandas as pd
import config

columnNames = ["name", "rating"]
dfPlayers = pd.DataFrame(columns = columnNames)
dfPlayers.loc[0] = ["Jack", 1000]
dfPlayers.loc[1] = ["Henry", 1000]
dfPlayers.to_csv(config.PLAYERS_FILEPATH)