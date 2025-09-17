import pickle
import os
from typing import Dict, Any, Optional
import pandas as pd

def save_minimal_state(exp_name: str, exp_params, levels_df, mice_dict, txt_file_name: str, txt_file_path: str, user_email: str = "") -> str:
    """
    שומר את המצב המינימלי של הניסוי בתיקיית הניסוי
    מחזיר את הנתיב שבו נשמר המצב
    """
    try:
        # יצירת תיקיית הניסוי אם לא קיימת
        folder_path = os.path.join(os.getcwd(), "experiments", exp_name)
        os.makedirs(folder_path, exist_ok=True)
        
        # נתיב לקובץ המצב
        state_file_path = os.path.join(folder_path, "minimal_state.pkl")
        
        # הכנת הנתונים לשמירה
        state_data = {
            'exp_params': exp_params,
            'levels_df': levels_df,
            'mice_dict': mice_dict,
            'txt_file_name': txt_file_name,
            'txt_file_path': txt_file_path,
            'user_email': user_email,
        }
        
        # שמירה עם pickle
        with open(state_file_path, 'wb') as f:
            pickle.dump(state_data, f)
        
        print(f"State saved to: {state_file_path}")
        return state_file_path
        
    except Exception as e:
        print(f"Error saving state: {e}")
        return None

def load_minimal_state(exp_name: str) -> Optional[Dict[str, Any]]:
    """
    טוען את המצב המינימלי של הניסוי מתיקיית הניסוי
    מחזיר None אם לא נמצא קובץ מצב
    """
    try:
        # נתיב לקובץ המצב
        folder_path = os.path.join(os.getcwd(), "experiments", exp_name)
        state_file_path = os.path.join(folder_path, "minimal_state.pkl")
        
        # בדיקה אם קובץ המצב קיים
        if not os.path.exists(state_file_path):
            print(f"No state file found at: {state_file_path}")
            return None
        
        # טעינת המצב
        with open(state_file_path, 'rb') as f:
            state_data = pickle.load(f)
        
        print(f"State loaded from: {state_file_path}")
        return state_data
        
    except Exception as e:
        print(f"Error loading state: {e}")
        return None

def check_if_restart_available(exp_name: str) -> bool:
    """
    בודק אם יש קובץ מצב זמין לניסוי מסוים
    """
    try:
        folder_path = os.path.join(os.getcwd(), "experiments", exp_name)
        state_file_path = os.path.join(folder_path, "minimal_state.pkl")
        return os.path.exists(state_file_path)
    except:
        return False
