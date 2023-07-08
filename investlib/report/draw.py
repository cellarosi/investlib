import os
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import matplotlib.pyplot as plt
from reportlab.lib.utils import ImageReader
import base64
from weasyprint import HTML
from jinja2 import Template

def generate_report(strategy, path='/tmp/report.pdf', name='Report'):
    """
        From strategy to pdf report
    """

    # Equity plot
    equity = strategy.get_equity()
    dd = strategy.get_drawdown()
    fig, axs = plt.subplots(5,1, sharex=True, gridspec_kw={'height_ratios': [5,2,5,2,2]})
    fig.set_size_inches(10, 15)
    axs[0].plot(equity.index, equity['abs'])
    axs01=axs[0].twinx()
    axs01.plot(strategy.cash.index, strategy.cash['post_close'], color='#FCE205')
    axs01.set_ylim(0,strategy.cash['post_close'].max()*5) # to compress in 1/5 of subplot the cash values   
    axs01.fill_between(strategy.cash.index, strategy.cash['post_close'], color='#FCE205') 
    axs[0].set_title('Equity $ / Cash')
    axs[0].grid(True)
    axs[1].plot(dd.index, dd['abs'], 'tab:red')
    axs[1].set_title('DD money')
    axs[1].grid(True)
    axs[2].plot(equity.index, equity['pct'])
    axs[2].set_title('Equity %')
    axs[2].grid(True)
    axs[3].plot(dd.index, dd['pct'], 'tab:red')
    axs[3].set_title('DD %')
    axs[3].grid(True)
    axs[4].plot(strategy.allocation.index, strategy.allocation)
    axs[4].set_title('Allocation %')
    axs[4].set_ylim(-0.1,1.1)
    axs[4].set_xlim(strategy.allocation.index[0],strategy.allocation.index[-1])
    fig.subplots_adjust(hspace=0.5)

    buffer = BytesIO()
    plt.savefig(buffer, format='svg', bbox_inches='tight' )
    plt.close()
    buffer.seek(0)
    img_equity_dd =  base64.b64encode(buffer.getbuffer()).decode("ascii")

    current_dir = os.path.dirname(os.path.abspath(__file__))
    with open('{}/templates/report.html'.format(current_dir), 'r') as file:
        template_html = file.read()
    template = Template(template_html)

    data = {
        'title': name,
        'start': strategy.start,
        'end': strategy.end,
        'img_equity_dd': img_equity_dd,
        'equity': equity,
        'net_profit_abs': round(equity.iloc[-1]['abs']-equity.iloc[0]['abs'],2),
        'drawdown': dd,
        'loss_period': strategy.get_loss_period(),
        'duration': strategy.get_duration(),
        'cagr': strategy.get_cagr(),
    }
    rendered_html = template.render(data)

    # Crea il documento PDF utilizzando WeasyPrint
    HTML(string=rendered_html).write_pdf(path)
