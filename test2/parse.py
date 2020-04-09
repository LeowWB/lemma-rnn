import collections
import zlib
import functools
import os
import pickle

def get_usefulness_problemslemmas():
    if (os.path.isfile('test1data/usefulness_raw.pickle')):
        usefulness = pickle.load(open('test1data/usefulness_raw.pickle', 'rb'))
    else:
        usefulness = _get_usefulness()
        pickle.dump(usefulness, open('test1data/usefulness_raw.pickle', 'wb'))

    if (os.path.isfile('test1data/problemslemmas_raw.pickle')):
        problemlemmas = pickle.load(open('test1data/problemslemmas_raw.pickle', 'rb'))
    else:
        problemlemmas = _get_problemslemmas()
        pickle.dump(problemlemmas, open('test1data/problemslemmas_raw.pickle', 'wb'))

    return usefulness, problemlemmas

@functools.lru_cache(maxsize=1)
def parse_problem(problemname):
    return _parse_cnf_file('E_conj/problems/{}'.format(problemname))


# all private methods from here on =================================================================


def _parse_cnf_list(s):
    # Filter out comments
    s = '\n'.join(l for l in s.split('\n') if not l.startswith('#') and l)
    return s

def _parse_cnf_file(filename):
    with open(filename, 'r') as f:
        return _parse_cnf_list(f.read())

def _get_usefulness():
    print('getting usefulness')
    with open('E_conj/statistics', 'r') as f:
        s = f.read()
        ls = s.split('\n')
        usefulness = collections.defaultdict(dict)
        for l in ls:
            if not l.strip():
                continue
            psr, problem, lemmaname, *_ = l.split(':')
            psr = float(psr)
            lemmaname = lemmaname.split('.')[0]
            usefulness[problem][lemmaname] = psr

    return usefulness

def _process_problemslemmas(l):
    name, lemma = l.split(':')
    _, problemname, lemmaname = name.split('/')
    return (
        problemname,
        lemmaname,
        parse_problem(problemname),
        lemma,
        )

def _get_problemslemmas():
    print('parsing problems and lemmas')
    import multiprocessing

    with multiprocessing.Pool() as pool:
        with open('E_conj/lemmas') as f:
            return pool.map(_process_problemslemmas, f, 32)
