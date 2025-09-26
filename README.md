# Portfolio-FAANG

This repository provides tools and notebooks to construct, analyze, and visualize a stock portfolio focused on **FAANG** companies (Facebook/Meta, Apple, Amazon, Netflix, Google). It allows users to compute portfolio weights, track daily returns, and visualize correlations and portfolio performance.

## Repository Structure

- **data/**: Contains datasets used for analysis, including historical stock prices.
- **notebooks/**: Jupyter notebooks demonstrating portfolio construction, analysis, and visualization workflows.
- **portfolio/**: Python scripts for calculating portfolio weights, free float, and cumulative portfolio value.
- **requirements.txt**: List of Python packages required to run the code.

## Features

### 1. Portfolio Weight Calculation
- Computes weights based on **free float shares** (shares available for public trading, excluding insider holdings and restricted shares).
- Stocks with **higher free floats** have proportionally higher influence in the portfolio.
- As an alternative, we also consider the **inverse free-float weighting scheme**, where companies with smaller free floats receive larger weights. This approach highlights the impact of less liquid stocks on portfolio performance.
- Results can be benchmarked against an **equal-weighted portfolio** to evaluate differences in performance.

### 2. Daily Portfolio Returns
- Calculates daily returns for each stock using closing prices.
- Aggregates individual stock returns to compute overall portfolio returns using weighted sums.

### 3. Portfolio Value Simulation
- Tracks cumulative portfolio value over time from an initial investment.
- Accounts for weighted contributions from each stock's daily performance.

### 4. Data Visualization
- Correlation heatmaps to explore relationships between stock returns.
- Portfolio and individual stock performance charts.

## Usage

### 1. Set up the environment
```bash
conda create --name portfolio-env
```
### 2. Activate the environment
```
conda activate portfolio-env
```
### 3. Install requirements
```
pip install -r requirements.txt
```
### 4. Analysis and Backtesting
All analysis and backtesting are implemented in `notebook` folder