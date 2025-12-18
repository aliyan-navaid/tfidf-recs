from typing import Any
from pathlib import Path

def load_json(file_path: Path) -> Any:
    with open(file_path, 'r', encoding='utf-8') as f:
        import json
        return json.load(f)
    
def save_json(data: Any, file_path: Path) -> None:
    with open(file_path, 'w', encoding='utf-8') as f:
        import json
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_yaml(file_path: Path) -> Any:
    with open(file_path, 'r', encoding='utf-8') as f:
        import yaml
        return yaml.safe_load(f)
    
def save_yaml(data: Any, file_path: Path) -> None:
    with open(file_path, 'w', encoding='utf-8') as f:
        import yaml
        yaml.dump(data, f, default_flow_style=False)

def load_pickle(file_path: Path) -> Any:
    with open(file_path, 'rb') as f:
        import pickle
        return pickle.load(f)
    
def save_pickle(data: Any, file_path: Path) -> None:
    with open(file_path, 'wb') as f:
        import pickle
        pickle.dump(data, f)

def load_joblib(file_path: Path) -> Any:
    import joblib
    return joblib.load(file_path)

def save_joblib(data: Any, file_path: Path) -> None:
    import joblib
    joblib.dump(data, file_path)

def load_npz(file_path: Path) -> Any:
    """Load npz file - handles both scipy sparse matrices and numpy arrays."""
    try:
        from scipy.sparse import load_npz as scipy_load_npz
        return scipy_load_npz(file_path)
    except:
        import numpy as np
        return np.load(file_path, allow_pickle=True)

def save_npz(data: Any, file_path: Path) -> None:
    """Save npz file - handles both scipy sparse matrices and numpy arrays."""
    try:
        from scipy.sparse import issparse, save_npz as scipy_save_npz
        if issparse(data):
            scipy_save_npz(file_path, data)
        else:
            import numpy as np
            np.savez_compressed(file_path, data=data)
    except ImportError:
        import numpy as np
        np.savez_compressed(file_path, data=data)

def load_parquet(file_path: Path) -> Any:
    import pandas as pd
    return pd.read_parquet(file_path)

def save_parquet(data: Any, file_path: Path) -> None:
    import pandas as pd
    if isinstance(data, pd.DataFrame):
        data.to_parquet(file_path)
    else:
        raise ValueError("Data must be a pandas DataFrame for parquet format")
    

__all__ = [
    "load_json",
    "save_json",
    "load_yaml",
    "save_yaml",
    "load_pickle",
    "save_pickle",
    "load_joblib",
    "save_joblib",
    "load_npz",
    "save_npz",
    "load_parquet",
    "save_parquet",
]