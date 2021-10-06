from google.cloud import bigquery
import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
from rankingSystem import recordMatch

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google_creds.json"


def rankings(client, display=False):
    """
    Returns player rankings with games >= 10
    :param client: A Client object that specifies the connection to the dataset
    :return: player rankings
    """
    if display:
        my_query = """
                SELECT *
                FROM `pingpong-322517.PingPong.current_rank`
                WHERE games >= 10
                ORDER BY rating DESC
                """
    else:
        my_query = """
                SELECT *
                FROM `pingpong-322517.PingPong.current_rank`
                ORDER BY rating DESC
                """
    # Set up the query
    safe_config = bigquery.QueryJobConfig(maximum_bytes_billed=10 ** 10)
    my_query_job = client.query(my_query, job_config=safe_config)

    # API request - run the query, and return a pandas DataFrame
    results = my_query_job.to_dataframe()
    print("Rankings loaded")
    return results


def game_history(client):
    my_query = """
               SELECT *
               FROM `pingpong-322517.PingPong.history`
               ORDER BY id DESC
               """
    game_history = client.query(my_query).to_dataframe()
    return game_history


def head2head(client, player1, player2):
    """
    Returns a head-to-head of the two specified players
    :param client: A Client object that specifies the connection to the dataset
    :param player1/player2: String, names of players to compare
    :return: Head-to-head of two players
    """

    players = [player1, player2]
    players = sorted(players)
    player1, player2 = players[0], players[1]

    my_query = """
               WITH filter AS 
               (
               SELECT *
               FROM `pingpong-322517.PingPong.history`
               WHERE player1 = '{}' AND player2 = '{}'
               ORDER BY id
               )
               SELECT winner, COUNT(winner) AS wins
               FROM filter
               GROUP BY winner
               """.format(
        player1, player2
    )

    # Set up the query
    safe_config = bigquery.QueryJobConfig(maximum_bytes_billed=10 ** 10)
    my_query_job = client.query(my_query, job_config=safe_config)

    # API request - run the query, and return a pandas DataFrame
    results = my_query_job.to_dataframe()

    return results


def history(client):
    """
    Returns player ranking history
    :param client: A Client object that specifies the connection to the dataset
    :return: player ranking history
    """

    my_query = """
               SELECT *
               FROM `pingpong-322517.PingPong.ranking_history`
               ORDER BY id DESC
               """

    # Set up the query
    safe_config = bigquery.QueryJobConfig(maximum_bytes_billed=10 ** 10)
    my_query_job = client.query(my_query, job_config=safe_config)

    # API request - run the query, and return a pandas DataFrame
    results = my_query_job.to_dataframe()

    return results


def plot_ranks(points_history, names=False, scale=False):

    sns.set_style("white")
    sns.set_palette("rainbow")

    points_history = points_history.replace(0, np.nan)
    df = points_history.drop("id", axis=1)
    if not names:
        names = df.columns.tolist()
    if scale:
        df = df.head(scale)
    df = df[names]
    df = df.iloc[::-1]
    df = df.reset_index(drop=True)
    df["Total games played"] = df.index
    df = df.apply(pd.to_numeric, errors="coerce")
    # Make a plot
    fig, ax = plt.subplots()
    # Add lines to it
    data_plot = pd.melt(df, ["Total games played"])
    data_plot.rename(columns={"value": "Ranking score"}, inplace=True)
    sns.lineplot(
        x="Total games played", y="Ranking score", hue="variable", data=data_plot
    )
    ax.get_legend().remove()
    # Add the text--for each line, find the end, annotate it with a label, and
    # adjust the chart axes so that everything fits on.
    for line, name in zip(ax.lines, names):
        y = line.get_ydata()[-1]
        x = line.get_xdata()[-1]
        if not np.isfinite(y):
            y = next(reversed(line.get_ydata()[~line.get_ydata().mask]), float("nan"))
        if not np.isfinite(y) or not np.isfinite(x):
            continue
        text = ax.annotate(
            name,
            xy=(x, y),
            xytext=(0, 0),
            color=line.get_color(),
            xycoords=(ax.get_xaxis_transform(), ax.get_yaxis_transform()),
            textcoords="offset points",
        )
        text_width = (
            text.get_window_extent(fig.canvas.get_renderer())
            .transformed(ax.transData.inverted())
            .width
        )
        if np.isfinite(text_width):
            ax.set_xlim(ax.get_xlim()[0], text.xy[0] + text_width * 1.05)
    st.pyplot(fig)


def update_rankings(client, person1, person2, winner):

    df = rankings(client)
    new_ranking_1, new_ranking_2 = recordMatch(df, person1, person2, winner)

    my_query1 = """
                UPDATE `pingpong-322517.PingPong.current_rank`
                SET rating = {}, games = games + 1
                WHERE name = '{}'
                """.format(
        new_ranking_1, person1
    )
    my_query2 = """
                UPDATE `pingpong-322517.PingPong.current_rank`
                SET rating = {}, games = games + 1
                WHERE name = '{}'
                """.format(
        new_ranking_2, person2
    )

    safe_config = bigquery.QueryJobConfig(maximum_bytes_billed=10 ** 10)

    my_query_job1 = client.query(my_query1, job_config=safe_config)
    my_query_job1.result()
    my_query_job2 = client.query(my_query2, job_config=safe_config)
    my_query_job2.result()

    print(f"Rankings updated for game between {person1} and {person2}")


def update_history(client, ranks):

    names = ranks.name.tolist()
    names.append("id")
    columns_query = ", ".join(names)

    rank_vals = ranks.rating.tolist()
    # rank_vals.append(hist.id.max() + 1)
    string_rank = [str(num) for num in rank_vals]
    rank_query = ", ".join(string_rank)

    my_query = f"""
                INSERT INTO `pingpong-322517.PingPong.ranking_history` ({columns_query})
                VALUES ({rank_query}, (SELECT MAX(id)+1 FROM `pingpong-322517.PingPong.ranking_history`))
                """
    hist_update = client.query(my_query)
    hist_update.result()

    print(f"Rankings history updated")


def update_game_history(client, person1, person2, winner):
    my_query = """
               SELECT *
               FROM `pingpong-322517.PingPong.history`
               """

    game_hist = game_history(client)
    idx_to_add = game_hist.id.max() + 1

    update = f"{idx_to_add}, '{person1}', '{person2}', '{winner}'"
    my_update_query = f"""
                      INSERT INTO `pingpong-322517.PingPong.history` (id, player1, player2, winner)
                      VALUES ({update})
                      """
    game_history_update = client.query(my_update_query)
    game_history_update.result()

    print(f"Rankings updated for game between {person1} and {person2}")


def delete_previous_game_history(client):
    game_hist = game_history(client)
    idx_to_delete = game_hist.id.max()

    my_query = f"""
                DELETE FROM `pingpong-322517.PingPong.history`
                WHERE id = {idx_to_delete}
                """

    safe_config = bigquery.QueryJobConfig(maximum_bytes_billed=10 ** 10)
    my_query_job = client.query(my_query, job_config=safe_config)
    print(f"Deleted column with id = {idx_to_delete}")


def delete_previous_history(client):
    hist = history(client)
    idx_to_delete = hist.id.max()

    my_query = f"""
                DELETE FROM `pingpong-322517.PingPong.ranking_history`
                WHERE id = {idx_to_delete}
                """

    safe_config = bigquery.QueryJobConfig(maximum_bytes_billed=10 ** 10)
    my_query_job = client.query(my_query, job_config=safe_config)
    print(f"Deleted column with id = {idx_to_delete}")


def revert_back_rankings(client):

    # get newly updated game result
    recent_game = game_history(client)
    recent_game = recent_game.loc[recent_game["id"] == recent_game.id.max()]
    names_to_update = recent_game.values.tolist()[0][1:-1]

    # get old scores
    hist = history(client)
    idx_to_update = hist.id.max() - 1
    old_scores = hist.loc[hist["id"] == idx_to_update].to_dict("records")[0]

    my_query1 = f"""
               UPDATE `pingpong-322517.PingPong.current_rank`
               SET rating = {old_scores[names_to_update[0]]}, games = games - 1
               WHERE name = '{names_to_update[0]}'
               """
    my_query2 = f"""
            UPDATE `pingpong-322517.PingPong.current_rank`
            SET rating = {old_scores[names_to_update[1]]}, games = games - 1
            WHERE name = '{names_to_update[1]}'
            """
    safe_config = bigquery.QueryJobConfig(maximum_bytes_billed=10 ** 10)
    my_query_job = client.query(my_query1, job_config=safe_config)
    my_query_job = client.query(my_query2, job_config=safe_config)
    print(f"Reverted scores")


def add_name_current_rank(client, name):
    my_query = f"""
                    INSERT INTO `pingpong-322517.PingPong.current_rank` (name, rating, games)
                    VALUES ('{name}', 1000, 0)
                    """
    safe_config = bigquery.QueryJobConfig(maximum_bytes_billed=10 ** 10)
    my_query_job = client.query(my_query, job_config=safe_config)
    my_query_job.result()
    print(f"Added {name} to current_rank")


def add_name_history(client, name):
    my_query = f"""
               ALTER TABLE `pingpong-322517.PingPong.ranking_history`
               ADD COLUMN {name} integer
               """
    safe_config = bigquery.QueryJobConfig(maximum_bytes_billed=10 ** 10)
    my_query_job = client.query(my_query, job_config=safe_config)
    my_query_job.result()
    print(f"Added {name} to ranking_history")


def remove_name_current_rank(client, name):
    my_query = f"""
                DELETE FROM `pingpong-322517.PingPong.current_rank`
                WHERE name = '{name}'
                """
    safe_config = bigquery.QueryJobConfig(maximum_bytes_billed=10 ** 10)
    my_query_job = client.query(my_query, job_config=safe_config)
    my_query_job.result()
    print(f"Deleted {name} from current_rank")


def remove_name_history(client, name):
    my_query = f"""
                ALTER TABLE `pingpong-322517.PingPong.ranking_history`
                DROP COLUMN IF EXISTS {name}
                """
    safe_config = bigquery.QueryJobConfig(maximum_bytes_billed=10 ** 10)
    my_query_job = client.query(my_query, job_config=safe_config)
    my_query_job.result()
    print(f"Deleted {name} from ranking_history")


def stats_lookup(client, name):
    my_query = f"""
                SELECT *
                FROM `pingpong-322517.PingPong.current_rank`
                WHERE name = '{name}'
                """
    safe_config = bigquery.QueryJobConfig(maximum_bytes_billed=10 ** 10)
    my_query_job = client.query(my_query, job_config=safe_config)
    return my_query_job.result().to_dataframe()


if __name__ == "__main__":
    client = bigquery.Client()

    # update rank
    # update_rankings(client, "Henry", "Luis", "Henry")
    # print(rankings(client, display=False))

    # update history
    hist = history(client)
    print(hist)
    ranks = rankings(client)
    update_history(client, ranks, hist)
    print(history(client))

    # # rankings
    # ranking = rankings(client)
    # print(ranking)

    # # head-to-head
    # head = head2head(client, "Logan", "Jack")
    # print(head)

    # # history
    # hist = history(client)
    # print(hist)
