# portfolio_optimizer.py - Advanced Portfolio Optimization
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from scipy.optimize import minimize
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class PortfolioOptimizer:
    """
    Advanced Portfolio Optimization using Modern Portfolio Theory
    
    Features:
    - Mean-Variance Optimization (Markowitz)
    - Sharpe Ratio Maximization
    - Risk Parity Allocation
    - Kelly Criterion Position Sizing
    - Value at Risk (VaR) Calculations
    - Monte Carlo Simulation
    """
    
    def __init__(self, risk_free_rate: float = 0.02):
        """
        Initialize Portfolio Optimizer
        
        Args:
            risk_free_rate: Annual risk-free rate (default 2%)
        """
        self.risk_free_rate = risk_free_rate
        self.assets = []
        self.returns_data = None
        self.covariance_matrix = None
        self.correlation_matrix = None
        
        logger.info("Portfolio Optimizer initialized")
    
    def calculate_portfolio_metrics(self, weights: np.ndarray, 
                                    returns: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate portfolio performance metrics
        
        Args:
            weights: Asset weights
            returns: Historical returns DataFrame
            
        Returns:
            Dictionary of portfolio metrics
        """
        try:
            # Portfolio return
            portfolio_return = np.sum(returns.mean() * weights) * 252  # Annualized
            
            # Portfolio volatility
            portfolio_variance = np.dot(weights.T, np.dot(returns.cov() * 252, weights))
            portfolio_std = np.sqrt(portfolio_variance)
            
            # Sharpe ratio
            sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_std
            
            # Sortino ratio (downside risk)
            downside_returns = returns[returns < 0]
            downside_std = np.sqrt(np.sum(downside_returns.mean() * weights) ** 2 * 252)
            sortino_ratio = (portfolio_return - self.risk_free_rate) / downside_std if downside_std > 0 else 0
            
            # Maximum drawdown
            cumulative_returns = (1 + returns).cumprod()
            portfolio_cumulative = (cumulative_returns * weights).sum(axis=1)
            running_max = portfolio_cumulative.expanding().max()
            drawdown = (portfolio_cumulative - running_max) / running_max
            max_drawdown = drawdown.min()
            
            # Calmar ratio
            calmar_ratio = portfolio_return / abs(max_drawdown) if max_drawdown != 0 else 0
            
            return {
                'return': float(portfolio_return),
                'volatility': float(portfolio_std),
                'sharpe_ratio': float(sharpe_ratio),
                'sortino_ratio': float(sortino_ratio),
                'max_drawdown': float(max_drawdown),
                'calmar_ratio': float(calmar_ratio)
            }
            
        except Exception as e:
            logger.error(f"Error calculating portfolio metrics: {e}")
            return {}
    
    def optimize_sharpe_ratio(self, returns: pd.DataFrame, 
                             constraints: Optional[Dict] = None) -> Tuple[np.ndarray, Dict]:
        """
        Optimize portfolio for maximum Sharpe ratio
        
        Args:
            returns: Historical returns DataFrame
            constraints: Optional constraints (min_weight, max_weight)
            
        Returns:
            Optimal weights and portfolio metrics
        """
        try:
            n_assets = len(returns.columns)
            
            # Objective function: negative Sharpe ratio (for minimization)
            def objective(weights):
                metrics = self.calculate_portfolio_metrics(weights, returns)
                return -metrics['sharpe_ratio']  # Negative for maximization
            
            # Constraints
            cons = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})  # Weights sum to 1
            
            # Bounds
            min_weight = constraints.get('min_weight', 0.0) if constraints else 0.0
            max_weight = constraints.get('max_weight', 1.0) if constraints else 1.0
            bounds = tuple((min_weight, max_weight) for _ in range(n_assets))
            
            # Initial guess (equal weights)
            initial_weights = np.array([1.0 / n_assets] * n_assets)
            
            # Optimize
            result = minimize(objective, initial_weights, method='SLSQP',
                            bounds=bounds, constraints=cons)
            
            if result.success:
                optimal_weights = result.x
                metrics = self.calculate_portfolio_metrics(optimal_weights, returns)
                
                logger.info(f"Sharpe optimization successful: {metrics['sharpe_ratio']:.4f}")
                return optimal_weights, metrics
            else:
                logger.error(f"Optimization failed: {result.message}")
                return initial_weights, {}
                
        except Exception as e:
            logger.error(f"Error in Sharpe optimization: {e}")
            return np.array([]), {}
    
    def optimize_minimum_variance(self, returns: pd.DataFrame,
                                  constraints: Optional[Dict] = None) -> Tuple[np.ndarray, Dict]:
        """
        Optimize portfolio for minimum variance
        
        Args:
            returns: Historical returns DataFrame
            constraints: Optional constraints
            
        Returns:
            Optimal weights and portfolio metrics
        """
        try:
            n_assets = len(returns.columns)
            
            # Objective function: portfolio variance
            def objective(weights):
                portfolio_variance = np.dot(weights.T, np.dot(returns.cov() * 252, weights))
                return portfolio_variance
            
            # Constraints
            cons = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
            
            # Bounds
            min_weight = constraints.get('min_weight', 0.0) if constraints else 0.0
            max_weight = constraints.get('max_weight', 1.0) if constraints else 1.0
            bounds = tuple((min_weight, max_weight) for _ in range(n_assets))
            
            # Initial guess
            initial_weights = np.array([1.0 / n_assets] * n_assets)
            
            # Optimize
            result = minimize(objective, initial_weights, method='SLSQP',
                            bounds=bounds, constraints=cons)
            
            if result.success:
                optimal_weights = result.x
                metrics = self.calculate_portfolio_metrics(optimal_weights, returns)
                
                logger.info(f"Min variance optimization successful: {metrics['volatility']:.4f}")
                return optimal_weights, metrics
            else:
                logger.error(f"Optimization failed: {result.message}")
                return initial_weights, {}
                
        except Exception as e:
            logger.error(f"Error in minimum variance optimization: {e}")
            return np.array([]), {}
    
    def risk_parity_allocation(self, returns: pd.DataFrame) -> Tuple[np.ndarray, Dict]:
        """
        Calculate Risk Parity allocation
        
        Each asset contributes equally to portfolio risk
        
        Args:
            returns: Historical returns DataFrame
            
        Returns:
            Risk parity weights and metrics
        """
        try:
            n_assets = len(returns.columns)
            cov_matrix = returns.cov() * 252
            
            # Objective: minimize difference in risk contributions
            def objective(weights):
                portfolio_var = np.dot(weights.T, np.dot(cov_matrix, weights))
                marginal_contrib = np.dot(cov_matrix, weights)
                risk_contrib = weights * marginal_contrib / np.sqrt(portfolio_var)
                
                # Target: equal risk contribution
                target_risk = 1.0 / n_assets
                return np.sum((risk_contrib - target_risk) ** 2)
            
            # Constraints
            cons = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
            bounds = tuple((0.01, 1.0) for _ in range(n_assets))
            
            # Initial guess
            initial_weights = np.array([1.0 / n_assets] * n_assets)
            
            # Optimize
            result = minimize(objective, initial_weights, method='SLSQP',
                            bounds=bounds, constraints=cons)
            
            if result.success:
                rp_weights = result.x
                metrics = self.calculate_portfolio_metrics(rp_weights, returns)
                
                logger.info(f"Risk parity allocation successful")
                return rp_weights, metrics
            else:
                logger.error(f"Risk parity failed: {result.message}")
                return initial_weights, {}
                
        except Exception as e:
            logger.error(f"Error in risk parity allocation: {e}")
            return np.array([]), {}
    
    def kelly_criterion(self, win_rate: float, win_loss_ratio: float,
                       conservative_factor: float = 0.25) -> float:
        """
        Calculate Kelly Criterion position size
        
        Args:
            win_rate: Historical win rate (0-1)
            win_loss_ratio: Average win / average loss
            conservative_factor: Fraction of Kelly to use (default 0.25 = Quarter Kelly)
            
        Returns:
            Optimal position size fraction
        """
        try:
            # Kelly formula: f = (p * b - q) / b
            # where p = win_rate, q = 1-p, b = win_loss_ratio
            
            p = win_rate
            q = 1 - p
            b = win_loss_ratio
            
            if b <= 0:
                return 0.0
            
            kelly_fraction = (p * b - q) / b
            
            # Apply conservative factor
            conservative_kelly = kelly_fraction * conservative_factor
            
            # Ensure position size is between 0 and 1
            position_size = max(0.0, min(conservative_kelly, 1.0))
            
            logger.info(f"Kelly Criterion: {kelly_fraction:.4f}, Conservative: {position_size:.4f}")
            return position_size
            
        except Exception as e:
            logger.error(f"Error calculating Kelly Criterion: {e}")
            return 0.0
    
    def calculate_var(self, returns: pd.DataFrame, weights: np.ndarray,
                     confidence_level: float = 0.95, horizon: int = 1) -> float:
        """
        Calculate Value at Risk (VaR)
        
        Args:
            returns: Historical returns DataFrame
            weights: Portfolio weights
            confidence_level: Confidence level (default 95%)
            horizon: Time horizon in days
            
        Returns:
            VaR as percentage loss
        """
        try:
            # Calculate portfolio returns
            portfolio_returns = (returns * weights).sum(axis=1)
            
            # Historical VaR
            var_percentile = (1 - confidence_level) * 100
            var = np.percentile(portfolio_returns, var_percentile)
            
            # Adjust for horizon
            var_horizon = var * np.sqrt(horizon)
            
            logger.info(f"VaR ({confidence_level*100}%, {horizon}d): {var_horizon:.4%}")
            return float(var_horizon)
            
        except Exception as e:
            logger.error(f"Error calculating VaR: {e}")
            return 0.0
    
    def calculate_cvar(self, returns: pd.DataFrame, weights: np.ndarray,
                      confidence_level: float = 0.95) -> float:
        """
        Calculate Conditional Value at Risk (CVaR/Expected Shortfall)
        
        Args:
            returns: Historical returns DataFrame
            weights: Portfolio weights
            confidence_level: Confidence level
            
        Returns:
            CVaR as percentage loss
        """
        try:
            # Calculate portfolio returns
            portfolio_returns = (returns * weights).sum(axis=1)
            
            # Calculate VaR threshold
            var_threshold = np.percentile(portfolio_returns, (1 - confidence_level) * 100)
            
            # CVaR: average of returns below VaR
            cvar = portfolio_returns[portfolio_returns <= var_threshold].mean()
            
            logger.info(f"CVaR ({confidence_level*100}%): {cvar:.4%}")
            return float(cvar)
            
        except Exception as e:
            logger.error(f"Error calculating CVaR: {e}")
            return 0.0
    
    def monte_carlo_simulation(self, returns: pd.DataFrame, weights: np.ndarray,
                              n_simulations: int = 10000, horizon: int = 252) -> Dict[str, Any]:
        """
        Run Monte Carlo simulation for portfolio
        
        Args:
            returns: Historical returns DataFrame
            weights: Portfolio weights
            n_simulations: Number of simulations
            horizon: Time horizon in days (default 252 = 1 year)
            
        Returns:
            Dictionary with simulation results
        """
        try:
            # Calculate portfolio statistics
            mean_return = (returns * weights).sum(axis=1).mean()
            std_return = (returns * weights).sum(axis=1).std()
            
            # Run simulations
            simulated_returns = np.random.normal(mean_return, std_return, 
                                                (n_simulations, horizon))
            
            # Calculate cumulative returns
            cumulative_returns = (1 + simulated_returns).cumprod(axis=1)
            final_values = cumulative_returns[:, -1]
            
            # Calculate statistics
            percentiles = np.percentile(final_values, [5, 25, 50, 75, 95])
            
            results = {
                'mean_final_value': float(np.mean(final_values)),
                'median_final_value': float(np.median(final_values)),
                'std_final_value': float(np.std(final_values)),
                'percentile_5': float(percentiles[0]),
                'percentile_25': float(percentiles[1]),
                'percentile_50': float(percentiles[2]),
                'percentile_75': float(percentiles[3]),
                'percentile_95': float(percentiles[4]),
                'probability_profit': float(np.sum(final_values > 1.0) / n_simulations),
                'probability_loss': float(np.sum(final_values < 1.0) / n_simulations),
                'max_simulated_return': float(np.max(final_values)),
                'min_simulated_return': float(np.min(final_values))
            }
            
            logger.info(f"Monte Carlo simulation completed: {n_simulations} simulations")
            return results
            
        except Exception as e:
            logger.error(f"Error in Monte Carlo simulation: {e}")
            return {}
    
    def efficient_frontier(self, returns: pd.DataFrame, n_points: int = 50) -> pd.DataFrame:
        """
        Generate efficient frontier
        
        Args:
            returns: Historical returns DataFrame
            n_points: Number of points on frontier
            
        Returns:
            DataFrame with frontier points
        """
        try:
            n_assets = len(returns.columns)
            target_returns = np.linspace(returns.mean().min(), returns.mean().max(), n_points)
            
            frontier_volatilities = []
            frontier_returns = []
            frontier_sharpes = []
            
            for target_return in target_returns:
                # Objective: minimize volatility
                def objective(weights):
                    portfolio_variance = np.dot(weights.T, np.dot(returns.cov() * 252, weights))
                    return np.sqrt(portfolio_variance)
                
                # Constraints
                cons = (
                    {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
                    {'type': 'eq', 'fun': lambda x: np.sum(returns.mean() * x) * 252 - target_return}
                )
                
                bounds = tuple((0, 1) for _ in range(n_assets))
                initial_weights = np.array([1.0 / n_assets] * n_assets)
                
                result = minimize(objective, initial_weights, method='SLSQP',
                                bounds=bounds, constraints=cons)
                
                if result.success:
                    weights = result.x
                    metrics = self.calculate_portfolio_metrics(weights, returns)
                    
                    frontier_returns.append(metrics['return'])
                    frontier_volatilities.append(metrics['volatility'])
                    frontier_sharpes.append(metrics['sharpe_ratio'])
            
            frontier_df = pd.DataFrame({
                'return': frontier_returns,
                'volatility': frontier_volatilities,
                'sharpe_ratio': frontier_sharpes
            })
            
            logger.info(f"Efficient frontier generated with {len(frontier_df)} points")
            return frontier_df
            
        except Exception as e:
            logger.error(f"Error generating efficient frontier: {e}")
            return pd.DataFrame()
    
    def get_optimization_summary(self, returns: pd.DataFrame) -> Dict[str, Any]:
        """
        Get comprehensive optimization summary
        
        Args:
            returns: Historical returns DataFrame
            
        Returns:
            Dictionary with all optimization results
        """
        try:
            # Equal weights baseline
            n_assets = len(returns.columns)
            equal_weights = np.array([1.0 / n_assets] * n_assets)
            equal_metrics = self.calculate_portfolio_metrics(equal_weights, returns)
            
            # Sharpe optimized
            sharpe_weights, sharpe_metrics = self.optimize_sharpe_ratio(returns)
            
            # Min variance
            minvar_weights, minvar_metrics = self.optimize_minimum_variance(returns)
            
            # Risk parity
            rp_weights, rp_metrics = self.risk_parity_allocation(returns)
            
            summary = {
                'equal_weight': {
                    'weights': equal_weights.tolist(),
                    'metrics': equal_metrics
                },
                'max_sharpe': {
                    'weights': sharpe_weights.tolist(),
                    'metrics': sharpe_metrics
                },
                'min_variance': {
                    'weights': minvar_weights.tolist(),
                    'metrics': minvar_metrics
                },
                'risk_parity': {
                    'weights': rp_weights.tolist(),
                    'metrics': rp_metrics
                }
            }
            
            logger.info("Portfolio optimization summary completed")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating optimization summary: {e}")
            return {}
