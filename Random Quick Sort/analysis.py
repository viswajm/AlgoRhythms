import os, sys, numpy as np, pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from numpy.linalg import lstsq

INPUT_CSV = 'results/combined_results.csv'
OUTDIR = 'plots'
os.makedirs(OUTDIR, exist_ok=True)

if not os.path.exists(INPUT_CSV):
    print("❌ Missing results/combined_results.csv. Run run_experiments.sh first.")
    sys.exit(1)

df = pd.read_csv(INPUT_CSV)
df['n'] = df['n'].astype(int)
df['n_log_n'] = df['n'] * np.log(df['n'])

agg = df.groupby(['variant', 'input_type', 'n']).agg(
    trials=('trial', 'count'),
    time_mean=('time_ms', 'mean'),
    comp_mean=('comparisons', 'mean')
).reset_index()

agg['n_log_n'] = agg['n'] * np.log(agg['n'])
variants = np.sort(agg['variant'].unique())
input_types = np.sort(agg['input_type'].unique())

# Time vs n
for input_type in input_types:
    plt.figure(figsize=(8,6))
    for var in variants:
        sub = agg[(agg['variant']==var)&(agg['input_type']==input_type)]
        plt.plot(sub['n'], sub['time_mean'], marker='o', label=var)
    plt.xscale('log'); plt.yscale('log')
    plt.xlabel('n'); plt.ylabel('mean time (ms)')
    plt.title(f'Time vs n — input={input_type}')
    plt.legend(); plt.grid(True, ls='--')
    plt.savefig(f'{OUTDIR}/time_vs_n_{input_type}.png', dpi=200)
    plt.close()

# Comparisons normalized
for var in variants:
    plt.figure(figsize=(8,6))
    for input_type in input_types:
        sub = agg[(agg['variant']==var)&(agg['input_type']==input_type)]
        plt.plot(sub['n'], sub['comp_mean']/(sub['n']*np.log(sub['n'])), marker='o', label=input_type)
    plt.xscale('log')
    plt.xlabel('n'); plt.ylabel('comparisons / (n log n)')
    plt.title(f'Normalized comparisons — {var}')
    plt.legend(); plt.grid(True)
    plt.savefig(f'{OUTDIR}/comp_norm_{var}.png', dpi=200)
    plt.close()

# Fit random/random
sub = agg[(agg['variant']=='random') & (agg['input_type']=='random')]
if len(sub) >= 3:
    X = np.vstack([sub['n_log_n'], sub['n'], np.ones(len(sub))]).T
    y = sub['time_mean'].values
    a,b,c = lstsq(X, y, rcond=None)[0]
    pred = a*sub['n_log_n'] + b*sub['n'] + c
    plt.figure(figsize=(8,6))
    plt.plot(sub['n'], sub['time_mean'], 'o', label='observed')
    plt.plot(sub['n'], pred, '-', label='fit')
    plt.xscale('log'); plt.xlabel('n'); plt.ylabel('mean time (ms)')
    plt.title('Fit: T(n) ≈ a·nlogn + b·n + c (random/random)')
    plt.legend(); plt.grid(True)
    plt.savefig(f'{OUTDIR}/fit_random_random.png', dpi=200)
    plt.close()
    print(f'✅ Fit coefficients: a={a:.6e}, b={b:.6e}, c={c:.6e}')

print('✅ Plots saved to', OUTDIR)
