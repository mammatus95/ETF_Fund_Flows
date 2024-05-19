import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.gridspec import GridSpec
import numpy as np

# ----------------------------------------------------------------------------------------------------------------------------
# flow profil


def moving_average(data, window_size):
    """
    Smooths the input data using a moving average.
    Parameters:
        data (numpy.ndarray): Input data to be smoothed.
        window_size (int): Size of the moving average window.
    Returns:
        numpy.ndarray: Smoothed data.
    """
    '''
    weights = np.repeat(1.0, window_size) / window_size
    smoothed = np.convolve(data, weights, 'valid')
    '''
    weights = np.ones(window_size) / window_size
    smoothed = np.convolve(data, weights, mode='same')

    return smoothed


def flowprofilebyprice(df, back_idx, smoothing=True, window_size=3):
    count = 50
    if back_idx >= 250:
        df['SMA_200'] = df.AdjClose.rolling(200).mean()
        offset = int(df.SMA_200.iloc[-1]*0.05)
    elif back_idx >= 100:
        df['SMA_50'] = df.AdjClose.rolling(50).mean()
        offset = int(df.SMA_50.iloc[-1]*0.05)
    else:
        df['SMA_20'] = df.AdjClose.rolling(20).mean()
        offset = int(df.SMA_20.iloc[-1]*0.05)

    price = np.linspace(np.round(df.AdjClose[-back_idx:].min()-offset, 3),
                        np.round(df.AdjClose[-back_idx:].max()+offset, 3), count)

    flow_out = np.zeros(np.size(price))
    flow_in = np.zeros(np.size(price))
    flow = np.zeros(np.size(price))

    for i in range(1, price.size):
        flow_in[i] = df[-back_idx:].loc[(df["AdjClose"].round(3) >= price[i-1]) &
                                        (df["AdjClose"].round(3) < price[i]), 'positive'].sum()
        flow_out[i] = df[-back_idx:].loc[(df["AdjClose"].round(3) >= price[i-1]) &
                                         (df["AdjClose"].round(3) < price[i]), 'negative'].sum()*(-1)
        flow[i] = flow_out[i] + flow_in[i]

    if smoothing is True:
        flow = moving_average(flow, window_size)
        flow_out = moving_average(flow_out, window_size)
        flow_in = moving_average(flow_in, window_size)

    return price, flow, flow_in, flow_out, round(price[2]-price[1], 3)

# ----------------------------------------------------------------------------------------------------------------------------
# basic plot


def basic_plot(ticker, fund_flow_df):
    fig = plt.figure(figsize=(16, 8), constrained_layout=True)
    ax = fig.add_subplot()
    fund_flow_df[["value"]].plot(ax=ax, legend=False)
    plt.savefig(f"./images/basic_plot_{ticker}.png")
    plt.close()

# ----------------------------------------------------------------------------------------------------------------------------


def flow_plot(ticker, fund_flow_df):
    back_idx = 450
    fig = plt.figure(figsize=(16, 8), constrained_layout=True)
    ax = fig.add_subplot()
    ax.bar(fund_flow_df.index[-back_idx:], fund_flow_df.negative[-back_idx:], color="red", zorder=0, lw=1.1, label="outflow")
    ax.bar(fund_flow_df.index[-back_idx:], fund_flow_df.positive[-back_idx:], color="green", zorder=0, lw=1.1, label="inflow")

    ax.set_title(f"Daily Fund Inflow and Outflow for {ticker} with Directional Indicators")
    ax.set_xlabel("Date")
    ax.set_ylabel("Fund Movement ($1e6)")

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d-%m-%Y"))
    ax.set_xticks(fund_flow_df.index[-back_idx::10])

    plt.xticks(rotation=45)
    plt.grid(visible=True, linestyle="--", linewidth=0.5)

    ax.axhline(0, color="black", linewidth=0.6)

    fig.legend(fontsize=10, title='Legende')
    plt.savefig(f"../images/flow_plot_{ticker}.png")
    plt.close()

# ----------------------------------------------------------------------------------------------------------------------------


def plot_stock_info(ticker, fund_flow_df, back_idx, longname, flowflag=True):
    
    price, flow, flow_in, flow_out, steps = flowprofilebyprice(fund_flow_df, back_idx, smoothing=True, window_size=3)

    fig = plt.figure(figsize=(16, 8), constrained_layout=True)
    gs = GridSpec(1, 3, figure=fig)
    # define subplots
    ax1 = fig.add_subplot(gs[0, 1:])
    ax2 = fig.add_subplot(gs[0, 0])
    fig.patch.set_alpha(1)
    fig.set_facecolor('w')

    # ax2 flow profile
    if flowflag is True:
        ax2.barh(price, width=flow_out, height=steps, color="navy")
        ax2.barh(price, width=flow_in, height=steps, left=flow_out, color="orange")
    else:
        ax2.barh(price, flow, height=steps)

    ax2.set_ylim(np.round(fund_flow_df.AdjClose[-back_idx:].min(), 0), 
                 np.round(fund_flow_df.AdjClose[-back_idx:].max(), 0) + np.round(fund_flow_df.AdjClose[-back_idx:].max()*0.01, 0))
    ax2_flow_limit = np.max(flow)*1.1
    ax2.set_xlim(0, ax2_flow_limit)
    ax2.set_xlabel("Fund Movement ($1e6)")

    # historic price action
    fund_flow_df.tail(back_idx)[["AdjClose"]].plot(title=f"{longname} ({ticker})", ax=ax1, legend=False)
    ax1.set_ylim(np.round(fund_flow_df.AdjClose[-back_idx:].min(), 0), 
                 np.round(fund_flow_df.AdjClose[-back_idx:].max(), 0) + np.round(fund_flow_df.AdjClose[-back_idx:].max()*0.01, 0))
    flow_max = fund_flow_df.value[-back_idx:].max()

    ax1.bar(fund_flow_df.index[-back_idx:],
            np.round(fund_flow_df.AdjClose[-back_idx:].min(), 0) +
                     (fund_flow_df.positive[-back_idx:]/flow_max) * (fund_flow_df.AdjClose[-back_idx:].min()*0.08),
            color="orange", zorder=1, label="flow in")
    ax1.bar(fund_flow_df.index[-back_idx:],
            np.round(fund_flow_df.AdjClose[-back_idx:].min(), 0) +
                     (fund_flow_df.negative[-back_idx:]*(-1)/flow_max) * (fund_flow_df.AdjClose[-back_idx:].min()*0.08),
            color="navy", zorder=1, label="flow out")
    ax1.grid(False)

    fig.legend(bbox_to_anchor=(0.33, 0.95), fontsize=10, title='Legende')

    # plt.tight_layout()
    plt.savefig(f"../images/{ticker}.png")
    plt.close()


def fund_flow_plotter(ticker, fund_flow_df, date_subset_range,
                      tick_freq=25, custom_title=None, plot_volume=True, plot_price=True):

    # date range
    plot_df = fund_flow_df[(fund_flow_df.index > date_subset_range[0])
                           & (fund_flow_df.index < date_subset_range[1])]

    title = "Fund Flows & Volume & Close"
    title = custom_title or f"{title} for {ticker}" if ticker else "Fund Flows"

    _, ax = plt.subplots(figsize=(17, 8))
    ax.set_title(title)
    ax.set_xlabel("Date")
    ax.set_ylabel("($, M)")

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d-%Y"))
    ax.set_xticks(plot_df.index[::tick_freq])

    plt.xticks(rotation=45)
    plt.grid(visible=True, linestyle="--", linewidth=0.5)
    ax.axhline(0, color="black", linewidth=0.6)

    ax.bar(plot_df.index, plot_df.negative,  color="red", zorder=0, lw=1.1, label="outflow")
    ax.bar(plot_df.index, plot_df.positive,   color="green", zorder=0, lw=1.1, label="inflow")

    if plot_volume:
        ax2 = ax.twinx()
        ax2.bar(plot_df.index, plot_df["Volume"], width=2, alpha=0.5, color='royalblue', label='Volume')
        ax2.set_ylabel('Volume')
        ax2.legend(loc='upper left')

    if plot_price:
        ax3 = ax.twinx()
        ax3.spines.right.set_position(("axes", 1.05))
        ax3.plot(plot_df.index, plot_df["AdjClose"], color='purple', label='Close', linewidth=2, alpha=0.35)
        ax3.set_ylabel('Adj Close', color='purple')
        ax3.tick_params(axis='y', labelcolor='purple')
        ax3.legend(loc='upper right')

    plt.tight_layout()
    plt.savefig(f"../images/flow_plotter_{ticker}.png")
    plt.close()
