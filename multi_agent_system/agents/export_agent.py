"""
Export Agent - Handles data export in various formats
"""
import logging
from typing import Dict, List, Any, Optional
import pandas as pd
import json
import io
import base64
from datetime import datetime

logger = logging.getLogger(__name__)

class ExportAgent:
    """Handles data export in multiple formats"""
    
    def __init__(self):
        self.supported_formats = ['csv', 'json', 'excel', 'html']
    
    def export_data(self, data: pd.DataFrame, format: str = 'csv', 
                   filename: str = None, max_rows: int = None, 
                   current_page_only: bool = False, page_data: pd.DataFrame = None) -> Dict[str, Any]:
        """Export data in specified format with pagination support"""
        try:
            # Determine what data to export
            if current_page_only and page_data is not None:
                export_data = page_data
                export_type = "current_page"
            elif max_rows and len(data) > max_rows:
                export_data = data.head(max_rows)
                export_type = "limited"
            else:
                export_data = data
                export_type = "full"
            
            if export_data.empty:
                return {"success": False, "error": "No data to export"}
            
            format = format.lower()
            if format not in self.supported_formats:
                return {"success": False, "error": f"Unsupported format: {format}"}
            
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                suffix = ""
                if export_type == "current_page":
                    suffix = "_page"
                elif export_type == "limited":
                    suffix = f"_first{max_rows}"
                filename = f"export_{timestamp}{suffix}.{format}"
            
            # Export based on format
            if format == 'csv':
                buffer = io.StringIO()
                export_data.to_csv(buffer, index=False)
                content = buffer.getvalue()
                content_type = "text/csv"
            elif format == 'json':
                json_data = {
                    "timestamp": datetime.now().isoformat(),
                    "export_type": export_type,
                    "total_records": len(data),
                    "exported_records": len(export_data),
                    "data": export_data.to_dict(orient='records')
                }
                content = json.dumps(json_data, indent=2, default=str)
                content_type = "application/json"
            elif format == 'html':
                html_header = f"""
                <h2>Data Export</h2>
                <p><strong>Export Type:</strong> {export_type}</p>
                <p><strong>Total Records:</strong> {len(data)}</p>
                <p><strong>Exported Records:</strong> {len(export_data)}</p>
                <p><strong>Export Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <hr>
                """
                content = html_header + export_data.to_html()
                content_type = "text/html"
            else:
                return {"success": False, "error": f"Format {format} not implemented"}
            
            return {
                "success": True,
                "format": format,
                "filename": filename,
                "content": content,
                "content_type": content_type,
                "export_type": export_type,
                "total_rows": len(data),
                "exported_rows": len(export_data)
            }
            
        except Exception as e:
            logger.error(f"Error exporting data: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def export_charts(self, charts: List[Dict[str, Any]], format: str = 'png') -> Dict[str, Any]:
        """Export charts in specified format"""
        try:
            if not charts:
                return {"success": False, "error": "No charts to export"}
            
            exported_charts = []
            
            for i, chart in enumerate(charts):
                if "figure" not in chart:
                    continue
                
                fig = chart["figure"]
                chart_filename = f"chart_{i+1}.{format}"
                
                if format.lower() == 'png':
                    img_bytes = fig.to_image(format="png")
                    content = base64.b64encode(img_bytes).decode()
                    content_type = "image/png"
                elif format.lower() == 'html':
                    content = fig.to_html()
                    content_type = "text/html"
                else:
                    continue
                
                exported_charts.append({
                    "filename": chart_filename,
                    "title": chart.get("title", f"Chart {i+1}"),
                    "content": content,
                    "content_type": content_type
                })
            
            return {
                "success": True,
                "format": format,
                "chart_count": len(exported_charts),
                "charts": exported_charts
            }
            
        except Exception as e:
            logger.error(f"Error exporting charts: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def create_dashboard_export(self, data: pd.DataFrame, charts: List[Dict[str, Any]], 
                               metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a comprehensive dashboard export"""
        try:
            dashboard_html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Dashboard Export</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                             color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
                    .metadata {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                    .chart-container {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                    .data-section {{ margin-top: 30px; }}
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                </style>
                <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            </head>
            <body>
                <div class="header">
                    <h1>📊 Dashboard Export</h1>
                    <p>Generated: {timestamp}</p>
                </div>
                
                {metadata_section}
                
                <div class="charts-section">
                    <h2>📈 Visualizations</h2>
                    {charts_html}
                </div>
                
                <div class="data-section">
                    <h2>📋 Data ({record_count} records)</h2>
                    {data_table}
                </div>
            </body>
            </html>
            """
            
            # Generate metadata section
            metadata_section = ""
            if metadata:
                metadata_section = "<div class='metadata'><h3>📋 Metadata</h3>"
                for key, value in metadata.items():
                    metadata_section += f"<p><strong>{key}:</strong> {value}</p>"
                metadata_section += "</div>"
            
            # Generate charts HTML
            charts_html = ""
            for i, chart in enumerate(charts):
                if "figure" in chart:
                    chart_div = f"chart-{i}"
                    chart_json = chart["figure"].to_json()
                    charts_html += f"""
                    <div class="chart-container">
                        <h3>{chart.get('title', f'Chart {i+1}')}</h3>
                        <div id="{chart_div}"></div>
                        <script>
                            Plotly.newPlot('{chart_div}', {chart_json});
                        </script>
                    </div>
                    """
            
            # Generate data table
            data_table = data.head(100).to_html(classes='data-table') if len(data) > 100 else data.to_html(classes='data-table')
            if len(data) > 100:
                data_table += f"<p><em>Showing first 100 of {len(data)} records</em></p>"
            
            dashboard_content = dashboard_html.format(
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                metadata_section=metadata_section,
                charts_html=charts_html,
                record_count=len(data),
                data_table=data_table
            )
            
            return {
                "success": True,
                "content": dashboard_content,
                "content_type": "text/html",
                "filename": f"dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            }
            
        except Exception as e:
            logger.error(f"Error creating dashboard export: {str(e)}")
            return {"success": False, "error": str(e)} 