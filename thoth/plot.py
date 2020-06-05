import argparse
import glob
import os
import json

import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

sns.set(style="darkgrid")


def smooth_and_bin(data, bin_size, window_size):
    numeric_dtypes = data.dtypes.apply(pd.api.types.is_numeric_dtype)
    numeric_cols = numeric_dtypes.index[numeric_dtypes]
    data[numeric_cols] = data[numeric_cols].rolling(window_size).mean()
    # starting from window_size, get every bin_size row
    data = data[window_size::bin_size]
    return data


def parse_filepath(fp, filename, bin_size, window_size):
    try:
        data = pd.read_csv(os.path.join(fp, filename))
        data = smooth_and_bin(data, bin_size, window_size)
        with open(os.path.join(fp, 'params.json'), "r") as json_file:
            params = json.load(json_file)
        for k, v in params.items():
            data[k] = v
        return data
    except FileNotFoundError as e:
        print("Error in parsing filepath {fp}: {e}".format(fp=fp, e=e))
        return None


def collate_results(results_dir, filename, bin_size, window_size):
    dfs = []
    for run in glob.glob(os.path.join(os.path.normpath(results_dir), '*')):
        print("Found {run}".format(run=run))
        run_df = parse_filepath(run, filename, bin_size, window_size)
        if run_df is None:
            continue
        dfs.append(run_df)
    return pd.concat(dfs, axis=0)


def plot(data, x, y, hue, style, seed, savepath=None, show=True):
    print("Plotting using hue={hue}, style={style}, {seed}".format(hue=hue, style=style, seed=seed))
    assert not data.empty, "DataFrame is empty, please check query"
    # If asking for multiple envs, use facetgrid and adjust height
    height = 3 if len(data['env'].unique()) > 2 else 5
    col_wrap = 2 if len(data['env'].unique()) > 1 else 1

    palette = sns.color_palette('Set1', n_colors=len(data[hue].unique()), desat=0.5)

    if isinstance(seed, list) or seed == 'average':
        g = sns.relplot(x=x,
                        y=y,
                        data=data,
                        hue=hue,
                        style=style,
                        kind='line',
                        legend='full',
                        height=height,
                        aspect=1.5,
                        col='env',
                        col_wrap=col_wrap,
                        palette=palette,
                        facet_kws={'sharey': False})

    elif seed == 'all':
        g = sns.relplot(x=x,
                        y=y,
                        data=data,
                        hue=hue,
                        units='seed',
                        style=style,
                        estimator=None,
                        kind='line',
                        legend='full',
                        height=height,
                        aspect=1.5,
                        col='env',
                        col_wrap=col_wrap,
                        palette=palette,
                        facet_kws={'sharey': False})
    else:
        raise ValueError("{seed} not a recognized choice".format(seed=seed))

    if savepath is not None:
        g.savefig(savepath)

    if show:
        plt.show()


def parse_args():
    # Parse input arguments
    # Use --help to see a pretty description of the arguments
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # yapf: disable
    parser.add_argument('--results-dir', help='Directory for results', required=True, type=str)
    parser.add_argument('--filename', help='CSV filename', required=False, type=str)
    parser.add_argument('--bin-size', help='How much to reduce the data by', type=int, default=10)
    parser.add_argument('--window-size', help='How much to average the data by', type=int, default=10)

    parser.add_argument('-x', help='Variable to plot on x axis', required=False, type=str)
    parser.add_argument('-y', help='Variable to plot on y axis', required=False, type=str)

    parser.add_argument('--query', help='DF query string', type=str)
    parser.add_argument('--hue', help='Hue variable', type=str)
    parser.add_argument('--style', help='Style variable', type=str)
    parser.add_argument('--seed', help='How to handle seeds', type=str, default='average')

    parser.add_argument('--no-plot', help='No plots', action='store_true')
    parser.add_argument('--no-show', help='Does not show plots', action='store_true')
    parser.add_argument('--save-path', help='Save the plot here', type=str)
    # yapf: enable

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    print("Looking for logs in results directory")
    print("Smoothing by {window_size}, binning by {bin_size}".format(window_size=args.window_size,
                                                                     bin_size=args.bin_size))
    assert args.filename is not None, "Must pass filename if creating csv"
    df = collate_results(args.results_dir, args.filename, args.bin_size, args.window_size)

    if not args.no_plot:
        assert args.x is not None and args.y is not None, "Must pass x, y if creating csv"
        if args.save_path:
            os.makedirs(os.path.split(args.save_path)[0], exist_ok=True)
        if args.query is not None:
            print("Filtering with {query}".format(query=args.query))
            df = df.query(args.query)
        plot(df,
             args.x,
             args.y,
             args.hue,
             args.style,
             args.seed,
             savepath=args.save_path,
             show=(not args.no_show))
