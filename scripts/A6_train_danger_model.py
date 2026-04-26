
import os
import json
import pandas as pd 
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, classification_report, confusion_matrix

DATA_FILE     = 'data_files/training_data.csv'
MODEL_FILE    = 'data_files/danger_model.json'
FEATURES_FILE = 'data_files/model_features.json'


def main():
    print("=" * 55)
    print("  SETUP ")
    print("=" * 55)
    
    if not os.path.exists(DATA_FILE):
        print(f"[ERROR] {DATA_FILE} not found. Build the dataset first.")
        return
        
    print(f"[>>] Loading '{DATA_FILE}' ...")
    df = pd.read_csv(DATA_FILE)
    
    X = df.drop(columns=['label'])
    y = df['label']
    
    # ================================================================
    #  PART 1: Train/Test Split
    # ================================================================
    print("\n[>>] PART 1: Train/Test Split (80/20) ...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    print(f"  Train shape : {X_train.shape}")
    print(f"  Test shape  : {X_test.shape}")
    
    # ================================================================
    #  PART 2: Train XGBoost
    # ================================================================
    print("\n[>>] PART 2: Training XGBoost Danger Model ...")
    
    # Instantiate strictly as per requested parameters
    model = XGBClassifier(
        n_estimators=300,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_weight=3,
        scale_pos_weight=4,
        eval_metric='auc',
        early_stopping_rounds=30,
        random_state=42
    )
    
    # eval_set needed for early_stopping
    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        verbose=50  # print score every 50 rounds
    )
    
    # ================================================================
    #  PART 3: Evaluate
    # ================================================================
    print("\n" + "=" * 55)
    print("  PART 3: EVALUATION")
    print("=" * 55)
    
    best_iteration = getattr(model, 'best_iteration', None)
    if best_iteration is not None:
        print(f"  Best iteration : {best_iteration}")
        
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    auc_score = roc_auc_score(y_test, y_pred_proba)
    print(f"  Test AUC Score : {auc_score:.4f}\n")
    
    y_pred = model.predict(X_test)
    
    print("  Classification Report:")
    print("  " + "-" * 51)
    
    # format indentation neatly for the printout
    cr = classification_report(y_test, y_pred)
    for line in cr.split('\n'):
        print("  " + line)
        
    print("  Confusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(f"     [TN: {cm[0][0]:>4} | FP: {cm[0][1]:>4}]")
    print(f"     [FN: {cm[1][0]:>4} | TP: {cm[1][1]:>4}]")
    
    # ================================================================
    #  PART 4: Feature Importance
    # ================================================================
    print("\n" + "=" * 55)
    print("  PART 4: TOP 10 FEATURE IMPORTANCE (GAIN)")
    print("=" * 55)
    
    booster = model.get_booster()
    # 'gain' implies the relative contribution of the corresponding feature
    # to the model calculated by taking each feature's contribution for each tree
    gain_scores = booster.get_score(importance_type='gain')
    
    importances = []
    for col in X.columns:
        importances.append((col, gain_scores.get(col, 0.0)))
        
    importances.sort(key=lambda x: x[1], reverse=True)
    
    print(f"  {'Rank':<4} | {'Feature Name':<25} | {'Importance Score'}")
    print("  " + "-" * 51)
    
    for i, (feat, score) in enumerate(importances[:10], 1):
        print(f"  {i:<4} | {feat:<25} | {score:.3f}")
        
    # ================================================================
    #  PART 5: Save Model
    # ================================================================
    print("\n" + "=" * 55)
    print("  PART 5: SAVING MODEL")
    print("=" * 55)
    
    model.save_model(MODEL_FILE)
    print(f"[OK] {MODEL_FILE} saved successfully")
    
    with open(FEATURES_FILE, 'w') as f:
        json.dump(list(X.columns), f)
    print(f"[OK] {FEATURES_FILE} saved successfully")
    
    print("\n  Model is ready for edge weight computation\n")


if __name__ == "__main__":
    main()
