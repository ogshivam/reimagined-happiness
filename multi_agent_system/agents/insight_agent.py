"""
Insight Agent - Provides business intelligence and pattern detection
"""
import logging
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from scipy import stats
from langchain_together import Together

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
from utils.rate_limiter import with_rate_limit, rate_limiter

logger = logging.getLogger(__name__)

class InsightAgent:
    """Generates business insights and detects patterns in data"""
    
    def __init__(self):
        self.llm = Together(
            model=settings.llm_model,
            temperature=0.3,  # Lower temperature for more focused insights
            max_tokens=2000,
            together_api_key=settings.together_api_key
        )
        self.vector_store = ConversationVectorStore()
    
    def generate_insights(self, df: pd.DataFrame, question: str = None, 
                         context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate comprehensive insights from data"""
        try:
            if df.empty:
                return {"success": False, "error": "Empty dataset", "insights": []}
            
            insights = {
                "statistical_insights": self._generate_statistical_insights(df),
                "business_insights": self._generate_business_insights(df, question),
                "pattern_insights": self._detect_patterns(df),
                "data_quality_insights": self._analyze_data_quality(df),
                "recommendations": self._generate_recommendations(df, question)
            }
            
            # Generate AI-powered insights using LLM
            ai_insights = self._generate_ai_insights(df, question, insights)
            insights["ai_insights"] = ai_insights
            
            # Store insights in vector store
            if question:
                insight_text = f"Generated insights for: {question}"
                self.vector_store.add_insight(
                    insight_text=insight_text,
                    insight_type="business_intelligence",
                    data_context=f"Dataset: {len(df)} rows, {len(df.columns)} columns",
                    metadata={"agent_type": "insight_agent", "question": question}
                )
            
            return {"success": True, "insights": insights}
            
        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            return {"success": False, "error": str(e), "insights": {}}
    
    def _generate_statistical_insights(self, df: pd.DataFrame) -> List[str]:
        """Generate statistical insights about the data"""
        insights = []
        
        # Basic statistics
        insights.append(f"Dataset contains {len(df)} records and {len(df.columns)} columns")
        
        # Numeric column analysis
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            insights.append(f"Found {len(numeric_cols)} numeric columns")
            
            for col in numeric_cols[:3]:  # Analyze top 3 numeric columns
                col_data = df[col].dropna()
                if len(col_data) > 0:
                    mean_val = col_data.mean()
                    std_val = col_data.std()
                    cv = (std_val / mean_val) * 100 if mean_val != 0 else 0
                    
                    insights.append(f"{col}: Mean={mean_val:.2f}, Std={std_val:.2f}, CV={cv:.1f}%")
        
        # Categorical column analysis
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        if len(categorical_cols) > 0:
            for col in categorical_cols[:2]:  # Analyze top 2 categorical columns
                unique_count = df[col].nunique()
                total_count = len(df[col].dropna())
                if total_count > 0:
                    diversity = (unique_count / total_count) * 100
                    insights.append(f"{col}: {unique_count} unique values ({diversity:.1f}% diversity)")
        
        return insights
    
    def _generate_business_insights(self, df: pd.DataFrame, question: str = None) -> List[str]:
        """Generate business-focused insights"""
        insights = []
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        # Revenue/Sales patterns (if applicable)
        revenue_cols = [col for col in numeric_cols if any(keyword in col.lower() 
                       for keyword in ['revenue', 'sales', 'amount', 'total', 'price'])]
        
        for col in revenue_cols[:2]:
            col_data = df[col].dropna()
            if len(col_data) > 0:
                total_value = col_data.sum()
                insights.append(f"Total {col}: {total_value:,.2f}")
                
                # Top contributors
                if len(df.columns) > 1:
                    # Find categorical column to group by
                    cat_cols = df.select_dtypes(include=['object', 'category']).columns
                    if len(cat_cols) > 0:
                        grouped = df.groupby(cat_cols[0])[col].sum().sort_values(ascending=False)
                        top_contributor = grouped.index[0]
                        top_value = grouped.iloc[0]
                        contribution_pct = (top_value / total_value) * 100
                        insights.append(f"Top {cat_cols[0]} by {col}: {top_contributor} ({contribution_pct:.1f}%)")
        
        # Growth/Trend analysis (if date columns exist)
        date_cols = df.select_dtypes(include=['datetime64']).columns
        if len(date_cols) > 0 and len(numeric_cols) > 0:
            insights.append("Time-series data detected - trend analysis possible")
        
        return insights
    
    def _detect_patterns(self, df: pd.DataFrame) -> List[str]:
        """Detect patterns and anomalies in the data"""
        patterns = []
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        # Correlation analysis
        if len(numeric_cols) >= 2:
            corr_matrix = df[numeric_cols].corr()
            
            # Find strong correlations
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    corr_val = corr_matrix.iloc[i, j]
                    if abs(corr_val) > 0.7:  # Strong correlation threshold
                        col1, col2 = corr_matrix.columns[i], corr_matrix.columns[j]
                        correlation_type = "positive" if corr_val > 0 else "negative"
                        patterns.append(f"Strong {correlation_type} correlation between {col1} and {col2} (r={corr_val:.3f})")
        
        # Outlier detection
        for col in numeric_cols[:3]:
            col_data = df[col].dropna()
            if len(col_data) > 10:  # Need sufficient data
                Q1 = col_data.quantile(0.25)
                Q3 = col_data.quantile(0.75)
                IQR = Q3 - Q1
                outliers = col_data[(col_data < Q1 - 1.5*IQR) | (col_data > Q3 + 1.5*IQR)]
                if len(outliers) > 0:
                    outlier_pct = (len(outliers) / len(col_data)) * 100
                    patterns.append(f"{col}: {len(outliers)} outliers detected ({outlier_pct:.1f}%)")
        
        return patterns
    
    def _analyze_data_quality(self, df: pd.DataFrame) -> List[str]:
        """Analyze data quality issues"""
        quality_issues = []
        
        # Missing data analysis
        missing_data = df.isnull().sum()
        total_missing = missing_data.sum()
        
        if total_missing > 0:
            missing_pct = (total_missing / (len(df) * len(df.columns))) * 100
            quality_issues.append(f"Missing data: {total_missing} values ({missing_pct:.1f}% of dataset)")
            
            # Columns with high missing data
            high_missing = missing_data[missing_data > len(df) * 0.1]  # >10% missing
            if len(high_missing) > 0:
                quality_issues.append(f"Columns with >10% missing data: {list(high_missing.index)}")
        
        # Duplicate rows
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            dup_pct = (duplicates / len(df)) * 100
            quality_issues.append(f"Duplicate rows: {duplicates} ({dup_pct:.1f}%)")
        
        # Data type consistency
        for col in df.columns:
            if df[col].dtype == 'object':
                # Check for mixed types in object columns
                non_null_values = df[col].dropna()
                if len(non_null_values) > 0:
                    # Check if numeric values are stored as strings
                    numeric_strings = pd.to_numeric(non_null_values, errors='coerce').notna().sum()
                    if numeric_strings > len(non_null_values) * 0.8:  # >80% numeric
                        quality_issues.append(f"{col}: Appears to contain numeric data stored as text")
        
        return quality_issues
    
    def _generate_recommendations(self, df: pd.DataFrame, question: str = None) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Data visualization recommendations
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        
        if len(numeric_cols) >= 2:
            recommendations.append("Consider scatter plots to explore relationships between numeric variables")
        
        if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
            recommendations.append("Bar charts would effectively show distributions across categories")
        
        # Analysis recommendations
        if len(df) > 1000:
            recommendations.append("Large dataset - consider sampling for initial exploration")
        
        missing_data = df.isnull().sum().sum()
        if missing_data > 0:
            recommendations.append("Address missing data before conducting detailed analysis")
        
        # Business recommendations based on question
        if question and any(keyword in question.lower() for keyword in ['revenue', 'sales', 'profit']):
            recommendations.append("Focus on top performers and identify growth opportunities")
        
        return recommendations
    
    def _generate_ai_insights(self, df: pd.DataFrame, question: str, 
                             existing_insights: Dict[str, Any]) -> List[str]:
        """Generate AI-powered insights using LLM"""
        try:
            # Prepare data summary for LLM
            data_summary = f"""
            Dataset Summary:
            - Rows: {len(df)}
            - Columns: {len(df.columns)}
            - Column names: {', '.join(df.columns[:10])}
            - Data types: {df.dtypes.value_counts().to_dict()}
            
            Statistical Insights: {existing_insights.get('statistical_insights', [])}
            Business Insights: {existing_insights.get('business_insights', [])}
            Patterns: {existing_insights.get('pattern_insights', [])}
            """
            
            prompt = f"""
            As a data analyst, provide 3-5 key insights about this dataset:
            
            {data_summary}
            
            User Question: {question or 'General analysis'}
            
            Focus on:
            1. Most important findings
            2. Business implications
            3. Actionable recommendations
            
            Provide concise, specific insights:
            """
            
            response = rate_limiter.retry_with_backoff(self.llm, prompt)
            
            # Parse response into individual insights
            insights = []
            for line in response.split('\n'):
                line = line.strip()
                if line and len(line) > 10:  # Filter out short/empty lines
                    # Remove numbering and bullet points
                    cleaned_line = line.lstrip('123456789.-• ')
                    if cleaned_line:
                        insights.append(cleaned_line)
            
            return insights[:5]  # Return top 5 AI insights
            
        except Exception as e:
            logger.error(f"Error generating AI insights: {str(e)}")
            return ["AI insight generation temporarily unavailable"] 