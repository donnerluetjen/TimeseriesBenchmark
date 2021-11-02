def header_translation(header=''):
    header_translations = {'dagdtw': 'DAGDTW (sect. \\ref{sct:dagdtw})',
                           'bagdtw': 'BAGDTW (sect. \\ref{sct:bagdtw})',
                           'dtw': 'DTW \\cite{bellman1959adaptive}',
                           'sdtw': 'SDTW \\cite{cuturi2017soft}',
                           'ddtw': 'DDTW \\cite{keogh2001derivative}',
                           'wdtw': 'WDTW \\cite{jeong2011weighted}',
                           'wddtw': 'WWDTW \\cite{jeong2011weighted}',
                           'agdtw_manhattan': 'Manhattan (equation \\ref{equ:manhattan-gen})',
                           'agdtw_euclidean': 'Euclidean (equation \\ref{equ:euclidean-gen})',
                           'agdtw_chebyshev': 'Chebishev (equation \\ref{equ:chebishev-gen})',
                           'agdtw_minkowski': 'Minkowski (equation \\ref{equ:minkowski-gen})'}
    return header_translations[header]


def float_format_pattern():
    return "%.4f"


def format_ratios(data):
    return [f'{x * 100:.0f}\\%' for x in data]


def format_seconds(seconds):
    minute = 60
    hour = minute * 60
    day = hour * 24
    week = day * 7

    weeks = int(seconds / week)
    seconds -= weeks * week
    days = int(seconds / day)
    seconds -= days * day
    hours = int(seconds / hour)
    seconds -= hours * hour
    minutes = int(seconds / minute)
    seconds -= minutes * minute
    return f'runtime was {weeks} weeks, {days} days, {hours} hours, {minutes} minutes and {seconds} seconds'
