"""Graphiques du rapport Word, en noir et blanc, à partir du CSV archivé."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).parent
frame = pd.read_csv(ROOT/'resultats/mesures.csv')
plt.rcParams.update({'font.family':'Times New Roman','font.size':12,'axes.spines.top':False,'axes.spines.right':False})
tasks = ['Concept','Raisonnement','Code Python','Synthèse','Traduction']
models = ['llama3.2:latest','qwen:0.5b']
for key, label, name in [('Temps (s)','Temps de réponse en secondes','temps_nb'),('Tokens/s','Tokens générés par seconde','debit_nb'),('TTFT (s)','Délai avant le premier fragment en secondes','ttft_nb')]:
    fig, ax = plt.subplots(figsize=(7.2,2.8))
    for i,model in enumerate(models):
        values=frame[frame['Modèle']==model].set_index('Tâche').loc[tasks,key]
        ax.bar([x+(i-.5)*.34 for x in range(5)],values,width=.32,color='0.25' if i==0 else 'white',edgecolor='black',hatch=None if i==0 else '///',label='Llama 3.2' if i==0 else 'Qwen 0.5B')
    ax.set_xticks(range(5),tasks)
    ax.set_ylabel(label)
    ax.set_ylim(0,frame[key].max()*1.3)
    ax.legend(frameon=False,ncol=2,loc='upper right')
    ax.grid(axis='y',color='.85',linewidth=.5)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(ROOT/'rapport_assets'/f'{name}.png',dpi=300)
    plt.close(fig)
fig,axes=plt.subplots(1,2,figsize=(7.2,2.7))
for ax,key,label in zip(axes,['ram_gb_max','vram_mb_max'],['Pic RAM système en Gio','Pic mémoire GPU en Mio']):
    values=[frame[frame['Modèle']==m][key].mean() for m in models]
    bars=ax.bar(['Llama 3.2','Qwen 0.5B'],values,color=['.25','white'],edgecolor='black',width=.55)
    bars[1].set_hatch('///')
    for bar,value in zip(bars,values):
        ax.text(bar.get_x()+bar.get_width()/2,value,f'{value:.2f}' if key=='ram_gb_max' else f'{value:.0f}',ha='center',va='bottom')
    ax.set_ylabel(label)
    ax.set_ylim(0,max(values)*1.2)
fig.tight_layout()
fig.savefig(ROOT/'rapport_assets/memoire_nb.png',dpi=300)
plt.close(fig)
