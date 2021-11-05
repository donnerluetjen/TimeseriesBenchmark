# This Python file uses the following encoding: utf-8
__author__ = "6541262: Ansgar Asseburg"
__copyright__ = "Copyright 2021 – Ansgar Asseburg; " \
                "You may use and copy this document (including changing it) " \
                "for non-commercial and educational purposes" \
                "as long as you leave the author and this copyright " \
                "information in"
__email__ = "s2092795@stud.uni-frankfurt.de"

from math import sqrt
from pathlib import Path

import pgfplots as pp
import textable as tt
import file_ops as fo
from dataset_details import datasets_details_json_path, generate_datasets_details
from dataset_details import datasets_property_values_list, \
    datasets_with_property_value
import progress_indication as p
import json


def archive_for(archive='UEA', wws='1.0'):
    json_store = './Benchmarks/json/'
    archives = {'UEA': 0, 'UCR': 1}
    json_files_dict = {
        '1.0': ['UEA_archive_wws--1.json', 'UCR_archive_wws--1.json'],
        '0.3': ['UEA_archive_wws-0-3.json', 'UCR_archive_wws-0-3.json'],
        '0.1': ['UEA_archive_wws-0-1.json', 'UCR_archive_wws-0-1.json']
    }
    return json_store + json_files_dict[wws][archives[archive.upper()]]


def archive_data(archive):
    with open(archive) as archive_json:
        return json.load(archive_json)


def ranking(scores, do_not_rank=None):
    exclude = ['arguments', 'runtime']
    if do_not_rank is not None:
        exclude += do_not_rank
    keys = [key for key in scores.keys() if key not in exclude]
    squared_result = 0
    for key in keys:
        squared_result += scores[key] ** 2
    return sqrt(squared_result)


def ranking_for_wws(wws, do_not_rank=[]):
    # concatenate both datasets for uea and ucr
    data = archive_data(archive_for('uea', '1.0'))
    data.update(archive_data(archive_for('ucr', '1.0')))
    datasets = [dataset for dataset in data.keys()]
    metrics = [metric for metric in data[datasets[0]].keys() if
               metric != 'properties']
    rankings = {}
    for metric in metrics:
        accumulated_ranking = 0
        for dataset in datasets:
            accumulated_ranking += ranking(data[dataset][metric])
        average_metric_ranking = accumulated_ranking / len(datasets)
        rankings[metric] = average_metric_ranking
    return rankings


def datasets_high_scores(data=None):
    if data is None:
        return None
    datasets = list(data.keys())
    metrics = [key for key in data[datasets[0]].keys() if key != 'properties']
    scores = [key for key in data[datasets[0]][metrics[0]].keys() if
              key != 'arguments']
    high_score_dict = {}
    for dataset in datasets:

        high_score_dict[dataset] = {}

        for score in scores:

            high_score = 0 if score != 'runtime' else float('inf')
            comparator = max if score != 'runtime' else min

            for metric in metrics:
                score_value = data[dataset][metric][score]
                if score_value == comparator(score_value, high_score):
                    high_score = score_value
                    high_score_dict[dataset][score] = metric
    return high_score_dict


def generate_number_property_correlation_plot(uea_json_path, ucr_json_path,
                                              scb='1.0', property_name='',
                                              y_axis_name=''):
    path_dict = fo.path_dictionary(uea_json_path)
    plot_file_name = f'pgfplot_{scb_name(scb)}_ranking_over_{property_name}.tex'
    pgf_path = Path(path_dict['tex_corr'], plot_file_name)
    sources = [uea_json_path, ucr_json_path, datasets_details_json_path]
    with open(uea_json_path) as uea_json_file:
        data = json.load(uea_json_file)
    with open(ucr_json_path) as ucr_json_file:
        data.update(json.load(ucr_json_file))
    cardinalities = datasets_property_values_list(property_name)

    metrics = [metric for metric in data[list(data.keys())[0]] if
               metric != 'properties']

    # find the average ranking for each metric
    average_rankings = ranking_for_wws(scb)
    class_cardinality_scores = {}
    xtick_labels = []
    for cardinality in cardinalities:
        xtick_labels.append(str(cardinality))
        class_cardinality_scores[cardinality] = {}
        cardinality_datasets = datasets_with_property_value(
            property_name, cardinality)
        for index, metric in enumerate(metrics):
            metric_average_ranking = average_rankings[metric]
            ranking_sum = 0
            for dataset in cardinality_datasets:
                ranking_sum += ranking(data[dataset][metric])
            ranking_ave = ranking_sum / len(cardinality_datasets)
            normalized_ranking_ave = ranking_ave / metric_average_ranking
            # spread graphs
            spread_normalized_ranking_ave = normalized_ranking_ave + index
            class_cardinality_scores[cardinality][
                metric] = spread_normalized_ranking_ave

    progress = p.Progress(f'Writing datasets plots {plot_file_name}')

    plot = pp.CorrelationPlots(pgf_path, y_axis_name, 'Algorithm',
                               xtick_labels, sources)

    for metric in metrics:
        plot.add_data(metric, [
            [cardinality, class_cardinality_scores[cardinality][metric]]
            for cardinality in cardinalities])
        progress.progress()

    del plot  # to ensure destructor is called before program exits
    progress.end()


def generate_string_property_correlation_plot(uea_json_path, ucr_json_path,
                                              scb='1.0', property_name='',
                                              y_axis_name=''):
    path_dict = fo.path_dictionary(uea_json_path)
    plot_file_name = f'pgfplot_{scb_name(scb)}_ranking_over_{property_name}.tex'
    pgf_path = Path(path_dict['tex_corr'], plot_file_name)
    sources = [uea_json_path, ucr_json_path, datasets_details_json_path]
    with open(uea_json_path) as uea_json_file:
        data = json.load(uea_json_file)
    with open(ucr_json_path) as ucr_json_file:
        data.update(json.load(ucr_json_file))
    prop_value_list = datasets_property_values_list(property_name)

    metrics = [metric for metric in data[list(data.keys())[0]] if
               metric != 'properties']

    # find the average ranking for each metric
    average_rankings = ranking_for_wws(scb)
    prop_value_scores = {}
    prop_value_labels = []
    for prop_value in prop_value_list:
        prop_value_labels.append(prop_value)
        prop_value_scores[prop_value] = {}
        prop_value_datasets = datasets_with_property_value(
            property_name, prop_value)
        for index, metric in enumerate(metrics):
            metric_average_ranking = average_rankings[metric]
            ranking_sum = 0
            for dataset in prop_value_datasets:
                ranking_sum += ranking(data[dataset][metric])
            ranking_ave = ranking_sum / len(prop_value_datasets)
            normalized_ranking_ave = ranking_ave / metric_average_ranking
            spread_normalized_ranking_ave = normalized_ranking_ave + index
            prop_value_scores[prop_value][metric] = spread_normalized_ranking_ave

    progress = p.Progress(f'Writing datasets plots {plot_file_name}')
    plot = pp.CorrelationXStrPlots(pgf_path, y_axis_name, 'Algorithm',
                                   prop_value_labels, sources)

    for metric in metrics:
        # we want to start at x = 1
        plot.add_data(metric, [
            [prop_value_labels.index(domain) + 1, prop_value_scores[domain][metric]]
            for domain in prop_value_list])
        progress.progress()

    del plot  # to ensure destructor is called before program exits
    progress.end()


def generate_trend_diagram(folder='', file_list=None, name='',
                           do_not_rank=None):
    if file_list is None:
        file_list = []
    if do_not_rank is None:
        do_not_rank = []
    if name == '' or not len(file_list):
        return

    path_dict = fo.path_dictionary(folder + 'SCB_trends.json')
    plot_file_name = f'pgfplot_{name}_scb_trend.tex'
    pgf_path = Path(path_dict['tex_dir'], plot_file_name)
    sources = []
    for file in file_list:
        sources.append(folder + file)

    all_files_data = {}  # initialize empty dictionary
    # collect all data
    for file in file_list:
        file_path = folder + file

        with open(file_path) as scoring_file:
            temp_data = json.load(scoring_file)

        datasets = temp_data.keys()
        wws = temp_data[list(datasets)[0]]['bagdtw']['arguments']['window']

        # clean dictionary of unnecessary data
        for dataset in datasets:
            temp_data[dataset].pop('properties')
            metrics = temp_data[dataset].keys()
            for metric in metrics:
                temp_data[dataset][metric].pop('arguments')

        all_files_data[wws] = temp_data

    wwss = list(all_files_data.keys())
    datasets = list(all_files_data[wwss[0]].keys())
    metrics = list(all_files_data[wwss[0]][datasets[0]].keys())
    scores = list(all_files_data[wwss[0]][datasets[0]][metrics[0]].keys())

    progress = p.Progress(f'Writing datasets plots {plot_file_name}')
    plot = pp.TrendPlots(pgf_path, 'Mean Runtime', 'Mean Ranking', sources,
                         True)

    for metric in metrics:
        table_data = []
        for wws in wwss:
            datasets = list(all_files_data[wws].keys())
            accumulated_scoring = 0
            accumulated_runtime = 0
            for dataset in datasets:
                accumulated_scoring += ranking(
                    all_files_data[wws][dataset][metric], do_not_rank)
                accumulated_runtime += all_files_data[wws][dataset][metric][
                    'runtime']
            table_data.append([accumulated_runtime / len(datasets),
                               accumulated_scoring / len(datasets), abs(wws)])
            plot.add_data(metric, table_data)
            progress.progress()

    del plot  # to ensure destructor is called before program exits
    progress.end()


def generate_score_diagram(json_path, plot_name_specific='',
                           score_name='ranking', do_not_rank=None):
    path_dict = fo.path_dictionary(json_path)
    plot_file_name = f'pgfplot_{score_name}_{"".join([c for c in plot_name_specific if c != " "])}.tex'
    pgf_path = Path(path_dict['tex_dir'], plot_file_name)
    sources = [json_path]
    with open(json_path) as json_file:
        data = json.load(json_file)

    datasets = list(data.keys())
    # read metrics and drop properties
    metrics = list(data[datasets[0]].keys())
    metrics.remove('properties')

    progress = p.Progress(f'Writing datasets plots {plot_file_name}')
    plot = pp.TexPlots(pgf_path, 'Mean Runtime',
                       f'Mean {score_name.capitalize()}', sources, True)

    for metric in metrics:
        # iterate over datasets for metric and find averages
        accumulated_scoring = 0
        accumulated_runtime = 0
        for dataset in datasets:
            if score_name == 'ranking':
                accumulated_scoring += ranking(data[dataset][metric],
                                               do_not_rank)
            else:
                accumulated_scoring += data[dataset][metric][score_name]
            accumulated_runtime += data[dataset][metric]['runtime']

        table_data = [[accumulated_runtime / len(datasets),
                       accumulated_scoring / len(datasets)]]
        plot.add_data(metric, table_data)
        progress.progress()
    del plot  # to ensure destructor is called before program exits
    progress.end()


def generate_table(json_path, dataset_details_file, table_name_specific='',
                   split_table_metrics=None, do_not_rank=None):
    path_dict = fo.path_dictionary(json_path)
    dataset_archive = path_dict['archive']

    if split_table_metrics is None:
        split_table_metrics = []
    if do_not_rank is None:
        do_not_rank = []
    sources = [json_path, dataset_details_file]

    # load dataset details
    with open(dataset_details_file) as dd_file:
        dataset_details = json.load(dd_file)

    with open(json_path) as json_file:
        data = json.load(json_file)

    high_scores = datasets_high_scores(data)

    datasets = list(data.keys())
    # read metrics and drop properties
    metrics = [key for key in data[datasets[0]] if key != 'properties']

    # split metrics into schemes for the two tables
    table_metrics_schemes = [sorted(split_table_metrics), sorted(list(set(metrics) - set(split_table_metrics)))]

    # read scores and drop arguments
    omitted = do_not_rank + ['arguments']
    scores = [key for key in data[datasets[0]][metrics[0]] if key not in omitted]
    scores = [score for score in scores if score not in do_not_rank]  # FixMe: line seems to be redundant

    for table_metrics_scheme in table_metrics_schemes:
        if len(table_metrics_scheme) == 0:
            continue
        table_file_name = f'table_{dataset_archive}_{"-".join(table_metrics_scheme)}_{"".join([c for c in table_name_specific if c != " "])}.tex'
        table_path = Path(path_dict['tex_dir'], table_file_name)

        table_caption = dataset_archive + ' Datasets for Metrics ' + ', '.join(
            table_metrics_scheme).upper() + f' \\gls{{scb}} {human_readable(table_name_specific.removeprefix("scb"))}'
        table_label = dataset_archive + '_' + '-'.join(
            table_metrics_scheme) + f'_scb_{"".join([c for c in table_name_specific if c != " "])}'

        score_columns_formatter = 'c' * len(scores)
        # table_column_formatter works as formatter list since all formats are single chars
        table_column_formatter = f'|l|{"|".join(score_columns_formatter for _ in range(len(table_metrics_scheme)))}|'

        progress = p.Progress(f'Writing datasets scoring table {table_file_name}')

        scores_table = tt.ScoreTexTable(table_path, table_column_formatter,
                                        table_caption, table_label, table_metrics_scheme, scores, sources)

        for dataset in datasets:
            table_line_list = [dataset_details[dataset]['short_name']]

            format_bold = [False]  # short_name should not be bold

            for metric in table_metrics_scheme:
                for score in scores:
                    table_line_list.append(data[dataset][metric][score])
                    format_bold.append(True if high_scores[dataset][score] == metric else False)
            scores_table.add_line(table_line_list, format_bold)

            progress.progress()
        del scores_table  # to make sure destructor is called
        progress.end()


def human_readable(message):
    """
    format message in human readable form
    :param message: string containing message with unwanted characters
    :return: formatted string
    """
    split_message = message.split('_')
    split_message = [m.strip() for m in split_message]
    name = ' '.join([m.capitalize() for m in split_message[0].split('-')]).strip()
    value = split_message[1].replace('-', '.')
    return f'{name} {value}'


def generate_classes_correlation_table(uea_json_path, ucr_json_path,
                                       scb='1.0'):
    path_dict = fo.path_dictionary(uea_json_path)
    table_file_name = f'table_{scb_name(scb)}_ranking_over_num_of_classes.tex'
    table_path = Path(path_dict['tex_corr'], table_file_name)
    sources = [uea_json_path, ucr_json_path, datasets_details_json_path]
    with open(uea_json_path) as uea_json_file:
        data = json.load(uea_json_file)
    with open(ucr_json_path) as ucr_json_file:
        data.update(json.load(ucr_json_file))
    cardinalities = datasets_property_values_list('num_of_classes')

    datasets = list(data.keys())
    # read metrics and drop properties
    metrics = [key for key in data[datasets[0]] if key != 'properties']

    table_caption = 'Correlation of Number of Classes and Ranking'
    table_label = 'corr-classes'

    score_columns_formatter = 'c'
    # table_column_formatter works as formatter list since all formats are single chars
    table_column_formatter = f'|l|c|{"|".join(score_columns_formatter for _ in range(len(metrics)))}|'

    class_cardinality_scores = {}
    num_datasets_in_cardinality = {}
    for cardinality in cardinalities:
        class_cardinality_scores[cardinality] = {}
        cardinality_datasets = datasets_with_property_value(
            'num_of_classes', cardinality)
        num_datasets_in_cardinality[cardinality] = len(cardinality_datasets)
        for index, metric in enumerate(metrics):
            ranking_sum = 0
            for dataset in cardinality_datasets:
                ranking_sum += ranking(data[dataset][metric])
            ranking_ave = ranking_sum / len(cardinality_datasets)
            class_cardinality_scores[cardinality][metric] = ranking_ave

    progress = p.Progress(f'Writing classes-ranking-correlation table {table_file_name}')
    correlation_table = tt.CorrelationTexTable(table_path, table_column_formatter,
                                               table_caption, table_label, metrics, ['Ranking'], 'Classes', sources)

    for cardinality in cardinalities:
        table_line_list = [str(cardinality)]
        table_line_list.append(str(num_datasets_in_cardinality[cardinality]))
        format_bold = [False, False]

        for metric in metrics:
            table_line_list.append(class_cardinality_scores[cardinality][metric])
            format_bold.append(False)  # (True if high_scores[dataset][score] == metric else False)
        correlation_table.add_line(table_line_list, format_bold)

        progress.progress()

    del correlation_table  # to make sure destructor is called
    progress.end()


def generate_dimensions_correlation_table(uea_json_path, ucr_json_path, scb='1.0'):
    path_dict = fo.path_dictionary(uea_json_path)
    table_file_name = f'table_{scb_name(scb)}_ranking_over_num_of_dimensions.tex'
    table_path = Path(path_dict['tex_corr'], table_file_name)
    sources = [uea_json_path, ucr_json_path, datasets_details_json_path]
    with open(uea_json_path) as uea_json_file:
        data = json.load(uea_json_file)
    with open(ucr_json_path) as ucr_json_file:
        data.update(json.load(ucr_json_file))
    cardinalities = datasets_property_values_list('num_of_dimensions')

    datasets = list(data.keys())
    # read metrics and drop properties
    metrics = [key for key in data[datasets[0]] if key != 'properties']

    table_caption = 'Correlation of Number of Dimensions and Ranking'
    table_label = 'corr_dimensions'

    score_columns_formatter = 'c'
    # table_column_formatter works as formatter list since all formats are single chars
    table_column_formatter = f'|l|c|{"|".join(score_columns_formatter for _ in range(len(metrics)))}|'

    dimension_cardinality_scores = {}
    num_datasets_in_cardinality = {}
    for cardinality in cardinalities:
        dimension_cardinality_scores[cardinality] = {}
        cardinality_datasets = datasets_with_property_value(
            'num_of_dimensions', cardinality)
        num_datasets_in_cardinality[cardinality] = len(cardinality_datasets)
        for index, metric in enumerate(metrics):
            ranking_sum = 0
            for dataset in cardinality_datasets:
                ranking_sum += ranking(data[dataset][metric])
            ranking_ave = ranking_sum / len(cardinality_datasets)
            dimension_cardinality_scores[cardinality][metric] = ranking_ave

    progress = p.Progress(f'Writing dimension-ranking-correlation table {table_file_name}')
    correlation_table = tt.CorrelationTexTable(table_path, table_column_formatter,
                                               table_caption, table_label, metrics, ['Ranking'], 'Dimensions', sources)

    for cardinality in cardinalities:
        table_line_list = [str(cardinality)]
        table_line_list.append(str(num_datasets_in_cardinality[cardinality]))
        format_bold = [False, False]

        for metric in metrics:
            table_line_list.append(dimension_cardinality_scores[cardinality][metric])
            format_bold.append(False)  # (True if high_scores[dataset][score] == metric else False)
        correlation_table.add_line(table_line_list, format_bold)

        progress.progress()

    del correlation_table  # to make sure destructor is called
    progress.end()


def generate_domains_correlation_table(uea_json_path, ucr_json_path, scb='1.0'):
    path_dict = fo.path_dictionary(uea_json_path)
    table_file_name = f'table_{scb_name(scb)}_ranking_over_domain.tex'
    table_path = Path(path_dict['tex_corr'], table_file_name)
    sources = [uea_json_path, ucr_json_path, datasets_details_json_path]
    with open(uea_json_path) as uea_json_file:
        data = json.load(uea_json_file)
    with open(ucr_json_path) as ucr_json_file:
        data.update(json.load(ucr_json_file))
    domain_list = datasets_property_values_list('domain')

    datasets = list(data.keys())
    # read metrics and drop properties
    metrics = [key for key in data[datasets[0]] if key != 'properties']

    table_caption = 'Correlation of Domains and Ranking'
    table_label = 'corr_domains'

    score_columns_formatter = 'c'
    # table_column_formatter works as formatter list since all formats are single chars
    table_column_formatter = f'|l|c|{"|".join(score_columns_formatter for _ in range(len(metrics)))}|'

    domain_scores = {}
    num_datasets_in_domain = {}
    for domain in domain_list:
        domain_scores[domain] = {}
        domain_datasets = datasets_with_property_value('domain', domain)
        num_datasets_in_domain[domain] = len(domain_datasets)
        for index, metric in enumerate(metrics):
            ranking_sum = 0
            for dataset in domain_datasets:
                ranking_sum += ranking(data[dataset][metric])
            ranking_ave = ranking_sum / len(domain_datasets)
            domain_scores[domain][metric] = ranking_ave

    progress = p.Progress(
        f'Writing domains-ranking-correlation table {table_file_name}')
    correlation_table = tt.CorrelationTexTable(table_path,
                                               table_column_formatter,
                                               table_caption, table_label,
                                               metrics, ['Ranking'], 'Domains',
                                               sources)

    for domain in domain_list:
        table_line_list = [domain]
        table_line_list.append(str(num_datasets_in_domain[domain]))
        format_bold = [False, False]

        for metric in metrics:
            table_line_list.append(domain_scores[domain][metric])
            format_bold.append(
                False)  # (True if high_scores[dataset][score] == metric
# else False)
        correlation_table.add_line(table_line_list, format_bold)

        progress.progress()

    del correlation_table  # to make sure destructor is called
    progress.end()


def generate_distance_consolidations_diagram(json_path, score_name='ranking',
                                             do_not_rank=None):
    path_dict = fo.path_dictionary(json_path)
    plot_file_name = f'pgfplot_{score_name}_distance_consolidations.tex'
    pgf_path = Path(path_dict['tex_dir'], plot_file_name)
    sources = [json_path]
    with open(json_path) as json_file:
        data = json.load(json_file)

    datasets = list(data.keys())
    # read metrics and drop properties
    metrics = sorted([key for key in data[datasets[0]] if key != 'properties'])

    progress = p.Progress(f'Writing datasets plots {plot_file_name}')
    plot = pp.TexPlots(pgf_path, 'Mean Runtime',
                       f'Mean {score_name.capitalize()}', sources)

    for metric in metrics:
        # iterate over datasets for metric and find averages
        accumulated_scoring = 0
        accumulated_runtime = 0
        for dataset in datasets:
            if score_name == 'ranking':
                accumulated_scoring += ranking(data[dataset][metric],
                                               do_not_rank)
            else:
                accumulated_scoring += data[dataset][metric][score_name]
            accumulated_runtime += data[dataset][metric]['runtime']

        table_data = [[accumulated_runtime / len(datasets),
                       accumulated_scoring / len(datasets)]]
        plot.add_data(metric, table_data)
        progress.progress()
    del plot  # to ensure destructor is called before program exits
    progress.end()


def generate_distance_consolidations_table(json_path, dataset_details_file,
                                           do_not_rank=None):
    path_dict = fo.path_dictionary(json_path)
    dataset_archive = path_dict['archive']

    if do_not_rank is None:
        do_not_rank = []

    sources = [json_path, dataset_details_file]

    # load dataset details
    with open(dataset_details_file) as dd_file:
        dataset_details = json.load(dd_file)

    with open(json_path) as json_file:
        data = json.load(json_file)

    high_scores = datasets_high_scores(data)

    datasets = list(data.keys())
    # read metrics and drop properties
    metrics = sorted([key for key in data[datasets[0]] if key != 'properties'])

    # read scores and drop arguments
    omitted = do_not_rank + ['arguments']
    scores = [key for key in data[datasets[0]][metrics[0]] if
              key not in omitted]
    scores = [score for score in scores if score not in do_not_rank]

    table_file_name = f'table_distance_consolidations.tex'
    table_path = Path(path_dict['tex_dir'], table_file_name)

    table_caption = 'Datasets for Distance Consolidation Methods'
    table_label = 'distance-consolidations'

    score_columns_formatter = 'c' * len(scores)
    # table_column_formatter works as formatter list since all formats are
    # single chars
    table_column_formatter = f'|l|{"|".join(score_columns_formatter for _ in range(len(metrics)))}|'

    progress = p.Progress(f'Writing datasets scoring table {table_file_name}')

    norms_table = tt.ScoreTexTable(table_path, table_column_formatter,
                                   table_caption, table_label, metrics, scores,
                                   sources)

    for dataset in datasets:
        table_line_list = [dataset_details[dataset]['short_name']]

        format_bold = [False]  # short_name should not be bold

        for metric in metrics:
            for score in scores:
                table_line_list.append(data[dataset][metric][score])
                format_bold.append(
                    True if high_scores[dataset][score] == metric else False)
        norms_table.add_line(table_line_list, format_bold)

        progress.progress()

    del norms_table  # to make sure destructor is called
    progress.end()


def scb_name(scb):
    """
    formats scb properly to be part of a file path
    :param scb: string containing the scb size
    :return: a formatted string
    """
    return f'scb-size_{scb.replace(".", "-")}'


if __name__ == '__main__':

    json_store = './Benchmarks/json/'
    json_files_dict = {
        '1.0': ['UEA_archive_wws--1.json', 'UCR_archive_wws--1.json'],
        '0.3': ['UEA_archive_wws-0-3.json', 'UCR_archive_wws-0-3.json'],
        '0.1': ['UEA_archive_wws-0-1.json', 'UCR_archive_wws-0-1.json']
    }
    wws_list = ['1.0', '0.3', '0.1']

    uea_list = []
    ucr_list = []

    # generate_datasets_details()

    for wws in wws_list:
        for json_file in json_files_dict[wws]:
            generate_table(json_store + json_file, datasets_details_json_path,
                           scb_name(wws), ['bagdtw', 'dagdtw', 'sdtw'])
            generate_score_diagram(json_store + json_file, scb_name(wws),
                                   'ranking')
            generate_score_diagram(json_store + json_file, scb_name(wws),
                                   'accuracy')
            generate_score_diagram(json_store + json_file, scb_name(wws),
                                   'recall')
            generate_score_diagram(json_store + json_file, scb_name(wws),
                                   'f1-score')
            generate_score_diagram(json_store + json_file, scb_name(wws),
                                   'auroc')

        uea_list.append(json_files_dict[wws][0])
        ucr_list.append(json_files_dict[wws][1])

        generate_trend_diagram(json_store, uea_list, 'UEA')
        generate_trend_diagram(json_store, ucr_list, 'UCR')

        json_data_file = 'UEA_distance_consolidations_0-03.json'
        generate_distance_consolidations_table(json_store + json_data_file,
                                               datasets_details_json_path)
        generate_distance_consolidations_diagram(json_store +
                                                 json_data_file, 'ranking')

        generate_number_property_correlation_plot(
            json_store + json_files_dict[wws][0],
            json_store + json_files_dict[wws][1], wws,
            'num_of_classes', 'Class Cardinality')
        generate_classes_correlation_table(
            json_store + json_files_dict[wws][0],
            json_store + json_files_dict[wws][1],
            wws)

        generate_number_property_correlation_plot(
            json_store + json_files_dict[wws][0],
            json_store + json_files_dict[wws][1], wws,
            'num_of_dimensions', 'Dimension Cardinality')
        generate_dimensions_correlation_table(
            json_store + json_files_dict[wws][0],
            json_store + json_files_dict[wws][1],
            wws)

        generate_string_property_correlation_plot(
            json_store + json_files_dict[wws][0],
            json_store + json_files_dict[wws][1], wws,
            'domain', 'Domain')
        generate_domains_correlation_table(
            json_store + json_files_dict[wws][0],
            json_store + json_files_dict[wws][1],
            wws)
