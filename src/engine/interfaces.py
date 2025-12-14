from abc import ABC, abstractmethod
from typing import Any, Dict, List
import numpy as np

class SimilarityStrategy(ABC):
    @abstractmethod
    def compute(self, features: np.ndarray) -> np.ndarray:
        """Compute similarity scores for the given features."""
        pass

    @abstractmethod
    def compute_pairwise(
        self, 
        features_A: np.ndarray, 
        features_B: np.ndarray
    ) -> np.ndarray:
        """Compute pairwise similarity scores between two sets of features."""
        pass

class Recommender(ABC):
    @abstractmethod
    def recommend(
        self, 
        id: int,
        k: int = 10
    ) -> List[Dict]:
        """Generate top-k recommendations for a given entity ID."""
        pass

    @abstractmethod
    def recommend_batch(
        self, 
        ids: List[int], 
        k: int = 10
    ) -> Dict[int, List[Dict]]:
        """Generate top-k recommendations for a batch of entity IDs."""
        pass