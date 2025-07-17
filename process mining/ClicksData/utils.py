import pandas as pd
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.log.util import dataframe_utils
from pm4py.visualization.process_tree import visualizer as pt_visualizer
from pm4py.algo.discovery.alpha import algorithm as alpha_miner
from pm4py.algo.discovery.heuristics import algorithm as heuristics_miner
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
import plotly.graph_objects as go

from pm4py.visualization.petri_net import visualizer as pn_visualizer
from pm4py.algo.filtering.log.variants import variants_filter
from pm4py.algo.filtering.log.variants.variants_filter import filter_variants_top_k
from pm4py.discovery import discover_petri_net_inductive
from pm4py.statistics.variants.log import get as variants_module
from pm4py.conformance import precision_alignments
from pm4py.conformance import fitness_token_based_replay
from pm4py.conformance import precision_token_based_replay, precision_alignments, fitness_token_based_replay, fitness_alignments

FILE = 'BPI2016_Clicks_NOT_Logged_In.csv'
DEPENDENCY_THRESH = 0.7
AND_MEASURE_THRESH = 0.65
def get_chunks():
    chunks = pd.read_csv(FILE, chunksize=70_0000, delimiter=';', encoding='latin1', low_memory=False)
    return chunks

# we will get all the sessions that have x actions and sort by the number of occurrences
def get_sessions_with_x_actions(data_counts, col , x, up_to_x=False):
    sessions = []
    for key, value in data_counts[col].items():
        if value == x or (up_to_x and value < x):
            sessions.append(key)
    return sessions
# sessions = get_sessions_with_x_actions(data_counts, "SessionID", 2)

def get_rows_with_x_actions(data_counts, col, x, up_to_x=False):
    sessions = get_sessions_with_x_actions(data_counts, col, x, up_to_x=up_to_x)
    total_df = None
    for chunk in get_chunks():
        # select all the rows where the session_id is in the sessions list
        filtered_chunk = chunk[chunk[col].isin([int(session) for session in sessions])]
        # append the filtered chunk to the total dataframe
        if total_df is None:
            total_df = filtered_chunk
        else:
            total_df = pd.concat([total_df, filtered_chunk])

    return total_df

def get_filtered_log(data_counts, col, x, top_n=10, action_col='PAGE_NAME'):
    df_logs = get_rows_with_x_actions(data_counts, col, x)

    # Rename columns for PM4Py compatibility
    df_logs = df_logs.rename(columns={
        "SessionID": "case:concept:name",
        action_col: "concept:name",
        "TIMESTAMP": "time:timestamp"
    })

    # Convert timestamps and DataFrame to EventLog
    df_logs = dataframe_utils.convert_timestamp_columns_in_df(df_logs)
    log = log_converter.apply(df_logs, variant=log_converter.Variants.TO_EVENT_LOG)

    # Get variant info and filter top N
    variants = variants_module.get_variants(log)
    sorted_variants = sorted(variants.items(), key=lambda x: len(x[1]), reverse=True)
    top_variant_keys = [variant[0] for variant in sorted_variants[:top_n]]

    filtered_log = variants_filter.apply(log, admitted_variants=top_variant_keys)
    return filtered_log

def display_most_common_actions(data_counts, col, x, top_n=10, action_col='PAGE_NAME'):
    filtered_log = get_filtered_log(data_counts, col, x, top=top_n, action_col=action_col)

    # --- Process Tree Visualization ---
    tree = inductive_miner.apply(filtered_log)
    pt_gviz = pt_visualizer.apply(tree)
    pt_visualizer.view(pt_gviz)

    # --- Petri Net Visualization ---
    # net, im, fm = inductive_miner.apply(filtered_log)
    net, im, fm = inductive_miner.apply(filtered_log)

    pn_gviz = pn_visualizer.apply(net, im, fm)
    pn_visualizer.view(pn_gviz)

    print("\n🔍 Conformance Checking Results:\n")

    # Token-based Fitness
    fitness_tok = fitness_token_based_replay(filtered_log, net, im, fm)
    print("🎯 Token-based Fitness:", fitness_tok)

    # Alignment-based Fitness
    fitness_align = fitness_alignments(filtered_log, net, im, fm)
    print("🎯 Alignment-based Fitness:", fitness_align)

    # Token-based Precision
    precision_tok = precision_token_based_replay(filtered_log, net, im, fm)
    print("🎯 Token-based Precision:", precision_tok    )

    # Alignment-based Precision
    precision_align = precision_alignments(filtered_log, net, im, fm)
    print("🎯 Alignment-based Precision:", precision_align)

    return filtered_log, pt_gviz, pn_gviz

def display_most_common_actions_from_df(df_logs, top_n=10, action_col='PAGE_NAME', algorithm='inductive'):
    ''''ArithmeticError
    Displays the most common actions from a DataFrame and visualizes the process tree and Petri net.
    Args:
        df_logs (pd.DataFrame): DataFrame containing the logs with columns 'SessionID',
        PAGE_NAME', and 'TIMESTAMP'.
        top_n (int): Number of top variants to display.
        action_col (str): Column name for the action in the DataFrame.
        algorithm (str): Algorithm to use for process tree discovery ('inductive', 'alpha', or 'heuristics').
    Returns:
        tree (ProcessTree): The discovered process tree.
        filtered_log (EventLog): The filtered event log containing the top N variants.
        pt_gviz (ProcessTree): The visualized process tree.
        pn_gviz (PetriNet): The visualized Petri net.
    
    '''
    # Prepare DataFrame for PM4Py
    df = df_logs.rename(columns={
        "SessionID": "case:concept:name",
        action_col: "concept:name",
        "TIMESTAMP": "time:timestamp"
    })
    df = df.dropna(subset=["concept:name"])  # drop NaNs just in case
    df["concept:name"] = df["concept:name"].astype(str)  # Ensure action column is string type
    df = dataframe_utils.convert_timestamp_columns_in_df(df)

    # Convert to EventLog
    log = log_converter.apply(df, variant=log_converter.Variants.TO_EVENT_LOG)

    # Filter to top N frequent variants
    filtered_log = filter_variants_top_k(log, k=top_n)

    # Process Tree visualization
    if algorithm == 'inductive':
        tree = inductive_miner.apply(filtered_log)
    elif algorithm == 'alpha':
        tree = alpha_miner.apply(filtered_log)
    elif algorithm == 'heuristics':
        tree = heuristics_miner.apply(filtered_log, parameters= {
            heuristics_miner.Parameters.DEPENDENCY_THRESH: DEPENDENCY_THRESH,
            heuristics_miner.Parameters.AND_MEASURE_THRESH: AND_MEASURE_THRESH
        })
    
    pt_gviz = pt_visualizer.apply(tree)
    pt_visualizer.view(pt_gviz)

    ### 5. Petri Net Discovery & Visualization ###
    net, im, fm = discover_petri_net_inductive(filtered_log)
    pn_gviz = pn_visualizer.apply(net, im, fm)
    pn_visualizer.view(pn_gviz)


    print("\n🔍 Conformance Checking Results:\n")

    # Token-based Fitness
    fitness_tok = fitness_token_based_replay(filtered_log, net, im, fm)
    print("🎯 Token-based Fitness:", fitness_tok)

    # Alignment-based Fitness
    fitness_align = fitness_alignments(filtered_log, net, im, fm)
    print(f"🎯 Alignment-based Fitness: {fitness_align}")

    # Token-based Precision
    precision_tok = precision_token_based_replay(filtered_log, net, im, fm)
    print(f"🎯 Token-based Precision: {precision_tok}")

    # Alignment-based Precision
    precision_align = precision_alignments(filtered_log, net, im, fm)
    print(f"🎯 Alignment-based Precision: {precision_align}")

    return tree , filtered_log, pt_gviz, pn_gviz



def plot_counts(data_counts, column_name, trend_line=True, top_n=0):
    counts = data_counts[column_name]
    sorted_items = sorted(counts.items(), key=lambda x: x[1], reverse=True)

    top_n = min(top_n, len(sorted_items)) if top_n > 0 else len(sorted_items)
    top_items = sorted_items[:top_n]
    labels, values = zip(*top_items)

    total = sum(counts.values())
    percentages = [round((v / total) * 100, 1) for v in values]
    percentage_labels = [f'{p}%' for p in percentages]

    fig = go.Figure()

    # Bar chart with percentage text
    fig.add_trace(go.Bar(
        x=[str(label) for label in labels],
        y=values,
        name='Counts',
        marker_color='royalblue',
        text=percentage_labels,
        textposition='inside',
        texttemplate='%{text}'
    ))

    if trend_line:
        # Trend line
        fig.add_trace(go.Scatter(
            x=labels,
            y=values,
            mode='lines+markers',
        name='Trend Line',
        line=dict(color='orange', width=2),
        marker=dict(size=6)
        ))

    fig.update_layout(
        title=f'Top {top_n} Counts for {column_name}',
        xaxis_title='Values',
        yaxis_title='Counts',
        template='plotly_white',
        uniformtext_minsize=8,
        uniformtext_mode='hide'
    )

    fig.show()