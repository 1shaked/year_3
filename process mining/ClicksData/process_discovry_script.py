# %% [markdown]
# ### Process Discovery
# We will discover the processes in the system.
# 
# 1) read the event log
# 2) filter only to the test events (with the accepted_sessions)
# 3) understand the amount of traces that exist in the event log
# 4) discover the process model with trashload to understand the process flow
# 5) evaluate the performance of the process model using conformance checking
# 

# %%
import pandas as pd
import json
import numpy as np
from utils import *
from pm4py.visualization.process_tree import visualizer as pt_visualizer
from pm4py.visualization.petri_net import visualizer as pn_visualizer
from pm4py.discovery import discover_petri_net_inductive

from pm4py.algo.discovery.alpha import algorithm as alpha_miner
from pm4py.algo.discovery.heuristics import algorithm as heuristics_miner
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.convert import convert_to_petri_net
from pm4py.conformance import precision_token_based_replay, precision_alignments, fitness_token_based_replay, fitness_alignments


# %%





def calculate_outcomes():
    # %%
    with open('accepted_sessions.json', 'r') as f:
        accepted_sessions = json.load(f)

    with open('test_sessions.json') as f:
        test_sessions = json.load(f)

    total_df = pd.read_csv(FILE, encoding='latin1', delimiter=';')
    # Filter the DataFrame to include only the accepted sessions
    filtered_df = total_df[total_df['SessionID'].isin([int(session) for session in accepted_sessions])]
    test_df = total_df[total_df['SessionID'].isin([int(session) for session in test_sessions])]


    # %% [markdown]
    # #### Understand the amount of unique traces in the event log

    # %%
    # Step 1: Sort events by session and time
    filtered_df = filtered_df.sort_values(by=["SessionID", "TIMESTAMP"])

    # Step 2: Group by session and collect the ordered activity list as a tuple
    traces = filtered_df.groupby("SessionID")["PAGE_NAME"].apply(tuple)

    # Step 3: Count how many times each unique trace occurs
    trace_counts = traces.value_counts()

    df = filtered_df.rename(columns={
        "SessionID": "case:concept:name",
        'PAGE_NAME': "concept:name",
        "TIMESTAMP": "time:timestamp"
    })
    df = df.dropna(subset=["concept:name"])  # drop NaNs just in case
    df["concept:name"] = df["concept:name"].astype(str)  # Ensure action column is string type
    df = dataframe_utils.convert_timestamp_columns_in_df(df)

    # Convert to EventLog
    log = log_converter.apply(df, variant=log_converter.Variants.TO_EVENT_LOG)

    alpha_miner_results = []
    heuristics_miner_results = []
    inductive_miner_results = []
    for top_n in range(10 ,100 , 5):
        # %%
        TOP_N = top_n
        # Filter to top N frequent variants
        filtered_log = filter_variants_top_k(log, k=TOP_N)

        # %%
        # create a test log for testing
        test_df = test_df.rename(columns={
            "SessionID": "case:concept:name",
            'PAGE_NAME': "concept:name",
            "TIMESTAMP": "time:timestamp"
        })
        test_df = test_df.dropna(subset=["concept:name"])  # drop NaNs just in case
        test_df["concept:name"] = test_df["concept:name"].astype(str)  # Ensure action column is string type
        test_df = dataframe_utils.convert_timestamp_columns_in_df(test_df)
        # Convert to EventLog
        test_log = log_converter.apply(test_df, variant=log_converter.Variants.TO_EVENT_LOG)
        # net, im, fm = alpha_miner.apply(filtered_log)

        # gviz = pn_visualizer.apply(net, im, fm)
        # pn_visualizer.view(gviz)

        # we will conduct conformance checking on the filtered log
        # fitness_tok = fitness_token_based_replay(test_log, net, im, fm)
        # print("🎯 Token-based Fitness:", fitness_tok)
        

        # fitness_align = fitness_alignments(test_log, net, im, fm)
        # print("🎯 Alignment-based Fitness:", fitness_align)

        # precision_tok = precision_token_based_replay(test_log, net, im, fm)
        # print("🎯 Token-based Precision:", precision_tok    )

        # precision_align = precision_alignments(test_log, net, im, fm)
        # print("🎯 Alignment-based Precision:", precision_align)
        # alpha_miner_results.append({
        #     "top_n": top_n,
        #     "fitness_tok": fitness_tok,
        #     "fitness_align": fitness_align,
        #     "precision_tok": precision_tok,
        #     "precision_align": precision_align
        # })
        # # %% [markdown]
        # # ### heuristics_miner

        # # %%
        # net, im, fm = heuristics_miner.apply(filtered_log, variant=heuristics_miner.Variants.CLASSIC)

        # # %%
        # # gviz = pn_visualizer.apply(net, im, fm)
        # # pn_visualizer.view(gviz)

        # # %%
        # # we will conduct conformance checking on the filtered log
        # fitness_tok = fitness_token_based_replay(test_log, net, im, fm)
        # print("🎯 Token-based Fitness:", fitness_tok)

        # fitness_align = fitness_alignments(test_log, net, im, fm)
        # print("🎯 Alignment-based Fitness:", fitness_align)

        # precision_tok = precision_token_based_replay(test_log, net, im, fm)
        # print("🎯 Token-based Precision:", precision_tok    )

        # precision_align = precision_alignments(test_log, net, im, fm)
        # print("🎯 Alignment-based Precision:", precision_align)
        # heuristics_miner_results.append({
        #     "top_n": top_n,
        #     "fitness_tok": fitness_tok,
        #     "fitness_align": fitness_align,
        #     "precision_tok": precision_tok,
        #     "precision_align": precision_align
        # })
        # %% [markdown]
        # ### inductive_miner

        # %%

        # tree = inductive_miner.apply(filtered_log)  # gives ProcessTree
        # net, im, fm = tree_converter.apply(tree, variant=tree_converter.Variants.TO_PETRI_NET)
        net, im, fm = discover_petri_net_inductive(filtered_log) 
        # we will conduct conformance checking on the filtered log
        fitness_tok = fitness_token_based_replay(test_log, net, im, fm)
        print("🎯 Token-based Fitness:", fitness_tok)

        fitness_align = fitness_alignments(test_log, net, im, fm)
        print("🎯 Alignment-based Fitness:", fitness_align)

        precision_tok = precision_token_based_replay(test_log, net, im, fm)
        print("🎯 Token-based Precision:", precision_tok    )

        precision_align = precision_alignments(test_log, net, im, fm)
        print("🎯 Alignment-based Precision:", precision_align)
        inductive_miner_results.append({
            "top_n": top_n,
            "fitness_tok": fitness_tok,
            "fitness_align": fitness_align,
            "precision_tok": precision_tok,
            "precision_align": precision_align
        })
    return alpha_miner_results, heuristics_miner_results, inductive_miner_results

alpha_miner_results, heuristics_miner_results, inductive_miner_results = calculate_outcomes()
# save the to json files
# with open('algorithms/alpha_miner_results.json', 'w') as f:
#     json.dump(alpha_miner_results, f)
# with open('algorithms/heuristics_miner_results.json', 'w') as f:
#     json.dump(heuristics_miner_results, f)
with open('algorithms/inductive_miner_results.json', 'w') as f:
    json.dump(inductive_miner_results, f)


