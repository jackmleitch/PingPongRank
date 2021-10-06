import tweepy
import io

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st

from tweetData import connectTwitter
import config


def update_points(df, points_history, names, i):
    for name in names:
        try:
            rank = df.loc[df["name"] == name].rating.values[0]
        except:
            rank = 0
        points_history.loc[i, name] = rank


def get_names(history):
    init_data = pd.read_csv(io.StringIO(history[0].full_text), sep=" ")
    # init_data_filt = init_data.loc[init_data.games > 9]
    names = init_data.name.values.tolist()
    return names


def get_full_history(twitter):
    history, count = twitter.fetchRankingsMulti()
    names = get_names(history)
    points_history = pd.DataFrame(columns=names)
    for i in range(0, count - 174):
        data = pd.read_csv(io.StringIO(history[i].full_text), sep=" ")
        update_points(data, points_history, names, i)
    return points_history


def plot_ranks(points_history, names=False, scale=False):

    sns.set_style("white")
    sns.set_palette("rainbow")

    points_history = points_history.replace(0, np.nan)
    df = points_history
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


if __name__ == "__main__":
    twitter = connectTwitter()
    points_history = get_full_history(twitter)
    points_history = points_history.iloc[::-1].reset_index(drop=True)
    points_history.to_csv("rankings_history.csv")
