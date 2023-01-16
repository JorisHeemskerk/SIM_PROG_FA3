from kies_model import KiesModel
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def plurality_printres(n_jaar, n_stem, n_partij):
    new_model = KiesModel(n_stem, n_partij, 'p')
    new_model.step()
    df = new_model.data
    print('partijen: ')
    for i in new_model.partijen:
        print('\t' + str(i))
    print('\nn stemmers: \t\t' + str(new_model.num_agents))
    print('condorcet winnaar:\t' + str(new_model.condorcet()))
    print('winnaar:\t\t\t' + str(df['vote'].value_counts().index[0]))
    print('stemmen:\n' + str(df['vote'].value_counts()))

    for i in range(n_jaar):
        new_model.step()
        df = new_model.data
        print('\nwinnaar:\t\t\t' + str(df['vote'].value_counts().index[0]))
        print('stemmen:\n' + str(df['vote'].value_counts()))

    return (new_model.winnaar, new_model.condorcet())

def approval_printres(n_jaar, n_stem, n_partij):
    new_model = KiesModel(n_stem, n_partij, 'a')
    new_model.step()
    print('partijen: ')
    for i in new_model.partijen:
        print('\t' + str(i))
    print('\nn stemmers: \t\t' + str(new_model.num_agents))
    print('condorcet winnaar:\t' + str(new_model.condorcet()))
    print('winnaar:\t\t\t' + str(new_model.winnaar))
    s = pd.Series(np.hstack(new_model.data['vote']))
    print('stemmen:\n' + str(s.value_counts()))

    for i in range(n_jaar):
        new_model.step()
        print('winnaar:\t\t\t' + str(new_model.winnaar))
        s = pd.Series(np.hstack(new_model.data['vote']))
        print('stemmen:\n' + str(s.value_counts()))

    return (new_model.winnaar, new_model.condorcet())

def runoff_printres(n_jaar, n_stem, n_partij):
    new_model = KiesModel(n_stem, n_partij, 'r')
    new_model.step()
    print('partijen: ')
    for i in new_model.partijen:
        print('\t' + str(i))
    print('\nn stemmers: \t\t' + str(new_model.num_agents))
    print('condorcet winnaar:\t' + str(new_model.condorcet()))
    print('winnaar:\t\t\t' + str(new_model.winnaar))
    s = pd.Series(np.hstack(new_model.data['vote']))
    print('stemmen:\n' + str(s.value_counts()))

    for i in range(n_jaar):
        new_model.step()
        print('winnaar:\t\t\t' + str(new_model.winnaar))
        s = pd.Series(np.hstack(new_model.data['vote']))
        print('stemmen:\n' + str(s.value_counts()))

    return (new_model.winnaar, new_model.condorcet())

def run(n_jaar, n_stem, n_partij, method='p'):
    new_model = KiesModel(n_stem, n_partij, method)
    new_model.step()
    c = new_model.condorcet()
    if method != 'r':
        for _ in range(n_jaar):
            new_model.step()
    return (int(new_model.winnaar), int(c))

def run_multiples(n_years=5, n_voters=1000, n_parties=5, runs=1000):
    ys = [[],[],[]]
    for i, method_name in enumerate(['p', 'r', 'a']):
        for j in range(3, n_parties+1): # 1 and 2 party simulations are not interesting, hence the 3.
            n = 0
            for _ in range(runs):
                res = run(n_years, n_voters, j, method_name)
                if(res[0] == res[1]):
                    n += 1
            print(f'% of matches for method {method_name} with {j} parties:', (n/runs) * 100)
            ys[i].append((n/runs) * 100)
        print()
    labels = list(np.arange(3, n_parties+1))

    x = np.arange(len(labels))
    width = 0.25

    fig, ax = plt.subplots()
    rects0 = ax.bar(x - width, ys[0], width, label='plurality')
    rects1 = ax.bar(x,         ys[1], width, label='instant runoff')
    rects2 = ax.bar(x + width, ys[2], width, label='approval')

    ax.set_xlabel('n parties')
    ax.set_ylabel('% of elections resulting in condorcet winner')
    ax.set_xticks(x, labels)
    ax.legend()

    fig.tight_layout()

    plt.show()

def main():
    # For individual runs of any method use one of the following:
        # NOTE: Comment in line 84 and 93 of kies_model.py for additional analysis.
    # approval_printres(5, 10000, 5)
    # plurality_printres(5, 10000, 5)
    # runoff_printres(0, 100000, 5)

    # For multiple runs over potentially multiple years, use the following:
    run_multiples(n_years=5, n_voters=1000, n_parties=5, runs=1)

if __name__ == '__main__':
    main()
