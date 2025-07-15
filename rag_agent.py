#!/usr/bin/env python3
"""
Enhanced RAG Agent POC using Llama 3 + Direct Ollama API + ChromaDB
with intelligent table and visualization generation
"""

import chromadb
from chroma_module.multitenant_chroma import get_tenant_collection
from utils.embedding_generator import generate_embedding
import json
import numpy as np
import re
import pandas as pd

class RAGAgent:
    def __init__(self, tenant_id="tenant_ABC"):
        self.tenant_id = tenant_id
        self.setup_agent()
        
    def setup_agent(self):
        """Set up the RAG agent configuration"""
        # We'll use direct Ollama API calls instead of AutoGen to avoid compatibility issues
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model_name = "llama3:8b"  # Use Llama 3 8B for best performance
        self.current_model = None
        
        # Test connection to Ollama
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                print("✅ Ollama connection successful")
                # Get the actual model name being used
                models_data = response.json()
                available_models = [model.get('name', '') for model in models_data.get('models', [])]
                
                # Try to find a model that works with available memory
                # Priority: best performance models first, with fallbacks
                preferred_models = [
                    'llama3:8b',  # Best performance model (4.7GB)
                    'llama3:latest',  # Latest Llama 3 version
                    'llama2:7b',  # Llama 2 7B version
                    'llama2:7b-chat-q4_0',  # Quantized version
                    'phi3:mini',  # Small working model (2.2GB)
                    'tinyllama:1.1b',  # Compact model (637MB)
                    'smollm2:135m',  # Very small model (270MB)
                    'smollm2:135m-instruct-q4_K_S',  # Smallest quantized model (102MB)
                ]
                
                for preferred in preferred_models:
                    for m in available_models:
                        if m == preferred or m.startswith(preferred):
                            self.current_model = m
                            print(f"✅ Selected model: {self.current_model}")
                            break
                    if self.current_model:
                        break
                
                if not self.current_model and available_models:
                    self.current_model = available_models[0]
                    print(f"⚠️ Using fallback model: {self.current_model}")
            else:
                print("⚠️ Ollama connection test failed")
        except Exception as e:
            print(f"⚠️ Ollama connection test failed: {e}")
        
    def retrieve_context(self, query, top_k=5):
        """Retrieve relevant context from ChromaDB using semantic search"""
        try:
            # Generate embedding for the query
            query_embedding = generate_embedding(query)
            
            # Convert to list if it's a numpy array
            if isinstance(query_embedding, np.ndarray):
                query_embedding = query_embedding.tolist()
            
            # Get tenant collection
            collection = get_tenant_collection(self.tenant_id)
            
            # Search for similar documents
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            # Extract documents and metadata
            documents = results.get('documents', [[]])[0]
            metadatas = results.get('metadatas', [[]])[0]
            
            # Format context
            context = []
            for i, doc in enumerate(documents):
                metadata = metadatas[i] if i < len(metadatas) else {}
                context.append(f"Document {i+1}: {doc}")
                if metadata:
                    context.append(f"Metadata: {metadata}")
            
            return "\n\n".join(context) if context else "No relevant context found."
            
        except Exception as e:
            print(f"Error in retrieval: {e}")
            return "Error retrieving context."
    
    def analyze_query_intent(self, query):
        """Analyze if the query explicitly requests tables or visualizations"""
        query_lower = query.lower()
        
        # Keywords that indicate table requests
        table_keywords = [
            'table', 'tabular', 'list', 'show me', 'display', 'format as table',
            'in a table', 'as a table', 'table format', 'structured data'
        ]
        
        # Keywords that indicate visualization requests
        viz_keywords = [
            'chart', 'graph', 'plot', 'visualize', 'visualization', 'bar chart',
            'line chart', 'pie chart', 'histogram', 'scatter plot', 'trend',
            'compare', 'analysis', 'statistics', 'summary'
        ]
        
        # Check for explicit requests
        needs_table = any(keyword in query_lower for keyword in table_keywords)
        needs_visualization = any(keyword in query_lower for keyword in viz_keywords)
        
        return {
            'needs_table': needs_table,
            'needs_visualization': needs_visualization,
            'is_analytical': needs_table or needs_visualization
        }
    
    def generate_enhanced_response(self, user_query, history=None, history_turns=3):
        """Generate an enhanced response with intelligent table/visualization generation"""
        try:
            # Step 1: Analyze query intent
            intent = self.analyze_query_intent(user_query)
            
            # Step 2: Retrieve relevant context
            print(f"🔍 Retrieving context for query: {user_query}")
            context = self.retrieve_context(user_query)
            print(f"📄 Retrieved context: {context[:200]}...")
            
            # Step 3: Generate initial response
            initial_response = self.generate_response(user_query, history, history_turns)
            
            if initial_response['status'] != 'success':
                return initial_response
            
            # Step 4: If query is analytical or explicitly requests data, enhance with table/visualization
            if intent['is_analytical'] or intent['needs_table'] or intent['needs_visualization']:
                enhanced_response = self.enhance_with_data_analysis(
                    user_query, 
                    initial_response['response'], 
                    context,
                    intent
                )
                return enhanced_response
            
            # Step 5: Add model information to response
            initial_response['model_used'] = self.current_model or 'Unknown'
            return initial_response
            
        except Exception as e:
            print(f"Error in enhanced response generation: {e}")
            return {
                "query": user_query,
                "context": "",
                "response": f"Error: {str(e)}",
                "status": "error",
                "model_used": self.current_model or 'Unknown'
            }
    
    def enhance_with_data_analysis(self, user_query, initial_response, context, intent):
        """Enhance the response with table and visualization generation"""
        try:
            # Create a prompt for data analysis
            analysis_prompt = f"""You are an expert data analyst assistant. Your job is to always provide structured, visual, and actionable answers.

User Query: {user_query}
Initial Response: {initial_response}
Context: {context}

Requirements:
1. If the user query is about rankings, summaries, comparisons, or contains words like 'top', 'highest', 'summary', 'compare', 'list', 'distribution', 'breakdown', 'table', 'chart', 'visualize', ALWAYS output a markdown table summarizing the relevant data. The table should have clear headers and rows, and be formatted as GitHub-flavored markdown (| Col1 | Col2 | ... |). If possible, include all relevant columns (e.g., Order ID, Value, Status, etc.).
2. If the data is suitable for visualization (e.g., numeric columns, categories), ALWAYS output Python code (in a code block) for a simple chart (bar, pie, line, etc.) using plotly or matplotlib. The code should use a variable 'df' for the table data if possible.
3. If the user asks for a table or chart, always provide both if possible.
4. If the query is analytical, consider if tabular data and a chart would be helpful, and include them.
5. If you cannot generate a table or chart, explicitly say so in the output.

Respond in this format:
TEXT: [enhanced text response]
TABLE: [markdown table if needed, otherwise "NONE"]
VISUALIZATION: [python code if needed, otherwise "NONE"]
"""

            # Generate enhanced response
            enhanced_result = self.generate_response_with_prompt(analysis_prompt)
            if enhanced_result['status'] != 'success':
                return {
                    **initial_response,
                    'model_used': self.current_model or 'Unknown'
                }
            # Parse the enhanced response
            response_text = enhanced_result['response']
            import re
            text_match = re.search(r'TEXT:\s*(.*?)(?=TABLE:|VISUALIZATION:|$)', response_text, re.DOTALL)
            table_match = re.search(r'TABLE:\s*(.*?)(?=VISUALIZATION:|$)', response_text, re.DOTALL)
            viz_match = re.search(r'VISUALIZATION:\s*(.*?)(?=TEXT:|TABLE:|$)', response_text, re.DOTALL)
            enhanced_text = text_match.group(1).strip() if text_match else initial_response['response']
            table_data = table_match.group(1).strip() if table_match and 'NONE' not in table_match.group(1) else None
            viz_code = viz_match.group(1).strip() if viz_match and 'NONE' not in viz_match.group(1) else None

            # Fallback: If no table but intent is summary/top/highest, try to parse a list into a table
            if not table_data and isinstance(intent, dict) and any(
                intent.get(k, False) for k in ['needs_table', 'summary', 'top', 'highest', 'compare']
            ):
                import pandas as pd
                import re
                lines = [l.strip('-• ') for l in enhanced_text.split('\n') if l.strip().startswith(('1.', '2.', '3.', '4.', '5.', '-', '•'))]
                extracted = []
                for l in lines:
                    # Regex to extract: Document, Order Name, ID, Value, Units, Price per unit
                    m = re.match(r"(?:Document|\d+)[^:]*: ([^(]+) \(ID: (\d+)\) with a total value of ([\d.]+)[^\(]*\(([^u]+)units x ([\d.]+)[^)]*\)", l)
                    if m:
                        order_name = m.group(1).strip()
                        order_id = m.group(2).strip()
                        value = m.group(3).strip()
                        units = m.group(4).strip()
                        price = m.group(5).strip()
                        extracted.append({
                            'Order Name': order_name,
                            'Order ID': order_id,
                            'Value': value,
                            'Units': units,
                            'Price per unit': price
                        })
                    else:
                        # Fallback: just put the line as a single column
                        extracted.append({'Order Name': l})
                if extracted:
                    df = pd.DataFrame(extracted)
                    table_md = df.to_markdown(index=False)
                    table_data = table_md
                    # Store DataFrame for charting
                    table_df = df
            
            # Use AutoGen agent to get chart recommendation
            chart_recommendation = None
            chart_fig = None
            if 'table_df' in locals() and table_df is not None:
                chart_recommendation = self.get_chart_recommendation(table_df, user_query)
                if chart_recommendation and chart_recommendation.get("chart_type") != "none":
                    chart_fig = self.generate_chart(table_df, chart_recommendation)
                    if chart_fig:
                        enhanced_text += f"\n\n## Chart Recommendation\nChart Type: {chart_recommendation.get('chart_type', 'Unknown')}\nReasoning: {chart_recommendation.get('reasoning', 'No reasoning provided')}"
            
            return {
                "query": user_query,
                "context": context,
                "response": enhanced_text,
                "status": "success",
                "model_used": self.current_model or 'Unknown',
                "table_data": table_data,
                "visualization_code": viz_code,
                "intent": intent,
                "chart_recommendation": chart_recommendation,
                "chart_figure": chart_fig,
                "table_dataframe": table_df if 'table_df' in locals() else None
            }
        except Exception as e:
            print(f"Error in data analysis enhancement: {e}")
            return {
                **initial_response,
                'model_used': self.current_model or 'Unknown'
            }
    
    def generate_response_with_prompt(self, prompt):
        """Generate response with a specific prompt"""
        try:
            import requests
            
            # Use the current model
            if not self.current_model:
                # Try to get available models
                try:
                    response = requests.get("http://localhost:11434/api/tags", timeout=5)
                    if response.status_code == 200:
                        models_data = response.json()
                        available_models = [model.get('name', '') for model in models_data.get('models', [])]
                        # Try to find a model that works with available memory
                        preferred_models = [
                            'phi3:mini',  # Smallest working model
                            'smollm2:135m',  # Very small model
                            'smollm:135m',  # Another small model
                            'tinyllama:1.1b',  # Compact model
                            'llama2:7b-chat-q4_0',  # Quantized version
                            'llama2:7b',  # Regular version
                            'llama3:8b',  # Llama 3 version
                            'llama3:latest'
                        ]
                        
                        for preferred in preferred_models:
                            for m in available_models:
                                if m == preferred or m.startswith(preferred):
                                    self.current_model = m
                                    break
                            if self.current_model:
                                break
                        
                        if not self.current_model and available_models:
                            self.current_model = available_models[0]
                except:
                    self.current_model = "llama3:8b"
            
            # Direct Ollama API call with memory optimization
            ollama_url = "http://localhost:11434/api/generate"
            payload = {
                "model": self.current_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 1500,  # Increased for better responses
                    "num_ctx": 4096,      # Larger context window
                    "num_thread": 8       # More threads for better performance
                }
            }
            
            response = requests.post(ollama_url, json=payload, timeout=60)
            if response.status_code == 200:
                response_data = response.json()
                response_text = response_data.get('response', 'No response generated')
                if not response_text.strip():
                    response_text = "Error: Empty response from Ollama"
            else:
                response_text = f"Error: Ollama API returned status {response.status_code}"
                
            return {
                "response": response_text,
                "status": "success"
            }
                
        except Exception as e:
            print(f"Error in prompt generation: {e}")
            return {
                "response": f"Error: {str(e)}",
                "status": "error"
            }
    
    def generate_response(self, user_query, history=None, history_turns=3):
        """Generate a response using RAG approach"""
        try:
            # Step 1: Retrieve relevant context
            print(f"🔍 Retrieving context for query: {user_query}")
            context = self.retrieve_context(user_query)
            print(f"📄 Retrieved context: {context[:200]}...")
            
            # Step 2: Construct prompt with context and history
            prompt = f"""User Query: {user_query}

Context from database:
{context}

Please answer the user's question based on the context provided above. Be specific and provide relevant details from the order data. If the context doesn't contain enough information to answer the question, please say so.

Answer:"""
            
            # Step 3: Generate response using Llama 3 via direct Ollama API call
            print("🤖 Generating response with Llama 3...")
            try:
                import requests
                import time
                
                # First, check if Ollama is healthy
                health_url = "http://localhost:11434/api/tags"
                try:
                    health_response = requests.get(health_url, timeout=5)
                    if health_response.status_code != 200:
                        response_text = "Error: Ollama is not responding properly"
                        return {
                            "query": user_query,
                            "context": context,
                            "response": response_text,
                            "status": "error",
                            "model_used": self.current_model or 'Unknown'
                        }
                except Exception as e:
                    response_text = f"Error: Cannot connect to Ollama - {str(e)}"
                    return {
                        "query": user_query,
                        "context": context,
                        "response": response_text,
                        "status": "error",
                        "model_used": self.current_model or 'Unknown'
                    }
                
                # Use the current model from setup_agent
                model_name = self.current_model
                if not model_name:
                    # Fallback: check available models and select the best one
                    models_response = requests.get(health_url, timeout=5)
                    if models_response.status_code == 200:
                        models_data = models_response.json()
                        available_models = [model.get('name', '') for model in models_data.get('models', [])]
                        
                        # Try to find a model that works with available memory
                        preferred_models = [
                            'phi3:mini',  # Smallest working model
                            'smollm2:135m',  # Very small model
                            'smollm:135m',  # Another small model
                            'tinyllama:1.1b',  # Compact model
                            'llama2:7b-chat-q4_0',  # Quantized version
                            'llama2:7b',  # Regular version
                            'llama3:8b',  # Llama 3 version
                            'llama3:latest'
                        ]
                        
                        for preferred in preferred_models:
                            for m in available_models:
                                if m == preferred or m.startswith(preferred):
                                    model_name = m
                                    break
                            if model_name:
                                break
                        
                        if not model_name and available_models:
                            model_name = available_models[0]
                            print(f"⚠️ Using fallback model: {model_name}")
                    else:
                        response_text = "Error: Could not retrieve models from Ollama."
                        return {
                            "query": user_query,
                            "context": context,
                            "response": response_text,
                            "status": "error",
                            "model_used": self.current_model or 'Unknown'
                        }
                
                if not model_name:
                    response_text = "Error: No models available in Ollama. Please pull a model first."
                    return {
                        "query": user_query,
                        "context": context,
                        "response": response_text,
                        "status": "error",
                        "model_used": self.current_model or 'Unknown'
                    }
                
                # Direct Ollama API call with memory optimization
                ollama_url = "http://localhost:11434/api/generate"
                payload = {
                    "model": model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 1500,  # Increased for better responses
                        "num_ctx": 4096,      # Larger context window
                        "num_thread": 8       # More threads for better performance
                    }
                }
                print(f"🔗 Sending request to Ollama with model: {model_name}")
                response = requests.post(ollama_url, json=payload, timeout=60)
                if response.status_code == 200:
                    response_data = response.json()
                    response_text = response_data.get('response', 'No response generated')
                    if not response_text.strip():
                        response_text = "Error: Empty response from Ollama"
                else:
                    response_text = f"Error: Ollama API returned status {response.status_code}"
                    
            except requests.exceptions.Timeout:
                response_text = "Error: Ollama request timed out. The model might be busy or taking too long to respond."
            except requests.exceptions.ConnectionError:
                response_text = "Error: Cannot connect to Ollama. Make sure it's running on localhost:11434"
            except Exception as e:
                print(f"Error in Ollama API call: {e}")
                response_text = f"Error generating response: {str(e)}"
            
            return {
                "query": user_query,
                "context": context,
                "response": response_text,
                "status": "success",
                "model_used": model_name or self.current_model or 'Unknown'
            }
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return {
                "query": user_query,
                "context": "",
                "response": f"Error: {str(e)}",
                "status": "error",
                "model_used": self.current_model or 'Unknown'
            }

    def create_chart_recommendation_agent(self):
        """Create an AutoGen agent for chart recommendation"""
        try:
            # Create the chart recommendation agent
            chart_agent = AssistantAgent(
                name="chart_recommender",
                system_message="""You are an expert data visualization specialist. Your job is to analyze data and user queries to recommend the most appropriate chart type and configuration.

Available chart types:
- bar: For comparing categories or showing rankings
- line: For trends over time or continuous data
- pie: For showing proportions/percentages
- scatter: For showing relationships between two variables
- histogram: For showing distribution of a single variable
- box: For showing statistical distribution
- heatmap: For correlation matrices or 2D data
- none: When no chart is appropriate

Always respond in this exact JSON format:
{
    "chart_type": "chart_type_name",
    "x_column": "column_name_for_x_axis",
    "y_column": "column_name_for_y_axis",
    "title": "Chart title",
    "reasoning": "Brief explanation of why this chart type was chosen"
}

If no chart is appropriate, set chart_type to "none" and leave other fields empty except reasoning.""",
                llm_config=self.llm_config
            )
            
            return chart_agent
        except Exception as e:
            print(f"Error creating chart recommendation agent: {e}")
            return None

    def get_chart_recommendation(self, df, user_query, table_data=None):
        """Get chart recommendation from AutoGen agent"""
        try:
            if df is None or df.empty:
                return {"chart_type": "none", "reasoning": "No data available for visualization"}
            
            chart_agent = self.create_chart_recommendation_agent()
            if not chart_agent:
                return {"chart_type": "none", "reasoning": "Could not create chart agent"}
            
            # Prepare the data summary for the agent
            data_summary = f"""
DataFrame Info:
- Shape: {df.shape}
- Columns: {list(df.columns)}
- Data types: {dict(df.dtypes)}
- Sample data (first 3 rows):
{df.head(3).to_string()}

User Query: {user_query}

Please recommend the best chart type for this data and query.
"""
            
            # Create a user proxy for the interaction
            user_proxy = UserProxyAgent(
                name="user_proxy",
                human_input_mode="NEVER",
                max_consecutive_auto_reply=1,
                llm_config=self.llm_config
            )
            
            # Start the conversation
            chat_result = user_proxy.initiate_chat(
                chart_agent,
                message=data_summary
            )
            
            # Extract the recommendation from the agent's response
            if chat_result and hasattr(chat_result, 'chat_history'):
                last_message = chat_result.chat_history[-1]
                if hasattr(last_message, 'content'):
                    response = last_message.content
                    
                    # Try to parse JSON from the response
                    import json
                    import re
                    
                    # Look for JSON in the response
                    json_match = re.search(r'\{.*\}', response, re.DOTALL)
                    if json_match:
                        try:
                            recommendation = json.loads(json_match.group())
                            return recommendation
                        except json.JSONDecodeError:
                            pass
                    
                    # Fallback: try to extract chart type from text
                    if "bar" in response.lower():
                        return {"chart_type": "bar", "reasoning": "Extracted from agent response"}
                    elif "line" in response.lower():
                        return {"chart_type": "line", "reasoning": "Extracted from agent response"}
                    elif "pie" in response.lower():
                        return {"chart_type": "pie", "reasoning": "Extracted from agent response"}
                    elif "scatter" in response.lower():
                        return {"chart_type": "scatter", "reasoning": "Extracted from agent response"}
                    else:
                        return {"chart_type": "none", "reasoning": "No clear chart recommendation found"}
            
            return {"chart_type": "none", "reasoning": "No response from chart agent"}
            
        except Exception as e:
            print(f"Error getting chart recommendation: {e}")
            return {"chart_type": "none", "reasoning": f"Error: {str(e)}"}

    def generate_chart(self, df, chart_recommendation):
        """Generate a chart based on the recommendation"""
        try:
            if not chart_recommendation or chart_recommendation.get("chart_type") == "none":
                return None
            
            chart_type = chart_recommendation.get("chart_type")
            x_column = chart_recommendation.get("x_column")
            y_column = chart_recommendation.get("y_column")
            title = chart_recommendation.get("title", "Data Visualization")
            
            import plotly.express as px
            import plotly.graph_objects as go
            
            # Validate columns exist
            if x_column and x_column not in df.columns:
                x_column = df.columns[0] if len(df.columns) > 0 else None
            if y_column and y_column not in df.columns:
                y_column = df.columns[1] if len(df.columns) > 1 else None
            
            # Generate chart based on type
            if chart_type == "bar":
                if x_column and y_column:
                    fig = px.bar(df, x=x_column, y=y_column, title=title)
                else:
                    # Use first two columns
                    fig = px.bar(df, x=df.columns[0], y=df.columns[1], title=title)
                    
            elif chart_type == "line":
                if x_column and y_column:
                    fig = px.line(df, x=x_column, y=y_column, title=title)
                else:
                    fig = px.line(df, x=df.columns[0], y=df.columns[1], title=title)
                    
            elif chart_type == "pie":
                if y_column:
                    fig = px.pie(df, values=y_column, names=x_column or df.columns[0], title=title)
                else:
                    fig = px.pie(df, values=df.columns[1], names=df.columns[0], title=title)
                    
            elif chart_type == "scatter":
                if x_column and y_column:
                    fig = px.scatter(df, x=x_column, y=y_column, title=title)
                else:
                    fig = px.scatter(df, x=df.columns[0], y=df.columns[1], title=title)
                    
            elif chart_type == "histogram":
                if x_column:
                    fig = px.histogram(df, x=x_column, title=title)
                else:
                    fig = px.histogram(df, x=df.columns[0], title=title)
                    
            elif chart_type == "box":
                if y_column:
                    fig = px.box(df, y=y_column, title=title)
                else:
                    fig = px.box(df, y=df.columns[1], title=title)
                    
            else:
                return None
            
            # Update layout for better appearance
            fig.update_layout(
                height=400,
                margin=dict(l=20, r=20, t=40, b=20),
                showlegend=True
            )
            
            return fig
            
        except Exception as e:
            print(f"Error generating chart: {e}")
            return None

def test_ollama_connection():
    """Test Ollama connectivity and model availability"""
    print("🔍 Testing Ollama Connection...")
    
    try:
        import requests
        
        # Test basic connectivity
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama is running and responding")
            
            # Check available models
            models_data = response.json()
            models = models_data.get('models', [])
            
            if models:
                print(f"📦 Available models ({len(models)}):")
                for model in models:
                    name = model.get('name', 'Unknown')
                    size = model.get('size', 0)
                    size_gb = size / (1024**3) if size > 0 else 0
                    print(f"  - {name} ({size_gb:.1f} GB)")
                
                # Check for llama3 models
                llama3_models = [m for m in models if m.get('name', '').startswith('llama3')]
                if llama3_models:
                    print("✅ Llama3 models are available")
                else:
                    print("⚠️ No Llama3 models found")
            else:
                print("⚠️ No models found. Please pull a model first.")
        else:
            print(f"❌ Ollama responded with status {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama. Make sure it's running on localhost:11434")
    except Exception as e:
        print(f"❌ Error testing Ollama: {e}")

def main():
    """Main function for testing"""
    print("🧪 Testing Enhanced RAG Agent...")
    
    # Test Ollama connection
    test_ollama_connection()
    
    # Test RAG agent
    try:
        agent = RAGAgent("tenant_ABC")
        print(f"✅ RAG Agent initialized with model: {agent.current_model}")
        
        # Test a simple query
        test_query = "What are the highest value orders?"
        print(f"\n🔍 Testing query: {test_query}")
        
        result = agent.generate_enhanced_response(test_query)
        print(f"📝 Response status: {result['status']}")
        print(f"🤖 Model used: {result.get('model_used', 'Unknown')}")
        print(f"📊 Has table data: {'Yes' if result.get('table_data') else 'No'}")
        print(f"📈 Has visualization: {'Yes' if result.get('visualization_code') else 'No'}")
        
    except Exception as e:
        print(f"❌ Error testing RAG agent: {e}")

if __name__ == "__main__":
    main() 