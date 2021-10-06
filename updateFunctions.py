from google.cloud import bigquery
import os

from bigqueryClient import *

import streamlit as st

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google_creds.json"


def update_all(client, person1, person2, winner):
    update_rankings(client, person1, person2, winner)
    ranks = rankings(client)
    update_history(client, ranks)
    update_game_history(client, person1, person2, winner)
    print("UPDATED ALL")


def go_back_all(client):
    revert_back_rankings(client)
    delete_previous_game_history(client)
    delete_previous_history(client)


def match_history_display(client, limit=5):
    my_query = f"""
               SELECT player1, player2, winner
               FROM `pingpong-322517.PingPong.history`
               ORDER BY id DESC
               LIMIT {limit}
               """
    game_history = client.query(my_query).to_dataframe()
    return game_history


def add_name(client, name, names):
    if name in names:
        st.error(
            f"{name} is already in the system! Use the lookup to see rank and games played."
        )
    else:
        add_name_current_rank(client, name)
        add_name_history(client, name)


def delete_name(client, name, names):
    if name in names:
        remove_name_current_rank(client, name)
        remove_name_history(client, name)
    else:
        st.error(f"{name} is not in the system!")


if __name__ == "__main__":
    client = bigquery.Client()
    go_back_all(client)
    # update_all(client, "Jack", "Logan", "Jack")

    ranks = rankings(client)
    hist = history(client)
    game_hist = game_history(client)

    print(ranks)
    print(hist)
    print(game_hist)
