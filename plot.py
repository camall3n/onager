import argparse
import glob
import os
import json

import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

sns.set(style="darkgrid")

default_lr = 0.0001

def smooth_and_bin(data, bin_size, window_size):
    numeric_dtypes = data.dtypes.apply(pd.api.types.is_numeric_dtype)
    numeric_cols = numeric_dtypes.index[numeric_dtypes]
    data[numeric_cols] = data[numeric_cols].rolling(window_size).mean()
    # starting from window_size, get every bin_size row
    data = data[window_size::bin_size] 
    return data


def parse_filepath(fp, bin_size, window_size):
    try:
        data = pd.read_csv(f"{fp}/reward.csv")
        data = smooth_and_bin(data, bin_size, window_size)
        with open(f"{fp}/params.json", "r") as json_file:
            params = json.load(json_file)
        for k, v in params.items():
            data[k] = v
        return data
    except FileNotFoundError as e:
        print(f"Error in parsing filepath {fp}: {e}")
        return None


def collate_results(results_dir, bin_size, window_size):
    dfs = []
    for run in glob.glob(os.path.join(os.path.normpath(results_dir), '*')):
        print(f"Found {run}")
        run_df = parse_filepath(run, bin_size, window_size)
        if run_df is None:
            continue
        dfs.append(run_df)
    return pd.concat(dfs, axis=0)



def plot(data, hue, style, seed, savepath=None, show=True):
    print(f"Plotting using hue={hue}, style={style}, {seed}")

    # If asking for multiple envs, use facetgrid and adjust height
    height = 3 if len(data['env'].unique()) > 2 else 5
    col_wrap = 2 if len(data['env'].unique()) > 1 else 1

    palette = sns.color_palette(n_colors=len(data[hue].unique()))

    if isinstance(seed, list) or seed == 'average':
        g = sns.relplot(x='episode',
                        y='reward',
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
        g = sns.relplot(x='episode',
                        y='reward',
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
        raise ValueError(f"{seed} not a recognized choice")

    # for ax in g.axes.flatten():
    # ax.set_xlabel(f"steps")
    # ax.set(ylim=(0, 3)) # TODO make this something like 80% of the points are visible

    if savepath is not None:
        g.savefig(savepath)

    if show:
        plt.show()


def parse_args():
    # Parse input arguments
    # Use --help to see a pretty description of the arguments
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # yapf: disable
    parser.add_argument('--results-dir', help='Directory for results', default='results/pretraining',
            required=False, type=str)
    parser.add_argument('--create-csv', help='Create csv, overwrites if exists',
            action='store_true')
    parser.add_argument('--bin-size', help='How much to reduce the data by', type=int, default=100)
    parser.add_argument('--window-size', help='How much to average the data by', type=int, default=100)

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

    if args.create_csv:
        print("Recreating csv in results directory")
        print(f"Binning by {args.bin_size}")
        df = collate_results(args.results_dir, args.bin_size, args.window_size)
        df.to_csv(os.path.join(args.results_dir, 'combined.csv'))

    if not args.no_plot:
        if args.save_path:
            os.makedirs(os.path.split(args.save_path)[0], exist_ok=True)
        df = pd.read_csv(os.path.join(args.results_dir, 'combined.csv'))
        if args.query is not None:
            print(f"Filtering with {args.query}")
            df = df.query(args.query)
        plot(df, args.hue, args.style, args.seed, savepath=args.save_path, show=(not args.no_show))
