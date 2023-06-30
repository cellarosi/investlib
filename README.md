# InvestLib

InvestLib is a Python package for backtesting ETF investments. It allows you to create strategies, filter ETFs, and allocate capital based on your personal preferences within a rebalancing period.

## Flow
 1. Choose etfs
 2. Choose rebalancing timer (every month, every 3 month at a custom interval)
 3. Filter certain ETFs for the next period.
 4. Allocate the current budget based on your chosen allocation

### Rebalance
**MonthlyTimer** class allow you to set number of month to execute the rebalancing and on which day. Common possibilities includes **FirstFriday**. 
### Filters
Filters allow you to select a group of etfs in your list based on specific conditions, to create for example a momentum selection every month:
    - Percentage variation in month/days
    - Sharpe ratio (assuming risk-free rate as zero)
### Allocations
You can allocate percentages between the chosen ETFs using:
	- Fixed allocation
		- Statically
		- Dinamically based on the number of filtered ETFs

## Data
The current unique data source is Tiingo. InvestLib automatically manages cash to avoid making repeated data calls. To use this feature, you need to create a free account on Tiingo and set the following environment variables:

- **tiingo_api_key**: the API token provided by Tiingo upon subscription
- **tiingo_backup_path**: the folder where you want to save the end-of-day CSV data for all the ETFs you need (default '/tmp/Tiingo'). 

## Examples

Here's some code to test out some famous **portfolios**:

### 60/40 (60 stocks/40 bond)

    import os
    import pandas as pd
    import plotly.graph_objects as go
    
    from investlib.strategy import Strategy
    from investlib.rebalance import FixedAllocation
    from investlib.rebalance import MonthlyTimer
    from investlib.rebalance import FirstFriday
    
    os.environ['tiingo_api_key'] = 'dd3b82b63e3dd1a4caa7c7658a2942977cef280a'
    
    start = '2007-01-01'
    end = '2021-06-04'
    tickers = ['VTI', 'IEF']
    
    # We create a strategy that rebalances the current money (invested + cash) to 60% VTI and 40% IEF
    # every month on the first Friday.
    s = Strategy(tickers, start=start, end=end, timer=MonthlyTimer(months=1, day=FirstFriday()),allocation_class=FixedAllocation({'VTI':0.6,'IEF':0.4}))
    s.run()
    # Build the final equity by summing up the value of investments per asset and the remaining cash
    eq = s.invested.loc[:, (slice(None), 'value')].droplevel(1, axis=1).sum(axis=1) + s.cash['post_close']
    
    # Plot the results
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=s.invested.index, y=eq, name='6040', yaxis='y1'))
    fig.add_trace(go.Scatter(x=bench.invested.index, y=bench_eq, name='VTI', yaxis='y1'))
    fig.update_layout(
        yaxis2=dict(
            title='Dati 2',
            overlaying='y',
            side='right'
        )
    )
    fig.show()

    
