import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import warnings
warnings.filterwarnings('ignore')

def generate_price_data():
    """Generate synthetic data for crop price prediction."""
    np.random.seed(42)
    crops = ['Rice', 'Wheat', 'Tomato', 'Onion', 'Potato', 'Maize', 'Cotton', 'Sugarcane', 'Soybean', 'Groundnut']
    states = ['Maharashtra', 'Punjab', 'UP', 'MP', 'Gujarat']
    seasons = ['Summer', 'Winter', 'Rainy', 'Spring']
    market_types = ['Mandi', 'Wholesale', 'Retail']

    data = []
    base_prices = {'Rice': 1800, 'Wheat': 2000, 'Tomato': 1500, 'Onion': 2200, 'Potato': 1200, 
                   'Maize': 1600, 'Cotton': 5500, 'Sugarcane': 350, 'Soybean': 4000, 'Groundnut': 5000}

    for _ in range(2000):
        crop = np.random.choice(crops)
        state = np.random.choice(states)
        month = np.random.randint(1, 13)
        year = np.random.randint(2020, 2026)
        season = np.random.choice(seasons)
        market = np.random.choice(market_types)

        # Realistic patterns
        price = base_prices[crop]
        price *= (1 + (month - 6) * 0.02) # Seasonality
        price *= (1 + (year - 2020) * 0.05) # Inflation
        if market == 'Retail': price *= 1.3
        elif market == 'Wholesale': price *= 1.1

        price += np.random.normal(0, price * 0.05) # Noise
        
        data.append([crop, state, month, year, season, market, price])

    df = pd.DataFrame(data, columns=['Crop', 'State', 'Month', 'Year', 'Season', 'Market', 'Price'])
    return df

def generate_yield_data():
    """Generate synthetic data for crop yield prediction."""
    np.random.seed(42)
    crops = ['Rice', 'Wheat', 'Tomato', 'Onion', 'Cotton']
    soils = ['Clay', 'Sandy', 'Loamy', 'Black', 'Red', 'Alluvial']
    irrigations = ['Rainfed', 'Drip', 'Sprinkler', 'Canal', 'Borewell']

    data = []
    for _ in range(2000):
        crop = np.random.choice(crops)
        area = np.random.uniform(1.0, 50.0)
        soil = np.random.choice(soils)
        irrigation = np.random.choice(irrigations)
        fert_n = np.random.uniform(10, 100)
        fert_p = np.random.uniform(10, 50)
        fert_k = np.random.uniform(5, 30)
        rainfall = np.random.uniform(50, 800)
        temp = np.random.uniform(15, 40)
        pesticide = np.random.choice(['Yes', 'No'])

        # Yield per acre logic
        base_yield = {'Rice': 20, 'Wheat': 15, 'Tomato': 30, 'Onion': 25, 'Cotton': 10}[crop]
        if soil == 'Loamy': base_yield *= 1.2
        if irrigation == 'Drip': base_yield *= 1.3
        if rainfall > 300: base_yield *= 1.1
        if temp > 35: base_yield *= 0.8
        
        yield_per_acre = base_yield + np.random.normal(0, base_yield * 0.1)
        total_yield = yield_per_acre * area

        data.append([crop, area, soil, irrigation, fert_n, fert_p, fert_k, rainfall, temp, pesticide, yield_per_acre])

    df = pd.DataFrame(data, columns=['Crop', 'Area', 'Soil', 'Irrigation', 'Fert_N', 'Fert_P', 'Fert_K', 'Rainfall', 'Temp', 'Pesticide', 'Yield_per_acre'])
    return df

def generate_disease_data():
    """Generate synthetic numeric features for disease classification to simulate CNN output."""
    np.random.seed(42)
    X = np.random.rand(1000, 267) # Simulating 267 features (256 color + 11 lbp)
    y = np.random.randint(0, 10, 1000) # 10 disease classes
    return X, y

def train_and_save_models():
    """Train all ML models and save as .pkl files."""
    print("Training ML Models...")
    os.makedirs('ml_models', exist_ok=True)

    # 1. Price Model
    print("Training Price Predictor...")
    df_price = generate_price_data()
    le_dict_price = {}
    for col in ['Crop', 'State', 'Season', 'Market']:
        le = LabelEncoder()
        df_price[col] = le.fit_transform(df_price[col])
        le_dict_price[col] = le
        
    X_price = df_price.drop('Price', axis=1)
    y_price = df_price['Price']
    X_train_p, X_test_p, y_train_p, y_test_p = train_test_split(X_price, y_price, test_size=0.2, random_state=42)
    
    model_price = GradientBoostingRegressor(n_estimators=100, random_state=42)
    model_price.fit(X_train_p, y_train_p)
    score_p = model_price.score(X_test_p, y_test_p)
    print(f"Price Model R2 Score: {score_p:.2f}")
    joblib.dump(model_price, 'ml_models/price_model.pkl')

    # 2. Yield Model
    print("Training Yield Predictor...")
    df_yield = generate_yield_data()
    le_dict_yield = {}
    for col in ['Crop', 'Soil', 'Irrigation', 'Pesticide']:
        le = LabelEncoder()
        df_yield[col] = le.fit_transform(df_yield[col])
        le_dict_yield[col] = le
        
    X_yield = df_yield.drop(['Yield_per_acre', 'Area'], axis=1) # predict per acre, area is separate
    y_yield = df_yield['Yield_per_acre']
    X_train_y, X_test_y, y_train_y, y_test_y = train_test_split(X_yield, y_yield, test_size=0.2, random_state=42)
    
    model_yield = RandomForestRegressor(n_estimators=100, random_state=42)
    model_yield.fit(X_train_y, y_train_y)
    score_y = model_yield.score(X_test_y, y_test_y)
    print(f"Yield Model R2 Score: {score_y:.2f}")
    joblib.dump(model_yield, 'ml_models/yield_model.pkl')

    # 3. Disease Model - Mock version for structure
    print("Training Disease Classifier...")
    X_d, y_d = generate_disease_data()
    X_train_d, X_test_d, y_train_d, y_test_d = train_test_split(X_d, y_d, test_size=0.2, random_state=42)
    
    model_disease = RandomForestClassifier(n_estimators=50, random_state=42)
    model_disease.fit(X_train_d, y_train_d)
    score_d = model_disease.score(X_test_d, y_test_d)
    print(f"Disease Model Accuracy: {score_d:.2f}")
    joblib.dump(model_disease, 'ml_models/disease_model.pkl')

    print("All models trained and saved successfully.")

if __name__ == "__main__":
    # Ensure run from root
    if os.path.basename(os.getcwd()) == 'ml_models':
        os.chdir('..')
    train_and_save_models()
