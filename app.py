import streamlit as st
import numpy as np
import pandas as pd
import os

from PIL import Image

from updateFunctions import *
from bigqueryClient import *

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google_creds.json"

st.markdown(
    "# Boise State's Official and Definitive Ping Pong Rankings :crown: :trophy:"
)

# load up big query client
client = bigquery.Client()

# load up rankings
if "ranks" not in st.session_state:
    st.session_state["ranks"] = rankings(client)

if "names" not in st.session_state:
    st.session_state["names"] = st.session_state.ranks["name"].tolist()

if "game_history_display" not in st.session_state:
    st.session_state["game_history_display"] = match_history_display(client)

# if "ranking_history" not in st.session_state:
#     st.session_state["ranking_history"] = history(client)

if "table" not in st.session_state:
    ranks_disp = st.session_state.ranks.loc[st.session_state.ranks["games"] >= 10]
    ranks_disp.index = np.arange(1, len(ranks_disp) + 1)
    ranks_disp.index = np.arange(1, len(ranks_disp) + 1)
    st.session_state["table"] = ranks_disp.style.apply(
        lambda x: [
            "background: gold"
            if x.name == 1
            else (
                "background: silver"
                if x.name == 2
                else ("background: saddlebrown" if x.name == 3 else "")
            )
            for i in x
        ],
        axis=1,
    )

with st.container():
    table = st.table(st.session_state["table"])
    # _, _, _, col, _, _, _ = st.columns(7)
    # with col:
    #     st.button("Reload rankings")
    st.button("Reload rankings")

with st.expander("Lookup Player Stats"):
    select_name = st.selectbox("Select plater", st.session_state.names)
    if st.button("Lookup plater statistics"):
        stats = stats_lookup(client, select_name)
        st.table(stats)

with st.expander("Most Recent 5 Games"):
    # st.markdown("## Most Recent 5 Games :ledger:")
    if "game_history_display" not in st.session_state:
        st.session_state["game_history_display"] = match_history_display(client)
    # st.write(st.session_state["game_history_display"])
    count = 0
    for index, row in st.session_state["game_history_display"].iterrows():
        count += 1
        person1, person2, winner = row["player1"], row["player2"], row["winner"]
        if person1 == winner:
            loser = person2
        else:
            loser = person1
        st.markdown(f"{count}) **{winner}** :crown: vs. {loser} :cry:")

with st.expander("Head-To-Head"):
    st.markdown("## Head-to-head :rage:")
    with st.form(key="head2head"):
        person1 = st.selectbox("Player 1: ", st.session_state.names)
        person2 = st.selectbox("Player 2: ", st.session_state.names[::-1])
        submit_head2head = st.form_submit_button(label="Submit")
        if submit_head2head:
            if person1 == person2:
                st.error(
                    "You are your greatest rival. Future you will always be one step ahead."
                )
            else:
                results = head2head(client, person1, person2)
                # st.write(results)
                try:
                    win1 = results.loc[results["winner"] == person1].wins.iloc[0]
                except:
                    win1 = 0
                try:
                    win2 = results.loc[results["winner"] == person2].wins.iloc[0]
                except:
                    win2 = 0

                if win1 > win2:
                    st.markdown(f"**{person1}'s wins: {win1} :crown:**")
                    st.markdown(f"{person2}'s wins: {win2} :cry:")
                elif win2 > win1:
                    st.markdown(f"**{person2}'s wins: {win2} :crown:**")
                    st.markdown(f"{person1}'s wins: {win1} :cry:")
                else:
                    st.markdown(f"**{person1}'s wins: {win1} :crown:**")
                    st.markdown(f"**{person2}'s wins: {win2} :crown:**")


st.sidebar.markdown("## Enter Match Results :black_nib:")
with st.sidebar.form(key="match_result"):
    winner = st.selectbox("Winner: ", st.session_state.names)
    loser = st.selectbox("Loser: ", st.session_state.names[::-1])
    submitted = st.form_submit_button(label="Submit")
    # with st.spinner("Loading Model"):
    if submitted:
        if winner == loser:
            pass
        else:
            update_all(client, winner, loser, winner)
            del st.session_state["ranks"]
            del st.session_state["table"]
            del st.session_state["game_history_display"]


with st.sidebar.expander("Delete game"):
    delete_button = st.button("Delete last game entered")
    if delete_button:
        st.session_state["delete"] = True
    if "delete" in st.session_state:
        to_be_deleted = st.session_state["game_history_display"].iloc[0].tolist()
        st.error(
            f"Do you really, really, wanna delete game between {to_be_deleted[0]} and {to_be_deleted[1]}?"
        )
        if st.button("Yes, do it!"):
            go_back_all(client)
            del st.session_state["delete"]
            del st.session_state["ranks"]
            del st.session_state["table"]
            del st.session_state["game_history_display"]

with st.sidebar.expander("Add Player"):
    player_to_add = st.text_input("Enter player here")
    if st.button("Add player"):
        # with st.spinner("Loading Model"):
        add_name(client, player_to_add, st.session_state.names)
        del st.session_state["ranks"]
        del st.session_state["table"]
        del st.session_state["game_history_display"]
        del st.session_state["names"]

with st.sidebar.expander("Delete Player"):
    delete_name_input = st.text_input("Enter player to delete here")
    if delete_name_input:
        st.session_state["delete_name"] = True
    if "delete_name" in st.session_state:
        st.error(
            f"Do you really, really, wanna delete {delete_name_input}? This is permanent."
        )
        if st.button("Yes, do it!"):
            delete_name(client, delete_name_input, st.session_state.names)
            del st.session_state["delete_name"]
            del st.session_state["ranks"]
            del st.session_state["table"]
            del st.session_state["game_history_display"]
            del st.session_state["names"]

# with st.expander("Ranking History"):
#     # st.write(st.session_state.ranking_history)
#     games_to_filter = st.slider(
#         "How many games to show?",
#         1,
#         st.session_state.ranking_history.shape[0],
#         st.session_state.ranking_history.shape[0],
#     )
#     names_slider = st.multiselect("Who to show on graph?", st.session_state.names)
#     plot_ranks(
#         st.session_state.ranking_history, names=names_slider, scale=games_to_filter
#     )

with st.expander("Leadville House Rules"):
    st.write(
        "Games will be played to 11 best of 3 or 5 whichever is agreed upon before the game starts"
    )
    st.markdown(" ### Service :dart:")
    st.markdown(
        "* Serves switch every 3 points, unless it’s game point - then serve goes to whoever is losing and they are allowed unlimited serving errors when they are facing game point."
    )
    st.markdown("* Serves don’t have to land in a specific quadrant. ")
    st.markdown("* If a serve hits the net it's a “let” which is a redo.")
    st.markdown(
        "* Serves should be thrown at least 6 inches into the air from an open palm. They are then to be struck by the paddle onto your own side, over the net and onto the opponents side."
    )
    st.markdown("### Play :arrow_forward:")
    st.markdown(
        "* You are allowed to play off of any object including, but not limited to, the rafters, bike, chairs. It just can’t hit the ground first."
    )
    st.markdown(
        "* If you strike the ball with your paddle before it strikes your side of the table the point goes to your opponent. This rule is within reason, if it’s miles from hitting the table and you use your paddle to save it from going under the cars there can be exceptions."
    )
    st.markdown("* The ball may go around or through the gap in the net.")
    st.markdown(
        "* The ball can play off of the net in normal play. It’s only a redo during service."
    )
    st.markdown(
        "* The ball hitting the edge of the table counts as in play. It’s ruled out if it clearly hits the side or bottom of the table (if this somehow happens)."
    )
    st.markdown("* You cannot return the ball with anything but your paddle.")
    st.markdown(
        "* If the ball bounces on your side and back to your opponents side without you touching it the point goes to your opponent."
    )

    st.markdown(" ## How are the rankings calculated? :straight_ruler:")
    st.markdown(
        "* The Elo Rating System (Elo) is a rating system used for rating players in games. Originally developed for chess by Arpad Elo, Elo has been applied to a large array of games."
    )
    st.markdown(
        "* Each player is assigned a number as a rating (base rating is 1000). The system predicts the outcome of a match between two players by using an expected score formula (i.e. a player whose rating is 100 points greater than their opponent's is expected to win 64% of the time)."
    )
    st.markdown(
        "* Everytime a game is played, the Elo rating of the participants change depending on the outcome and the expected outcome. The winner takes points from the loser; the amount is determined by the players' scores and ratings."
    )

st.text("")
st.text("")
st.text("")
st.markdown("App created by [Jack Leitch](https://github.com/jackmleitch) :frog:")
