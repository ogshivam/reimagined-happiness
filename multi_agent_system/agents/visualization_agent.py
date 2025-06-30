"""
Visualization Agent - Creates charts and visual representations
"""
import logging
from typing import Dict, List, Any, Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Import settings with fallback for your project structure
try:
    from config.settings import settings
except ImportError:
    # Fallback: create a simple settings object for your project
    class SimpleSettings:
        def __init__(self):
            self.database_path = "chinook.db"
            self.model_name = "meta-llama/Llama-3-70b-chat-hf"
    
    settings = SimpleSettings()
from memory.vector_store import ConversationVectorStore

logger = logging.getLogger(__name__)

class ChartTypeDetector:
    """Intelligent chart type detection based on data characteristics"""
    
    @staticmethod
    def suggest_chart_types(df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Suggest appropriate chart types based on data analysis"""
        suggestions = []
        
        # Analyze columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = []
        
        for col in df.columns:
            if col not in numeric_cols and df[col].nunique() <= 20:
                categorical_cols.append(col)
        
        # One categorical, one numeric -> Bar chart
        if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
            suggestions.append({
                "chart_type": "bar",
                "columns": {"x": categorical_cols[0], "y": numeric_cols[0]},
                "title": f"{numeric_cols[0]} by {categorical_cols[0]}",
                "priority": 9
            })
            
            if df[categorical_cols[0]].nunique() <= 10:
                suggestions.append({
                    "chart_type": "pie", 
                    "columns": {"names": categorical_cols[0], "values": numeric_cols[0]},
                    "title": f"{numeric_cols[0]} Distribution",
                    "priority": 7
                })
        
        # Two numeric columns -> Scatter plot
        if len(numeric_cols) >= 2:
            suggestions.append({
                "chart_type": "scatter",
                "columns": {"x": numeric_cols[0], "y": numeric_cols[1]},
                "title": f"{numeric_cols[1]} vs {numeric_cols[0]}",
                "priority": 8
            })
        
        # Single numeric -> Histogram
        if len(numeric_cols) >= 1:
            suggestions.append({
                "chart_type": "histogram",
                "columns": {"x": numeric_cols[0]},
                "title": f"Distribution of {numeric_cols[0]}",
                "priority": 6
            })
        
        # Box plot for categorical vs numeric
        if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
            suggestions.append({
                "chart_type": "box",
                "columns": {"x": categorical_cols[0], "y": numeric_cols[0]},
                "title": f"{numeric_cols[0]} by {categorical_cols[0]}",
                "priority": 7
            })
        
        # Sort by priority and return top suggestions
        suggestions.sort(key=lambda x: x["priority"], reverse=True)
        return suggestions[:3]

class VisualizationAgent:
    """Main visualization agent that creates charts"""
    
    def __init__(self):
        self.detector = ChartTypeDetector()
        self.color_palette = px.colors.qualitative.Set3
    
    def create_visualizations(self, df: pd.DataFrame, question: str = None) -> Dict[str, Any]:
        """Create visualizations for the given data"""
        try:
            if df.empty:
                return {"success": False, "error": "Empty dataset", "charts": []}
            
            # Get chart suggestions
            suggestions = self.detector.suggest_chart_types(df)
            
            if not suggestions:
                return {"success": False, "error": "No suitable charts found", "charts": []}
            
            # Generate charts
            charts = []
            for suggestion in suggestions:
                chart = self._generate_chart(df, suggestion)
                if chart:
                    charts.append(chart)
            
            result = {
                "success": True,
                "charts": charts,
                "insights": self._generate_insights(df),
                "chart_count": len(charts)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error creating visualizations: {str(e)}")
            return {"success": False, "error": str(e), "charts": []}
    
    def _generate_chart(self, df: pd.DataFrame, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate a single chart"""
        try:
            chart_type = config["chart_type"]
            
            if chart_type == "bar":
                fig = px.bar(df, x=config["columns"]["x"], y=config["columns"]["y"], 
                           title=config["title"], color_discrete_sequence=self.color_palette)
            elif chart_type == "pie":
                fig = px.pie(df, names=config["columns"]["names"], values=config["columns"]["values"],
                           title=config["title"], color_discrete_sequence=self.color_palette)
            elif chart_type == "scatter":
                fig = px.scatter(df, x=config["columns"]["x"], y=config["columns"]["y"],
                               title=config["title"], color_discrete_sequence=self.color_palette)
            elif chart_type == "histogram":
                fig = px.histogram(df, x=config["columns"]["x"], title=config["title"],
                                 color_discrete_sequence=self.color_palette)
            elif chart_type == "box":
                fig = px.box(df, x=config["columns"]["x"], y=config["columns"]["y"],
                           title=config["title"], color_discrete_sequence=self.color_palette)
            else:
                return None
            
            fig.update_layout(width=800, height=600)
            
            return {
                "figure": fig,
                "config": config,
                "chart_type": chart_type,
                "title": config["title"]
            }
            
        except Exception as e:
            logger.error(f"Error generating chart: {str(e)}")
            return None
    
    def _generate_insights(self, df: pd.DataFrame) -> List[str]:
        """Generate basic insights about the data"""
        insights = []
        insights.append(f"Dataset contains {len(df)} records with {len(df.columns)} columns")
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            insights.append(f"Found {len(numeric_cols)} numeric columns")
        
        return insights 