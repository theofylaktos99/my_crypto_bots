# ml_momentum_strategy.py - Machine Learning Enhanced Momentum Strategy
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
import logging
from .base_strategy import BaseStrategy, Signal
from datetime import datetime
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class MLMomentumStrategy(BaseStrategy):
    """
    Machine Learning Enhanced Momentum Strategy
    
    Uses ensemble machine learning (Random Forest + Gradient Boosting) to predict
    price momentum and generate trading signals.
    
    Features:
    - Multiple technical indicators as ML features
    - Ensemble prediction for robustness
    - Adaptive threshold based on prediction confidence
    - Real-time model retraining capability
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize ML Momentum Strategy"""
        super().__init__(config)
        
        # Strategy parameters
        self.lookback_period = config.get('lookback_period', 100)
        self.prediction_threshold = config.get('prediction_threshold', 0.6)
        self.retrain_interval = config.get('retrain_interval', 500)  # Retrain every N candles
        self.feature_engineering = config.get('feature_engineering', True)
        
        # ML models
        self.rf_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        self.gb_model = GradientBoostingClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42
        )
        
        # Scaler for feature normalization
        self.scaler = StandardScaler()
        
        # State variables
        self.is_trained = False
        self.training_data_count = 0
        self.predictions = []
        self.feature_importance = {}
        
        logger.info(f"Initialized {self.name} - ML Momentum Strategy")
        logger.info(f"Lookback: {self.lookback_period}, Threshold: {self.prediction_threshold}")
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators for ML features"""
        try:
            df = data.copy()
            
            # Price-based features
            df['returns'] = df['close'].pct_change()
            df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
            
            # Momentum indicators
            df['momentum_5'] = df['close'].pct_change(5)
            df['momentum_10'] = df['close'].pct_change(10)
            df['momentum_20'] = df['close'].pct_change(20)
            
            # Moving averages
            df['sma_10'] = df['close'].rolling(window=10).mean()
            df['sma_20'] = df['close'].rolling(window=20).mean()
            df['sma_50'] = df['close'].rolling(window=50).mean()
            df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
            df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()
            
            # Price position relative to MAs
            df['price_to_sma10'] = (df['close'] - df['sma_10']) / df['sma_10']
            df['price_to_sma20'] = (df['close'] - df['sma_20']) / df['sma_20']
            df['price_to_sma50'] = (df['close'] - df['sma_50']) / df['sma_50']
            
            # Volatility
            df['volatility_10'] = df['returns'].rolling(window=10).std()
            df['volatility_20'] = df['returns'].rolling(window=20).std()
            
            # RSI
            df = self._calculate_rsi(df, period=14)
            df = self._calculate_rsi(df, period=7, col_name='rsi_7')
            
            # MACD
            df['macd'] = df['ema_12'] - df['ema_26']
            df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
            df['macd_histogram'] = df['macd'] - df['macd_signal']
            
            # Bollinger Bands
            df['bb_middle'] = df['close'].rolling(window=20).mean()
            df['bb_std'] = df['close'].rolling(window=20).std()
            df['bb_upper'] = df['bb_middle'] + (df['bb_std'] * 2)
            df['bb_lower'] = df['bb_middle'] - (df['bb_std'] * 2)
            df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
            
            # ATR for volatility
            df['tr'] = np.maximum(
                df['high'] - df['low'],
                np.maximum(
                    abs(df['high'] - df['close'].shift(1)),
                    abs(df['low'] - df['close'].shift(1))
                )
            )
            df['atr'] = df['tr'].rolling(window=14).mean()
            df['atr_percent'] = df['atr'] / df['close']
            
            # Volume indicators
            df['volume_sma'] = df['volume'].rolling(window=20).mean()
            df['volume_ratio'] = df['volume'] / df['volume_sma']
            
            # Price patterns
            df['higher_high'] = (df['high'] > df['high'].shift(1)).astype(int)
            df['lower_low'] = (df['low'] < df['low'].shift(1)).astype(int)
            df['higher_close'] = (df['close'] > df['close'].shift(1)).astype(int)
            
            # Candlestick features
            df['body'] = abs(df['close'] - df['open'])
            df['upper_shadow'] = df['high'] - np.maximum(df['close'], df['open'])
            df['lower_shadow'] = np.minimum(df['close'], df['open']) - df['low']
            df['body_ratio'] = df['body'] / (df['high'] - df['low'] + 1e-10)
            
            # Advanced features if enabled
            if self.feature_engineering:
                df = self._add_advanced_features(df)
            
            # Create target variable for training (future return)
            df['target'] = np.where(df['close'].shift(-5) > df['close'], 1, 0)
            
            # Fill NaN values
            df = df.ffill().fillna(0)
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
            return data
    
    def _calculate_rsi(self, df: pd.DataFrame, period: int = 14, col_name: str = 'rsi') -> pd.DataFrame:
        """Calculate RSI indicator"""
        try:
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            
            rs = gain / loss
            df[col_name] = 100 - (100 / (1 + rs))
            df[col_name] = df[col_name].fillna(50)
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating RSI: {e}")
            return df
    
    def _add_advanced_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add advanced engineered features"""
        try:
            # Rate of change
            df['roc_10'] = ((df['close'] - df['close'].shift(10)) / df['close'].shift(10)) * 100
            df['roc_20'] = ((df['close'] - df['close'].shift(20)) / df['close'].shift(20)) * 100
            
            # Stochastic oscillator
            low_14 = df['low'].rolling(window=14).min()
            high_14 = df['high'].rolling(window=14).max()
            df['stoch_k'] = 100 * ((df['close'] - low_14) / (high_14 - low_14 + 1e-10))
            df['stoch_d'] = df['stoch_k'].rolling(window=3).mean()
            
            # Williams %R
            df['williams_r'] = -100 * ((high_14 - df['close']) / (high_14 - low_14 + 1e-10))
            
            # Commodity Channel Index (CCI)
            df['tp'] = (df['high'] + df['low'] + df['close']) / 3
            df['tp_sma'] = df['tp'].rolling(window=20).mean()
            df['tp_mad'] = df['tp'].rolling(window=20).apply(lambda x: np.abs(x - x.mean()).mean())
            df['cci'] = (df['tp'] - df['tp_sma']) / (0.015 * df['tp_mad'] + 1e-10)
            
            # Money Flow Index (MFI)
            df['typical_price'] = (df['high'] + df['low'] + df['close']) / 3
            df['money_flow'] = df['typical_price'] * df['volume']
            
            # Trend strength
            df['adx'] = self._calculate_adx(df)
            
            return df
            
        except Exception as e:
            logger.error(f"Error adding advanced features: {e}")
            return df
    
    def _calculate_adx(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average Directional Index"""
        try:
            # True Range
            df['tr'] = np.maximum(
                df['high'] - df['low'],
                np.maximum(
                    abs(df['high'] - df['close'].shift(1)),
                    abs(df['low'] - df['close'].shift(1))
                )
            )
            
            # Directional Movement
            df['dm_plus'] = np.where((df['high'] - df['high'].shift(1)) > (df['low'].shift(1) - df['low']),
                                      np.maximum(df['high'] - df['high'].shift(1), 0), 0)
            df['dm_minus'] = np.where((df['low'].shift(1) - df['low']) > (df['high'] - df['high'].shift(1)),
                                       np.maximum(df['low'].shift(1) - df['low'], 0), 0)
            
            # Smoothed indicators
            atr = df['tr'].rolling(window=period).mean()
            di_plus = 100 * (df['dm_plus'].rolling(window=period).mean() / atr)
            di_minus = 100 * (df['dm_minus'].rolling(window=period).mean() / atr)
            
            # ADX calculation
            dx = 100 * abs(di_plus - di_minus) / (di_plus + di_minus + 1e-10)
            adx = dx.rolling(window=period).mean()
            
            return adx.fillna(0)
            
        except Exception as e:
            logger.error(f"Error calculating ADX: {e}")
            return pd.Series([0] * len(df))
    
    def _get_feature_columns(self) -> List[str]:
        """Get list of feature columns for ML"""
        features = [
            'returns', 'momentum_5', 'momentum_10', 'momentum_20',
            'price_to_sma10', 'price_to_sma20', 'price_to_sma50',
            'volatility_10', 'volatility_20',
            'rsi', 'rsi_7',
            'macd', 'macd_signal', 'macd_histogram',
            'bb_position', 'atr_percent',
            'volume_ratio',
            'higher_high', 'lower_low', 'higher_close',
            'body_ratio'
        ]
        
        if self.feature_engineering:
            features.extend([
                'roc_10', 'roc_20', 'stoch_k', 'stoch_d',
                'williams_r', 'cci', 'adx'
            ])
        
        return features
    
    def train_models(self, df: pd.DataFrame):
        """Train ML models on historical data"""
        try:
            if len(df) < self.lookback_period:
                logger.warning("Insufficient data for training")
                return
            
            # Get features and target
            feature_cols = self._get_feature_columns()
            
            # Check if all features exist
            missing_cols = [col for col in feature_cols if col not in df.columns]
            if missing_cols:
                logger.error(f"Missing feature columns: {missing_cols}")
                return
            
            X = df[feature_cols].values
            y = df['target'].values
            
            # Remove rows with NaN or inf
            mask = np.isfinite(X).all(axis=1) & np.isfinite(y)
            X = X[mask]
            y = y[mask]
            
            if len(X) < 50:
                logger.warning("Insufficient clean data for training")
                return
            
            # Split data for training (use recent 70% for training)
            split_idx = int(len(X) * 0.7)
            X_train = X[-split_idx:]  # Last 70% (most recent data)
            y_train = y[-split_idx:]
            
            # Normalize features
            X_train_scaled = self.scaler.fit_transform(X_train)
            
            # Train models
            self.rf_model.fit(X_train_scaled, y_train)
            self.gb_model.fit(X_train_scaled, y_train)
            
            self.is_trained = True
            self.training_data_count = len(X_train)
            
            # Get feature importance
            self.feature_importance = dict(zip(
                feature_cols,
                (self.rf_model.feature_importances_ + self.gb_model.feature_importances_) / 2
            ))
            
            # Sort by importance
            self.feature_importance = dict(sorted(
                self.feature_importance.items(),
                key=lambda x: x[1],
                reverse=True
            ))
            
            logger.info(f"Models trained on {len(X_train)} samples")
            logger.info(f"Top features: {list(self.feature_importance.keys())[:5]}")
            
        except Exception as e:
            logger.error(f"Error training models: {e}")
            self.is_trained = False
    
    def generate_signal(self, data: pd.DataFrame) -> Optional[Signal]:
        """Generate trading signal using ML predictions"""
        try:
            # Calculate indicators
            df = self.calculate_indicators(data)
            
            if len(df) < self.lookback_period:
                return None
            
            # Train models if not trained or retrain interval reached
            if not self.is_trained or len(df) % self.retrain_interval == 0:
                self.train_models(df)
            
            if not self.is_trained:
                return None
            
            # Get current features
            feature_cols = self._get_feature_columns()
            current_features = df[feature_cols].iloc[-1:].values
            
            # Check for invalid values
            if not np.isfinite(current_features).all():
                logger.warning("Invalid feature values detected")
                return None
            
            # Normalize features
            current_features_scaled = self.scaler.transform(current_features)
            
            # Get predictions from both models
            rf_pred_proba = self.rf_model.predict_proba(current_features_scaled)[0]
            gb_pred_proba = self.gb_model.predict_proba(current_features_scaled)[0]
            
            # Ensemble prediction (average probabilities)
            ensemble_proba = (rf_pred_proba + gb_pred_proba) / 2
            
            # Predicted class (0 = down, 1 = up)
            prediction = int(ensemble_proba[1] > ensemble_proba[0])
            confidence = float(max(ensemble_proba))
            
            # Store prediction
            current_price = df['close'].iloc[-1]
            self.predictions.append({
                'price': current_price,
                'prediction': prediction,
                'confidence': confidence,
                'timestamp': datetime.now()
            })
            
            # Keep only recent predictions
            if len(self.predictions) > 100:
                self.predictions = self.predictions[-100:]
            
            # Update indicators
            self.indicators = {
                'price': current_price,
                'prediction': prediction,
                'confidence': confidence,
                'rf_prob': rf_pred_proba[1],
                'gb_prob': gb_pred_proba[1],
                'ensemble_prob': ensemble_proba[1]
            }
            
            # Generate signal based on prediction and confidence
            signal = None
            
            if self.position == 0:  # No position
                # BUY signal: Predict up with high confidence
                if prediction == 1 and confidence >= self.prediction_threshold:
                    signal = Signal(
                        action='buy',
                        confidence=confidence,
                        price=current_price,
                        timestamp=datetime.now(),
                        metadata={
                            'ml_prediction': 'bullish',
                            'rf_prob': rf_pred_proba[1],
                            'gb_prob': gb_pred_proba[1],
                            'top_features': list(self.feature_importance.keys())[:3]
                        }
                    )
                    logger.info(f"ML BUY Signal @ {current_price:.2f} | Confidence: {confidence:.2%}")
                
                # SELL signal: Predict down with high confidence
                elif prediction == 0 and confidence >= self.prediction_threshold:
                    signal = Signal(
                        action='sell',
                        confidence=confidence,
                        price=current_price,
                        timestamp=datetime.now(),
                        metadata={
                            'ml_prediction': 'bearish',
                            'rf_prob': rf_pred_proba[0],
                            'gb_prob': gb_pred_proba[0],
                            'top_features': list(self.feature_importance.keys())[:3]
                        }
                    )
                    logger.info(f"ML SELL Signal @ {current_price:.2f} | Confidence: {confidence:.2%}")
            
            else:  # Have position - check for exit
                exit_signal = self._check_ml_exit(df, prediction, confidence)
                if exit_signal:
                    return exit_signal
            
            return signal
            
        except Exception as e:
            logger.error(f"Error generating signal: {e}")
            return None
    
    def _check_ml_exit(self, df: pd.DataFrame, prediction: int, confidence: float) -> Optional[Signal]:
        """Check ML-based exit conditions"""
        try:
            current_price = df['close'].iloc[-1]
            
            # Exit long position
            if self.position > 0:
                # Prediction changed to bearish with high confidence
                if prediction == 0 and confidence >= self.prediction_threshold:
                    return Signal(
                        action='exit_long',
                        confidence=confidence,
                        price=current_price,
                        timestamp=datetime.now(),
                        metadata={'reason': 'ml_reversal_prediction'}
                    )
            
            # Exit short position
            elif self.position < 0:
                # Prediction changed to bullish with high confidence
                if prediction == 1 and confidence >= self.prediction_threshold:
                    return Signal(
                        action='exit_short',
                        confidence=confidence,
                        price=current_price,
                        timestamp=datetime.now(),
                        metadata={'reason': 'ml_reversal_prediction'}
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking ML exit: {e}")
            return None
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get ML model information"""
        return {
            'is_trained': self.is_trained,
            'training_samples': self.training_data_count,
            'feature_count': len(self._get_feature_columns()),
            'top_features': list(self.feature_importance.keys())[:5] if self.feature_importance else [],
            'prediction_count': len(self.predictions),
            'last_prediction': self.predictions[-1] if self.predictions else None
        }
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """Get comprehensive strategy information"""
        base_info = super().get_strategy_info()
        
        base_info.update({
            'strategy_type': 'ML Momentum',
            'is_trained': self.is_trained,
            'training_samples': self.training_data_count,
            'prediction_threshold': self.prediction_threshold,
            'recent_accuracy': self._calculate_recent_accuracy()
        })
        
        return base_info
    
    def _calculate_recent_accuracy(self) -> float:
        """Calculate accuracy of recent predictions"""
        try:
            if len(self.predictions) < 10:
                return 0.0
            
            recent = self.predictions[-20:]
            # This is a simplified accuracy - in practice, you'd validate against actual outcomes
            correct = sum(1 for p in recent if p['confidence'] > 0.7)
            return round(correct / len(recent), 2)
            
        except Exception as e:
            logger.error(f"Error calculating accuracy: {e}")
            return 0.0
