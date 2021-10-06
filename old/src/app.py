import streamlit as st
import numpy as np
import pandas as pd

pd.options.mode.chained_assignment = None

from PIL import Image
import tweepy
import io

import config
from ratingSystem import *
from tweetData import connectTwitter
from history import get_names, plot_ranks, update_points

import SessionState

# session_state = SessionState.get(plot_history=True, points_history="")

st.markdown(
    "# Boise State's Official and Definitive Ping Pong Rankings :crown: :trophy:"
)

twitter = connectTwitter()
df = twitter.fetchRankings()
df = df.sort_values(by=["rating"], ascending=False, ignore_index=True)
df_disp = df.loc[df["games"] >= 10]
df.index = np.arange(1, len(df) + 1)
df_disp.index = np.arange(1, len(df_disp) + 1)

dfColour = df_disp.style.apply(
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

with st.beta_container():
    table = st.table(dfColour)
    st.button("Reload rankings")


@st.cache
def head2head(points_history, person1, person2):
    df = points_history[[person1, person2]]

    # df[f"{person1}_diff"] = df[person1].shift(-1)
    # df[f"{person2}_diff"] = df[person2].shift(-1)
    df[person1] = df[person1] - df[person1].shift(-1)
    df[person2] = df[person2] - df[person2].shift(-1)
    win1 = 0
    win2 = 0
    for index, row in df.iterrows():
        if row[person1] == 0 or row[person2] == 0:
            continue
        elif row[person1] > 0 and row[person2] < 0:
            win1 += 1
        elif row[person1] < 0 and row[person2] > 0:
            win2 += 1
        else:
            continue
    return win1, win2


st.write(
    "Match results can be added between two ranked players in the sidebar (make sure to click 'Reload rankings' afterwards). You can also add players, remove players and adjust player ratings (admin only). To see a complete history of ranking updates [click here](https://twitter.com/BoisePing/)"
)


@st.cache
def get_full_history():
    twitter = connectTwitter()
    history, count = twitter.fetchRankingsMulti()
    names = get_names(history)
    points_history = pd.DataFrame(columns=names)
    for i in range(0, count - 174):
        data = pd.read_csv(io.StringIO(history[i].full_text), sep=" ")
        update_points(data, points_history, names, i)
    return points_history


# if session_state.plot_history:
#     session_state.points_history = get_full_history(twitter)
#     session_state.plot_history = False
st.write("")
points_history = get_full_history()
total_games = points_history.shape[0]
names = points_history.columns.tolist()

st.markdown("## Head-to-head :rage:")
col1, col2 = st.beta_columns(2)
with col1:
    person1 = st.selectbox("Person 1", names)
with col2:
    person2 = st.selectbox("Person 2", names[::-1])
win1, win2 = head2head(points_history, person1, person2)
if win1 > win2:
    st.markdown(f"**{person1}'s wins: {win1} :crown:**")
    st.markdown(f"{person2}'s wins: {win2} :cry:")
elif win2 > win1:
    st.markdown(f"**{person2}'s wins: {win2} :crown:**")
    st.markdown(f"{person1}'s wins: {win1} :cry:")
else:
    st.markdown(f"**{person1}'s wins: {win1} :crown:**")
    st.markdown(f"**{person2}'s wins: {win2} :crown:**")

st.write("")

st.markdown("##  Rating History :scroll:")

games_to_filter = st.slider("How many games to show?", 1, total_games, total_games)
names_slider = st.multiselect("Who to show on graph?", names)
plot_ranks(points_history, names=names_slider, scale=games_to_filter)

st.write("")

with st.beta_expander("Leadville House Rules"):
    # st.markdown(" ## Leadville House Rules :house:")
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


st.sidebar.subheader("Enter match results")
player1 = st.sidebar.selectbox("Name of player 1: ", getPlayerList(df))

player2 = st.sidebar.selectbox("Name of player 2: ", getPlayerList(df))

winner = st.sidebar.selectbox("Who won the match?", [player1, player2])

if st.sidebar.button("Update rankings"):
    df = recordMatch(df, player1, player2, winner)
    df = df.sort_values(by=["rating"], ascending=False, ignore_index=True)
    toTweet = df.to_csv(sep=" ", index=True, header=True)
    twitter.updateRankings(toTweet)
    st.sidebar.button("Reload rankings!")

with st.sidebar.beta_expander("Add new player"):
    newPlayer = st.text_input("Add new player name here: ")
    if st.button("Add player"):
        df = addPlayer(df, newPlayer)
        df = df.sort_values(by=["rating"], ascending=False, ignore_index=True)
        toTweet = df.to_csv(sep=" ", index=True, header=True)
        twitter.updateRankings(toTweet)

with st.sidebar.beta_expander("Remove player"):
    removeName = st.selectbox("What player do you want removed?", getPlayerList(df))
    if st.button("Remove player"):
        df = removePlayer(df, removeName)
        df = df.sort_values(by=["rating"], ascending=False, ignore_index=True)
        toTweet = df.to_csv(sep=" ", index=True, header=True)
        twitter.updateRankings(toTweet)

with st.sidebar.beta_expander("Update player rating"):
    player = st.selectbox("Name of player: ", getPlayerList(df))
    newRating = st.text_input("Add new player rating here: ")
    if st.button("Change ranking"):
        df = updatePlayerRating(df, player, newRating)
        df = df.sort_values(by=["rating"], ascending=False, ignore_index=True)
        toTweet = df.to_csv(sep=" ", index=True, header=True)
        twitter.updateRankings(toTweet)

st.text("")
st.text("")
st.text("")
st.markdown("App created by [Jack Leitch](https://github.com/jackmleitch) :frog:")


col1, col2, col3, col4 = st.beta_columns(4)
with col2:
    image = Image.open("./input/bronco.png")
    st.image(image)
