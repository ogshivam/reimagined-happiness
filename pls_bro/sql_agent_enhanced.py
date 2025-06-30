"""
Enhanced SQL Agent with Advanced Visualization & Reporting Capabilities.
Extends the LangGraph SQL agent with automatic chart detection, interactive dashboards, and export features.
"""

import os
import io
import base64
from typing import Dict, Any, List, Annotated, Literal, Optional, Tuple
from langchain_together import ChatTogether
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from database_tools import DatabaseManager, create_database_tools, get_chinook_schema_description
import pandas as pd
import numpy as np
from pydantic import BaseModel
from typing_extensions import TypedDict
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
import streamlit as st
from datetime import datetime
import json

def convert_numpy_types(obj):
    """Convert numpy types to native Python types for serialization."""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_numpy_types(list(obj)))
    return obj

# Enhanced state for visualization features
class EnhancedAgentState(TypedDict):
    # Original agent state fields
    messages: Annotated[list, add_messages]
    question: str
    current_step: str
    tables_fetched: bool
    relevant_tables: List[str]
    schema_info: str
    sql_query: str
    query_valid: bool
    query_results: str
    error_count: int
    max_errors: int
    final_answer: str
    
    # Enhanced visualization fields
    raw_data: Optional[Dict[str, Any]]  # Store as dict instead of DataFrame
    data_analysis: Dict[str, Any]
    suggested_charts: List[Dict[str, Any]]
    selected_chart_type: Optional[str]
    visualization_config: Dict[str, Any]
    generated_charts: List[Dict[str, Any]]
    export_options: List[str]
    dashboard_layout: Optional[Dict[str, Any]]
    visualization_insights: List[str]

class ChartTypeDetector:
    """Intelligent chart type detection based on data characteristics."""
    
    @staticmethod
    def analyze_data(df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze DataFrame to determine optimal visualization types."""
        if df.empty:
            return {"error": "No data to analyze"}
        
        analysis = {
            "num_rows": len(df),
            "num_columns": len(df.columns),
            "column_types": {},
            "unique_counts": {},
            "null_counts": {},
            "numeric_columns": [],
            "categorical_columns": [],
            "datetime_columns": [],
            "high_cardinality_columns": [],
            "low_cardinality_columns": []
        }
        
        for col in df.columns:
            dtype = str(df[col].dtype)
            unique_count = df[col].nunique()
            null_count = df[col].isnull().sum()
            
            analysis["column_types"][col] = dtype
            analysis["unique_counts"][col] = unique_count
            analysis["null_counts"][col] = null_count
            
            # Categorize columns
            if df[col].dtype in ['int64', 'float64', 'int32', 'float32']:
                analysis["numeric_columns"].append(col)
            elif df[col].dtype == 'datetime64[ns]' or 'date' in col.lower():
                analysis["datetime_columns"].append(col)
            else:
                analysis["categorical_columns"].append(col)
            
            # Cardinality analysis
            cardinality_ratio = unique_count / len(df)
            if cardinality_ratio > 0.8:
                analysis["high_cardinality_columns"].append(col)
            elif cardinality_ratio < 0.1:
                analysis["low_cardinality_columns"].append(col)
        
        return analysis
    
    @staticmethod
    def suggest_chart_types(df: pd.DataFrame, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest appropriate chart types based on data analysis."""
        suggestions = []
        
        num_rows = analysis["num_rows"]
        num_cols = analysis["num_columns"]
        numeric_cols = analysis["numeric_columns"]
        categorical_cols = analysis["categorical_columns"]
        datetime_cols = analysis["datetime_columns"]
        low_card_cols = analysis["low_cardinality_columns"]
        
        # Single numeric column
        if len(numeric_cols) == 1 and num_cols == 1:
            suggestions.append({
                "type": "histogram",
                "title": f"Distribution of {numeric_cols[0]}",
                "description": "Shows the distribution of values",
                "columns": {"x": numeric_cols[0]},
                "priority": 8
            })
        
        # Single categorical column with counts
        if len(categorical_cols) == 1 and num_cols == 1:
            suggestions.append({
                "type": "bar",
                "title": f"Count by {categorical_cols[0]}",
                "description": "Shows frequency of each category",
                "columns": {"x": categorical_cols[0], "y": "count"},
                "priority": 9
            })
        
        # One categorical + one numeric (more flexible - check unique count directly)
        if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
            # Find categorical columns with reasonable number of unique values
            suitable_cat_cols = [c for c in categorical_cols 
                               if analysis["unique_counts"][c] <= 20]  # Up to 20 categories
            
            if not suitable_cat_cols and categorical_cols:
                # If no low-cardinality columns, use the first categorical column anyway
                suitable_cat_cols = [categorical_cols[0]]
            
            if suitable_cat_cols:
                cat_col = suitable_cat_cols[0]
                suggestions.append({
                    "type": "bar",
                    "title": f"{numeric_cols[0]} by {cat_col}",
                    "description": "Compare values across categories",
                    "columns": {"x": cat_col, "y": numeric_cols[0]},
                    "priority": 9
                })
                
                if analysis["unique_counts"][cat_col] <= 10:
                    suggestions.append({
                        "type": "pie",
                        "title": f"Distribution of {numeric_cols[0]} by {cat_col}",
                        "description": "Shows proportional breakdown",
                        "columns": {"names": cat_col, "values": numeric_cols[0]},
                        "priority": 7
                    })
        
        # Time series data
        if datetime_cols and numeric_cols:
            suggestions.append({
                "type": "line",
                "title": f"{numeric_cols[0]} over time",
                "description": "Shows trend over time",
                "columns": {"x": datetime_cols[0], "y": numeric_cols[0]},
                "priority": 10
            })
        
        # Two numeric columns - scatter plot
        if len(numeric_cols) >= 2:
            suggestions.append({
                "type": "scatter",
                "title": f"{numeric_cols[1]} vs {numeric_cols[0]}",
                "description": "Shows relationship between two variables",
                "columns": {"x": numeric_cols[0], "y": numeric_cols[1]},
                "priority": 8
            })
        
        # Multiple numeric columns - correlation heatmap
        if len(numeric_cols) >= 3:
            suggestions.append({
                "type": "heatmap",
                "title": "Correlation Matrix",
                "description": "Shows relationships between all numeric variables",
                "columns": {"data": numeric_cols},
                "priority": 6
            })
        
        # Box plot for numeric data grouped by category (more flexible)
        if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
            suitable_cat_cols = [c for c in categorical_cols 
                               if analysis["unique_counts"][c] <= 15]
            
            if suitable_cat_cols:
                cat_col = suitable_cat_cols[0]
                suggestions.append({
                    "type": "box",
                    "title": f"Distribution of {numeric_cols[0]} by {cat_col}",
                    "description": "Shows distribution across categories",
                    "columns": {"x": cat_col, "y": numeric_cols[0]},
                    "priority": 7
                })
        
        # Sort by priority
        suggestions.sort(key=lambda x: x["priority"], reverse=True)
        
        return suggestions[:5]  # Return top 5 suggestions

class VisualizationGenerator:
    """Generate interactive Plotly visualizations."""
    
    @staticmethod
    def create_chart(df: pd.DataFrame, chart_config: Dict[str, Any]) -> go.Figure:
        """Create a Plotly chart based on configuration."""
        chart_type = chart_config["type"]
        columns = chart_config["columns"]
        title = chart_config["title"]
        
        fig = None
        
        try:
            if chart_type == "bar":
                if "y" in columns and columns["y"] == "count":
                    # Count plot
                    value_counts = df[columns["x"]].value_counts()
                    fig = px.bar(
                        x=value_counts.index,
                        y=value_counts.values,
                        title=title,
                        labels={"x": columns["x"], "y": "Count"}
                    )
                else:
                    fig = px.bar(
                        df,
                        x=columns["x"],
                        y=columns["y"],
                        title=title
                    )
            
            elif chart_type == "line":
                fig = px.line(
                    df,
                    x=columns["x"],
                    y=columns["y"],
                    title=title
                )
            
            elif chart_type == "scatter":
                fig = px.scatter(
                    df,
                    x=columns["x"],
                    y=columns["y"],
                    title=title
                )
            
            elif chart_type == "pie":
                fig = px.pie(
                    df,
                    names=columns["names"],
                    values=columns["values"],
                    title=title
                )
            
            elif chart_type == "histogram":
                fig = px.histogram(
                    df,
                    x=columns["x"],
                    title=title
                )
            
            elif chart_type == "box":
                fig = px.box(
                    df,
                    x=columns["x"],
                    y=columns["y"],
                    title=title
                )
            
            elif chart_type == "heatmap":
                correlation_matrix = df[columns["data"]].corr()
                fig = px.imshow(
                    correlation_matrix,
                    title=title,
                    color_continuous_scale="RdBu_r",
                    aspect="auto"
                )
            
            if fig:
                # Common styling
                fig.update_layout(
                    template="plotly_white",
                    font=dict(size=12),
                    title_font_size=16,
                    showlegend=True if chart_type in ["pie", "scatter"] else False
                )
                
                # Make it responsive
                fig.update_layout(
                    autosize=True,
                    margin=dict(l=40, r=40, t=60, b=40)
                )
            
        except Exception as e:
            # Fallback to simple table
            fig = go.Figure(data=[go.Table(
                header=dict(values=list(df.columns)),
                cells=dict(values=[df[col] for col in df.columns])
            )])
            fig.update_layout(title=f"Data Table (Chart Error: {str(e)})")
        
        return fig
    
    @staticmethod
    def export_chart(fig: go.Figure, format_type: str, filename: str) -> str:
        """Export chart in specified format."""
        if format_type == "html":
            return fig.to_html(include_plotlyjs='cdn')
        elif format_type == "png":
            img_bytes = pio.to_image(fig, format="png")
            return base64.b64encode(img_bytes).decode()
        elif format_type == "svg":
            return pio.to_image(fig, format="svg").decode()
        elif format_type == "json":
            return fig.to_json()
        else:
            return fig.to_html()

class BusinessVisualizationTemplates:
    """Pre-built visualization templates for common business scenarios."""
    
    @staticmethod
    def get_templates() -> Dict[str, Dict[str, Any]]:
        """Return business visualization templates."""
        return {
            "sales_performance": {
                "name": "Sales Performance Dashboard",
                "description": "Revenue, trends, and top performers",
                "required_columns": ["date", "revenue", "product/category"],
                "charts": [
                    {"type": "line", "title": "Revenue Trend", "priority": 1},
                    {"type": "bar", "title": "Top Products", "priority": 2},
                    {"type": "pie", "title": "Revenue by Category", "priority": 3}
                ]
            },
            "customer_analysis": {
                "name": "Customer Analysis",
                "description": "Customer behavior and demographics",
                "required_columns": ["customer", "region/country", "orders/revenue"],
                "charts": [
                    {"type": "bar", "title": "Customers by Region", "priority": 1},
                    {"type": "histogram", "title": "Customer Value Distribution", "priority": 2},
                    {"type": "scatter", "title": "Orders vs Revenue", "priority": 3}
                ]
            },
            "inventory_monitoring": {
                "name": "Inventory Monitoring",
                "description": "Stock levels and movement",
                "required_columns": ["product", "quantity", "category"],
                "charts": [
                    {"type": "bar", "title": "Stock Levels by Product", "priority": 1},
                    {"type": "pie", "title": "Inventory by Category", "priority": 2}
                ]
            },
            "financial_overview": {
                "name": "Financial Overview",
                "description": "Revenue, costs, and profitability",
                "required_columns": ["period", "revenue", "cost/profit"],
                "charts": [
                    {"type": "line", "title": "Financial Trend", "priority": 1},
                    {"type": "bar", "title": "Revenue vs Cost", "priority": 2}
                ]
            }
        }
    
    @staticmethod
    def match_template(df: pd.DataFrame, analysis: Dict[str, Any]) -> Optional[str]:
        """Match data to the most appropriate business template."""
        columns = [col.lower() for col in df.columns]
        templates = BusinessVisualizationTemplates.get_templates()
        
        best_match = None
        best_score = 0
        
        for template_id, template in templates.items():
            score = 0
            required_concepts = template["required_columns"]
            
            for concept in required_concepts:
                concept_parts = concept.split("/")
                if any(any(part in col for col in columns) for part in concept_parts):
                    score += 1
            
            if score > best_score and score >= len(required_concepts) / 2:
                best_score = score
                best_match = template_id
        
        return best_match

class EnhancedSQLAgent:
    """Enhanced SQL Agent with advanced visualization capabilities."""
    
    def __init__(self, database_path: str = "chinook.db", model: str = "meta-llama/Llama-3-70b-chat-hf", api_key: str = None):
        """Initialize the enhanced SQL agent."""
        from config import TOGETHER_API_KEY
        
        self.database_path = database_path
        self.db_manager = DatabaseManager(database_path)
        
        # Use provided API key or fall back to config
        effective_api_key = api_key or TOGETHER_API_KEY
        
        if not effective_api_key:
            raise ValueError("TOGETHER_API_KEY must be set either as parameter or environment variable")
        
        self.llm = ChatTogether(
            model=model,
            together_api_key=effective_api_key,
            temperature=0
        )
        
        # Don't use the problematic toolkit for now
        # self.db_manager, self.toolkit = create_database_tools(database_path, model, api_key)
        # self.tools = self.toolkit.get_tools()
        
        # Initialize visualization components
        self.chart_detector = ChartTypeDetector()
        self.viz_generator = VisualizationGenerator()
        self.templates = BusinessVisualizationTemplates()
        
        # Memory for session persistence (must be initialized before graph creation)
        import sqlite3
        conn = sqlite3.connect(":memory:", check_same_thread=False)
        self.memory = SqliteSaver(conn)
        
        # Create the enhanced agent graph
        self.graph = self._create_enhanced_agent_graph()
    
    def _create_enhanced_agent_graph(self) -> StateGraph:
        """Create the enhanced LangGraph workflow with visualization capabilities."""
        
        workflow = StateGraph(EnhancedAgentState)
        
        # Original nodes
        workflow.add_node("fetch_tables", self._fetch_tables_node)
        workflow.add_node("decide_relevance", self._decide_relevance_node)
        workflow.add_node("get_schemas", self._get_schemas_node)
        workflow.add_node("generate_query", self._generate_query_node)
        workflow.add_node("validate_query", self._validate_query_node)
        workflow.add_node("execute_query", self._execute_query_node)
        workflow.add_node("fix_errors", self._fix_errors_node)
        
        # New visualization nodes
        workflow.add_node("analyze_data", self._analyze_data_node)
        workflow.add_node("detect_chart_types", self._detect_chart_types_node)
        workflow.add_node("generate_visualizations", self._generate_visualizations_node)
        workflow.add_node("create_dashboard", self._create_dashboard_node)
        workflow.add_node("generate_insights", self._generate_insights_node)
        workflow.add_node("finalize_response", self._finalize_response_node)
        
        # Set entry point
        workflow.set_entry_point("fetch_tables")
        
        # Original workflow edges
        workflow.add_edge("fetch_tables", "decide_relevance")
        workflow.add_edge("decide_relevance", "get_schemas")
        workflow.add_edge("get_schemas", "generate_query")
        workflow.add_edge("generate_query", "validate_query")
        
        # Enhanced conditional edges
        workflow.add_conditional_edges(
            "validate_query",
            self._validate_query_condition,
            {
                "execute": "execute_query",
                "fix": "fix_errors"
            }
        )
        
        workflow.add_conditional_edges(
            "execute_query",
            self._execute_query_condition,
            {
                "success": "analyze_data",
                "error": "fix_errors"
            }
        )
        
        workflow.add_conditional_edges(
            "fix_errors",
            self._fix_errors_condition,
            {
                "retry": "generate_query",
                "give_up": "finalize_response"
            }
        )
        
        # New visualization workflow
        workflow.add_edge("analyze_data", "detect_chart_types")
        workflow.add_edge("detect_chart_types", "generate_visualizations")
        workflow.add_edge("generate_visualizations", "create_dashboard")
        workflow.add_edge("create_dashboard", "generate_insights")
        workflow.add_edge("generate_insights", "finalize_response")
        workflow.add_edge("finalize_response", END)
        
        # Compile without checkpointer for now to avoid serialization issues
        return workflow.compile()
    
    # Original agent nodes (preserved from original implementation)
    def _fetch_tables_node(self, state: EnhancedAgentState) -> EnhancedAgentState:
        """Fetch all available tables from the database."""
        try:
            tables = self.db_manager.list_tables()
            state["tables_fetched"] = True
            state["current_step"] = "tables_fetched"
            
            table_message = f"Available tables: {', '.join(tables)}"
            state["messages"].append(SystemMessage(content=table_message))
            
            return state
        except Exception as e:
            state["messages"].append(SystemMessage(content=f"Error fetching tables: {str(e)}"))
            return state
    
    def _decide_relevance_node(self, state: EnhancedAgentState) -> EnhancedAgentState:
        """Decide which tables are relevant to the question."""
        try:
            question = state["question"]
            tables = self.db_manager.list_tables()
            
            relevance_prompt = f"""
            Given the question: "{question}"
            And these available tables: {', '.join(tables)}
            
            Based on the question and the database schema, 
            which tables are most relevant? Return only the table names, comma-separated.
            
            Schema context: {get_chinook_schema_description()}
            """
            
            response = self.llm.invoke([HumanMessage(content=relevance_prompt)])
            relevant_tables_str = response.content.strip()
            
            relevant_tables = [t.strip() for t in relevant_tables_str.split(",") if t.strip() in tables]
            
            if not relevant_tables:
                relevant_tables = ["Artist", "Album", "Track", "Customer", "Invoice"]
            
            state["relevant_tables"] = relevant_tables
            state["current_step"] = "relevance_decided"
            
            message = f"Relevant tables identified: {', '.join(relevant_tables)}"
            state["messages"].append(SystemMessage(content=message))
            
            return state
        except Exception as e:
            state["relevant_tables"] = ["Artist", "Album", "Track", "Customer", "Invoice"]
            state["messages"].append(SystemMessage(content=f"Error deciding relevance: {str(e)}"))
            return state
    
    def _get_schemas_node(self, state: EnhancedAgentState) -> EnhancedAgentState:
        """Get detailed schema information for relevant tables."""
        try:
            relevant_tables = state["relevant_tables"]
            schema_info = self.db_manager.get_table_info(relevant_tables)
            
            state["schema_info"] = schema_info
            state["current_step"] = "schemas_retrieved"
            
            message = f"Schema information retrieved for tables: {', '.join(relevant_tables)}"
            state["messages"].append(SystemMessage(content=message))
            
            return state
        except Exception as e:
            state["messages"].append(SystemMessage(content=f"Error getting schemas: {str(e)}"))
            return state
    
    def _generate_query_node(self, state: EnhancedAgentState) -> EnhancedAgentState:
        """Generate SQL query based on the question and schema."""
        try:
            question = state["question"]
            schema_info = state.get("schema_info", "")
            relevant_tables = state.get("relevant_tables", [])
            
            query_prompt = f"""
            Generate a SQL query to answer this question: "{question}"
            
            Use ONLY these tables and their schemas:
            {schema_info}
            
            Relevant tables: {', '.join(relevant_tables)}
            
            Important guidelines:
            - Use only SQLite-compatible syntax
            - Be precise with column names and table joins
            - Use appropriate aggregations and sorting
            - Limit results if appropriate (use LIMIT 100 max for visualization)
            - Return ONLY the SQL query, no explanation
            """
            
            response = self.llm.invoke([HumanMessage(content=query_prompt)])
            sql_query = response.content.strip()
            
            # Clean up the query
            if sql_query.startswith("```"):
                sql_query = sql_query.split("\n", 1)[1]
            if sql_query.endswith("```"):
                sql_query = sql_query.rsplit("\n", 1)[0]
            
            state["sql_query"] = sql_query
            state["current_step"] = "query_generated"
            
            message = f"SQL query generated: {sql_query}"
            state["messages"].append(SystemMessage(content=message))
            
            return state
        except Exception as e:
            state["messages"].append(SystemMessage(content=f"Error generating query: {str(e)}"))
            return state
    
    def _validate_query_node(self, state: EnhancedAgentState) -> EnhancedAgentState:
        """Validate the generated SQL query."""
        try:
            sql_query = state["sql_query"]
            validation = self.db_manager.validate_query(sql_query)
            
            state["query_valid"] = validation["valid"]
            state["current_step"] = "query_validated"
            
            if validation["valid"]:
                message = "SQL query validation: PASSED"
            else:
                message = f"SQL query validation: FAILED - {validation['message']}"
            
            state["messages"].append(SystemMessage(content=message))
            
            return state
        except Exception as e:
            state["query_valid"] = False
            state["messages"].append(SystemMessage(content=f"Error validating query: {str(e)}"))
            return state
    
    def _execute_query_node(self, state: EnhancedAgentState) -> EnhancedAgentState:
        """Execute the validated SQL query and get results."""
        try:
            sql_query = state["sql_query"]
            
            # Use direct database manager execution instead of toolkit
            raw_data = self.db_manager.execute_query(sql_query)
            
            # Convert to string for display
            if not raw_data.empty:
                query_results = raw_data.to_string(index=False)
                # Store as dict for serialization with numpy type conversion
                data_dict = raw_data.to_dict('records')
                data_dict = convert_numpy_types(data_dict)
                
                state["raw_data"] = {
                    "data": data_dict,
                    "columns": raw_data.columns.tolist(),
                    "shape": convert_numpy_types(raw_data.shape)
                }
            else:
                query_results = "No results found."
                state["raw_data"] = None
            
            state["query_results"] = query_results
            state["current_step"] = "query_executed"
            
            message = f"Query executed successfully. Found {len(raw_data) if raw_data is not None else 0} rows."
            state["messages"].append(SystemMessage(content=message))
            
            return state
            
        except Exception as e:
            error_message = f"Error executing query: {str(e)}"
            state["query_results"] = f"Error: {error_message}"
            state["error_count"] = state.get("error_count", 0) + 1
            state["current_step"] = "query_failed"
            
            state["messages"].append(SystemMessage(content=error_message))
            
            return state
    
    def _fix_errors_node(self, state: EnhancedAgentState) -> EnhancedAgentState:
        """Attempt to fix errors in the SQL query."""
        try:
            question = state["question"]
            sql_query = state["sql_query"]
            error_msg = state["query_results"] if "Error:" in state.get("query_results", "") else "Validation failed"
            schema_info = state.get("schema_info", "")
            
            # INCREMENT ERROR COUNT - CRITICAL FIX!
            error_count = state.get("error_count", 0) + 1
            state["error_count"] = error_count
            
            fix_prompt = f"""
            The following SQL query has an error:
            Query: {sql_query}
            Error: {error_msg}
            
            Question: {question}
            Schema: {schema_info}
            
            Please provide a corrected SQL query that fixes the error.
            Return ONLY the corrected SQL query, no explanation.
            """
            
            response = self.llm.invoke([HumanMessage(content=fix_prompt)])
            corrected_query = response.content.strip()
            
            if corrected_query.startswith("```"):
                corrected_query = corrected_query.split("\n", 1)[1]
            if corrected_query.endswith("```"):
                corrected_query = corrected_query.rsplit("\n", 1)[0]
            
            state["sql_query"] = corrected_query
            state["current_step"] = "error_fixed"
            
            message = f"Attempted to fix query (attempt {error_count}): {corrected_query}"
            state["messages"].append(SystemMessage(content=message))
            
            return state
        except Exception as e:
            # Still increment error count on exception
            error_count = state.get("error_count", 0) + 1
            state["error_count"] = error_count
            state["messages"].append(SystemMessage(content=f"Error fixing query (attempt {error_count}): {str(e)}"))
            return state
    
    # New visualization nodes
    def _analyze_data_node(self, state: EnhancedAgentState) -> EnhancedAgentState:
        """Analyze the query results for visualization opportunities."""
        try:
            raw_data_dict = state.get("raw_data")
            
            if raw_data_dict is None:
                state["data_analysis"] = {"error": "No data to analyze"}
                return state
            
            # Convert back to DataFrame for analysis
            raw_data = pd.DataFrame(raw_data_dict["data"])
            
            if raw_data.empty:
                state["data_analysis"] = {"error": "No data to analyze"}
                return state
            
            # Perform data analysis
            analysis = self.chart_detector.analyze_data(raw_data)
            state["data_analysis"] = analysis
            state["current_step"] = "data_analyzed"
            
            message = f"Data analysis complete: {len(raw_data)} rows, {len(raw_data.columns)} columns"
            state["messages"].append(SystemMessage(content=message))
            
            return state
        except Exception as e:
            state["data_analysis"] = {"error": str(e)}
            state["messages"].append(SystemMessage(content=f"Error analyzing data: {str(e)}"))
            return state
    
    def _detect_chart_types_node(self, state: EnhancedAgentState) -> EnhancedAgentState:
        """Detect and suggest appropriate chart types."""
        try:
            raw_data_dict = state.get("raw_data")
            analysis = state.get("data_analysis", {})
            
            if raw_data_dict is None or "error" in analysis:
                state["suggested_charts"] = []
                return state
            
            # Convert back to DataFrame
            raw_data = pd.DataFrame(raw_data_dict["data"])
            
            if raw_data.empty:
                state["suggested_charts"] = []
                return state
            
            # Get chart suggestions
            suggestions = self.chart_detector.suggest_chart_types(raw_data, analysis)
            
            # Check for business template match
            template_match = self.templates.match_template(raw_data, analysis)
            if template_match:
                template_info = self.templates.get_templates()[template_match]
                suggestions.insert(0, {
                    "type": "business_template",
                    "template_id": template_match,
                    "title": template_info["name"],
                    "description": template_info["description"],
                    "priority": 10
                })
            
            state["suggested_charts"] = suggestions
            state["current_step"] = "chart_types_detected"
            
            chart_types = [s["type"] for s in suggestions[:3]]
            message = f"Chart suggestions: {', '.join(chart_types)}"
            state["messages"].append(SystemMessage(content=message))
            
            return state
        except Exception as e:
            state["suggested_charts"] = []
            state["messages"].append(SystemMessage(content=f"Error detecting chart types: {str(e)}"))
            return state
    
    def _generate_visualizations_node(self, state: EnhancedAgentState) -> EnhancedAgentState:
        """Generate the actual visualizations."""
        try:
            raw_data_dict = state.get("raw_data")
            suggestions = state.get("suggested_charts", [])
            
            if raw_data_dict is None or not suggestions:
                state["generated_charts"] = []
                return state
            
            # Convert back to DataFrame
            raw_data = pd.DataFrame(raw_data_dict["data"])
            
            if raw_data.empty:
                state["generated_charts"] = []
                return state
            
            generated_charts = []
            
            # Generate top 3 charts
            for suggestion in suggestions[:3]:
                if suggestion["type"] == "business_template":
                    continue  # Skip template entries for now
                
                try:
                    fig = self.viz_generator.create_chart(raw_data, suggestion)
                    
                    chart_data = {
                        "config": suggestion,
                        "figure": fig,
                        "html": fig.to_html(include_plotlyjs='cdn'),
                        "json": fig.to_json()
                    }
                    generated_charts.append(chart_data)
                    
                except Exception as chart_error:
                    state["messages"].append(SystemMessage(content=f"Error creating {suggestion['type']} chart: {str(chart_error)}"))
                    continue
            
            state["generated_charts"] = generated_charts
            state["current_step"] = "visualizations_generated"
            
            message = f"Generated {len(generated_charts)} visualizations"
            state["messages"].append(SystemMessage(content=message))
            
            return state
        except Exception as e:
            state["generated_charts"] = []
            state["messages"].append(SystemMessage(content=f"Error generating visualizations: {str(e)}"))
            return state
    
    def _create_dashboard_node(self, state: EnhancedAgentState) -> EnhancedAgentState:
        """Create dashboard layout and export options."""
        try:
            generated_charts = state.get("generated_charts", [])
            
            if not generated_charts:
                state["dashboard_layout"] = None
                state["export_options"] = ["csv", "json"]
                return state
            
            # Create dashboard layout
            dashboard_layout = {
                "title": f"Analysis Dashboard - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                "charts": [],
                "layout": "grid",
                "columns": 2 if len(generated_charts) > 1 else 1
            }
            
            for i, chart in enumerate(generated_charts):
                dashboard_layout["charts"].append({
                    "id": f"chart_{i}",
                    "title": chart["config"]["title"],
                    "type": chart["config"]["type"],
                    "description": chart["config"]["description"],
                    "position": {"row": i // 2, "col": i % 2}
                })
            
            state["dashboard_layout"] = dashboard_layout
            state["export_options"] = ["html", "png", "svg", "json", "csv", "excel"]
            state["current_step"] = "dashboard_created"
            
            message = f"Dashboard created with {len(generated_charts)} charts"
            state["messages"].append(SystemMessage(content=message))
            
            return state
        except Exception as e:
            state["dashboard_layout"] = None
            state["export_options"] = ["csv", "json"]
            state["messages"].append(SystemMessage(content=f"Error creating dashboard: {str(e)}"))
            return state
    
    def _generate_insights_node(self, state: EnhancedAgentState) -> EnhancedAgentState:
        """Generate insights about the data and visualizations."""
        try:
            raw_data_dict = state.get("raw_data")
            analysis = state.get("data_analysis", {})
            generated_charts = state.get("generated_charts", [])
            
            insights = []
            
            if raw_data_dict is not None:
                # Convert back to DataFrame
                raw_data = pd.DataFrame(raw_data_dict["data"])
                
                if not raw_data.empty:
                    # Data insights
                    insights.append(f"Dataset contains {len(raw_data)} records across {len(raw_data.columns)} columns")
                
                    # Numeric insights
                    numeric_cols = analysis.get("numeric_columns", [])
                    if numeric_cols:
                        for col in numeric_cols[:2]:  # Top 2 numeric columns
                            mean_val = raw_data[col].mean()
                            max_val = raw_data[col].max()
                            min_val = raw_data[col].min()
                            insights.append(f"{col}: Average {mean_val:.2f}, Range {min_val:.2f} to {max_val:.2f}")
                    
                    # Categorical insights
                    categorical_cols = analysis.get("categorical_columns", [])
                    if categorical_cols:
                        for col in categorical_cols[:2]:  # Top 2 categorical columns
                            unique_count = raw_data[col].nunique()
                            top_value = raw_data[col].mode().iloc[0] if not raw_data[col].mode().empty else "N/A"
                            insights.append(f"{col}: {unique_count} unique values, most common: {top_value}")
                    
                    # Visualization insights
                    if generated_charts:
                        chart_types = [chart["config"]["type"] for chart in generated_charts]
                        insights.append(f"Created {len(generated_charts)} visualizations: {', '.join(chart_types)}")
                        
                        # Suggest best chart
                        if generated_charts:
                            best_chart = generated_charts[0]["config"]
                            insights.append(f"Recommended visualization: {best_chart['type']} - {best_chart['description']}")
            
            state["visualization_insights"] = insights
            state["current_step"] = "insights_generated"
            
            message = f"Generated {len(insights)} data insights"
            state["messages"].append(SystemMessage(content=message))
            
            return state
        except Exception as e:
            state["visualization_insights"] = []
            state["messages"].append(SystemMessage(content=f"Error generating insights: {str(e)}"))
            return state
    
    def _finalize_response_node(self, state: EnhancedAgentState) -> EnhancedAgentState:
        """Generate the final comprehensive response with visualizations."""
        try:
            question = state["question"]
            query_results = state.get("query_results", "")
            insights = state.get("visualization_insights", [])
            generated_charts = state.get("generated_charts", [])
            
            # Create comprehensive response
            response_parts = []
            
            # Basic answer
            if "Error:" not in query_results:
                response_parts.append(f"Here's the answer to your question: '{question}'")
                response_parts.append(query_results)
            else:
                response_parts.append(f"I encountered an issue processing your question: {query_results}")
            
            # Add insights
            if insights:
                response_parts.append("\n📊 **Data Insights:**")
                for insight in insights:
                    response_parts.append(f"• {insight}")
            
            # Add visualization info
            if generated_charts:
                response_parts.append(f"\n📈 **Visualizations:** {len(generated_charts)} charts have been generated to help you understand the data better.")
                for i, chart in enumerate(generated_charts):
                    config = chart["config"]
                    response_parts.append(f"{i+1}. {config['title']}: {config['description']}")
            
            final_answer = "\n".join(response_parts)
            
            state["final_answer"] = final_answer
            state["current_step"] = "completed"
            
            state["messages"].append(AIMessage(content=final_answer))
            
            return state
        except Exception as e:
            error_response = f"I apologize, but I encountered an error while processing your question: {str(e)}"
            state["final_answer"] = error_response
            state["messages"].append(AIMessage(content=error_response))
            return state
    
    # Condition functions (same as original)
    def _validate_query_condition(self, state: EnhancedAgentState) -> Literal["execute", "fix"]:
        return "execute" if state.get("query_valid", False) else "fix"
    
    def _execute_query_condition(self, state: EnhancedAgentState) -> Literal["success", "error"]:
        query_results = state.get("query_results", "")
        return "error" if query_results.startswith("Error:") else "success"
    
    def _fix_errors_condition(self, state: EnhancedAgentState) -> Literal["retry", "give_up"]:
        error_count = state.get("error_count", 0)
        max_errors = state.get("max_errors", 3)
        return "give_up" if error_count >= max_errors else "retry"
    
    def query(self, question: str, max_errors: int = 3) -> Dict[str, Any]:
        """Process a text-to-SQL query with advanced visualization capabilities."""
        
        # Initialize enhanced state
        initial_state = {
            "messages": [HumanMessage(content=question)],
            "question": question,
            "current_step": "starting",
            "tables_fetched": False,
            "relevant_tables": [],
            "schema_info": "",
            "sql_query": "",
            "query_valid": False,
            "query_results": "",
            "error_count": 0,
            "max_errors": max_errors,
            "final_answer": "",
            
            # Visualization fields
            "raw_data": None,
            "data_analysis": {},
            "suggested_charts": [],
            "selected_chart_type": None,
            "visualization_config": {},
            "generated_charts": [],
            "export_options": [],
            "dashboard_layout": None,
            "visualization_insights": []
        }
        
        config = {
            "configurable": {"thread_id": f"enhanced_sql_session_{datetime.now().timestamp()}"},
            "recursion_limit": 50  # Increase from default 25 to allow for complex workflows
        }
        
        try:
            # Run the enhanced workflow
            final_state = self.graph.invoke(initial_state, config)
            
            return {
                "question": question,
                "answer": final_state.get("final_answer", "No response generated"),
                "sql_query": final_state.get("sql_query", ""),
                "raw_data": final_state.get("raw_data"),
                "data_analysis": final_state.get("data_analysis", {}),
                "suggested_charts": final_state.get("suggested_charts", []),
                "generated_charts": final_state.get("generated_charts", []),
                "dashboard_layout": final_state.get("dashboard_layout"),
                "visualization_insights": final_state.get("visualization_insights", []),
                "export_options": final_state.get("export_options", []),
                "success": True,
                "approach": "Enhanced LangGraph Agent with Visualization"
            }
            
        except Exception as e:
            return {
                "question": question,
                "answer": f"I encountered an error while processing your question: {str(e)}",
                "success": False,
                "error": str(e),
                "approach": "Enhanced LangGraph Agent with Visualization"
            }

def create_enhanced_sql_agent(database_path: str = "chinook.db", model: str = "meta-llama/Llama-3-70b-chat-hf", api_key: str = None) -> EnhancedSQLAgent:
    """Create an enhanced SQL agent with visualization capabilities."""
    from config import TOGETHER_API_KEY
    
    # Use provided API key or fall back to config
    effective_api_key = api_key or TOGETHER_API_KEY
    
    return EnhancedSQLAgent(database_path, model, effective_api_key)

# Example usage
if __name__ == "__main__":
    # Create the enhanced agent
    agent = EnhancedSQLAgent()
    
    # Test with visualization-friendly queries
    test_questions = [
        "What are the top 10 selling artists by total sales?",
        "Show me the revenue by country",
        "What is the distribution of track lengths?",
        "How do album sales vary by genre?",
        "Show customer purchase patterns over time"
    ]
    
    print("Testing Enhanced SQL Agent with Visualizations...")
    print("=" * 60)
    
    for question in test_questions:
        print(f"\nQuestion: {question}")
        result = agent.query(question)
        
        if result["success"]:
            print(f"Answer: {result['answer']}")
            print(f"Charts generated: {len(result.get('generated_charts', []))}")
            if result.get('visualization_insights'):
                print("Insights:", "; ".join(result['visualization_insights'][:2]))
        else:
            print(f"Error: {result['error']}")
        
        print("-" * 40)