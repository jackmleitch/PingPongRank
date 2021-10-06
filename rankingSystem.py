import pandas as pd
import config
import numpy as np


def compareRating(df, name1, name2):
    """
    Compares the two ratings of a player and an opponent.
    :param df: Pandas DataFrame with players and rating
    :param name1/name2: The two names of the players
    :return: The expected score between the two players.
    """
    rating1 = df.loc[df["name"] == name1, "rating"].iloc[0]
    rating2 = df.loc[df["name"] == name2, "rating"].iloc[0]
    return (1 + 10 ** ((rating2 - rating1) / 400.0)) ** -1


def getPlayerList(df):
    """
    :param df: Pandas DataFrame with players and ratings
    :return: the list of all players in the system
    """
    return df["name"].tolist()


def contains(df, name):
    """
    :param df: Pandas DataFrame with players and ratings
    :param name: name to check for
    :return: True if system contains player, otherwise False
    """
    players = getPlayerList(df)
    return name in players


# def addPlayer(df, name, rating=None):
#     """
#     Adds a new player to the system
#     :param df: Pandas DataFrame with players and ratings
#     :param name: The name to identify a specific player
#     :param rating: The player's rating
#     """
#     if rating == None:
#         rating = config.BASE_RATING
#     tooAdd = pd.Series([name, rating, 0], index=df.columns)
#     df = df.append(tooAdd, ignore_index=True)
#     return df


def removePlayer(df, name):
    """
    Removes player from the system
    :param df: Pandas DataFrame with players and ratings
    :param name: The name to identify the specific player
    """
    if name in getPlayerList(df):
        df = df[df.name != name]
    return df


def recordMatch(df, name1, name2, winner=None):
    """
    This is called to record the results of a match
    :param df: Pandas DataFrame with players and ratings
    :param name1/name2: - name of the first/second player
    :param winner: The player the won the match
    """

    expected1 = compareRating(df, name1, name2)
    expected2 = compareRating(df, name2, name1)

    k = 42

    rating1 = getPlayerRating(df, name1)
    rating2 = getPlayerRating(df, name2)

    if winner == name1:
        score1 = 1.0
        score2 = 0.0
    elif winner == name2:
        score1 = 0.0
        score2 = 1.0
    else:
        raise InputError("One of the names must be the winner")

    newRating1 = int(rating1 + k * (score1 - expected1))
    newRating2 = int(rating2 + k * (score2 - expected2))

    if newRating1 < 0:
        newRating1 = 0
        newRating2 = rating2 - rating1

    elif newRating2 < 0:
        newRating2 = 0
        newRating1 = rating1 - rating2

    # df = updatePlayerRating(df, name1, newRating1)
    # df = updatePlayerRating(df, name2, newRating2)
    return newRating1, newRating2


def getPlayerRating(df, name):
    """
    Returns the rating of the player with the given name.
    :param df: Pandas DataFrame with players and ratings
    :param name: name of the player
    :return: the rating of the player with the given name
    """
    return df.loc[df["name"] == name, "rating"].iloc[0]


def updatePlayerRating(df, name, newRating):
    """
    Updates the rating of player
    :param df: Pandas DataFrame with players and ratings
    :param name: name of the player
    :param newRating: the new rating of the player
    """
    df.loc[df["name"] == name, "rating"] = int(newRating)
    df.loc[df["name"] == name, "games"] = df.loc[df["name"] == name, "games"] + 1
    return df


def getRankings(df):
    return df["rating"].tolist()
