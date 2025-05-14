"""
Metrics utilities for tracking performance and analyzing results.
"""

from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime


class PerformanceMetrics:
    def __init__(self):
        self.metrics_history = []

    def record_generation(
        self,
        prompt: str,
        response: str,
        validation_results: Dict[str, any],
        generation_time: float,
        technique: str,
    ) -> None:
        """Record metrics for a single generation."""
        metrics = {
            "timestamp": datetime.now(),
            "technique": technique,
            "prompt_length": len(prompt.split()),
            "response_length": len(response.split()),
            "generation_time": generation_time,
            "style_adherence_score": validation_results["style_adherence"][
                "adherence_score"
            ],
            "coherence_score": validation_results["coherence"]["is_coherent"],
            "is_valid_length": validation_results["length"]["is_valid"],
        }

        self.metrics_history.append(metrics)

    def get_summary(self) -> Dict[str, any]:
        """Get summary statistics of all generations."""
        if not self.metrics_history:
            return {}

        df = pd.DataFrame(self.metrics_history)

        return {
            "total_generations": len(df),
            "avg_generation_time": df["generation_time"].mean(),
            "avg_style_adherence": df["style_adherence_score"].mean(),
            "avg_coherence": df["coherence_score"].mean(),
            "technique_performance": df.groupby("technique")
            .agg(
                {
                    "style_adherence_score": "mean",
                    "coherence_score": "mean",
                    "generation_time": "mean",
                }
            )
            .to_dict(),
        }

    def get_technique_comparison(self) -> Dict[str, any]:
        """Compare performance across different techniques."""
        if not self.metrics_history:
            return {}

        df = pd.DataFrame(self.metrics_history)

        return {
            technique: {
                "count": len(group),
                "avg_style_score": group["style_adherence_score"].mean(),
                "avg_coherence": group["coherence_score"].mean(),
                "avg_time": group["generation_time"].mean(),
            }
            for technique, group in df.groupby("technique")
        }

    def export_metrics(self, filepath: str) -> None:
        """Export metrics to CSV file."""
        if not self.metrics_history:
            return

        df = pd.DataFrame(self.metrics_history)
        df.to_csv(filepath, index=False)


def calculate_performance_metrics(generations: List[Dict[str, any]]) -> Dict[str, any]:
    """Calculate performance metrics from a list of generations."""
    metrics = PerformanceMetrics()

    for gen in generations:
        metrics.record_generation(
            prompt=gen["prompt"],
            response=gen["response"],
            validation_results=gen["validation"],
            generation_time=gen["time"],
            technique=gen["technique"],
        )

    return metrics.get_summary()
