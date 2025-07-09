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
        self.model_name = "llama3"
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
                if any(m.startswith('llama3') for m in available_models):
                    for preferred in ['llama3:latest', 'llama3:8b', 'llama3']:
                        for m in available_models:
                            if m == preferred or m.startswith(preferred):
                                self.current_model = m
                                break
                        if self.current_model:
                            break
                    if not self.current_model and available_models:
                        self.current_model = available_models[0]
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
                    # Optionally, you can also return df for charting if needed
            return {
                "query": user_query,
                "context": context,
                "response": enhanced_text,
                "status": "success",
                "model_used": self.current_model or 'Unknown',
                "table_data": table_data,
                "visualization_code": viz_code,
                "intent": intent
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
                        if any(m.startswith('llama3') for m in available_models):
                            for preferred in ['llama3:latest', 'llama3:8b', 'llama3']:
                                for m in available_models:
                                    if m == preferred or m.startswith(preferred):
                                        self.current_model = m
                                        break
                                if self.current_model:
                                    break
                        if not self.current_model and available_models:
                            self.current_model = available_models[0]
                except:
                    self.current_model = "llama3"
            
            # Direct Ollama API call
            ollama_url = "http://localhost:11434/api/generate"
            payload = {
                "model": self.current_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 1500
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
                
                # Check available models and select the best one
                models_response = requests.get(health_url, timeout=5)
                if models_response.status_code == 200:
                    models_data = models_response.json()
                    available_models = [model.get('name', '') for model in models_data.get('models', [])]
                    model_name = None
                    if any(m.startswith('llama3') for m in available_models):
                        # Prefer llama3:latest or llama3:8b if available
                        for preferred in ['llama3:latest', 'llama3:8b', 'llama3']:
                            for m in available_models:
                                if m == preferred or m.startswith(preferred):
                                    model_name = m
                                    break
                            if model_name:
                                break
                        print(f"✅ Using model: {model_name}")
                    elif available_models:
                        model_name = available_models[0]
                        print(f"⚠️ llama3 not found, using {model_name}")
                    else:
                        response_text = "Error: No models available in Ollama. Please pull a model first."
                        return {
                            "query": user_query,
                            "context": context,
                            "response": response_text,
                            "status": "error",
                            "model_used": self.current_model or 'Unknown'
                        }
                else:
                    response_text = "Error: Could not retrieve models from Ollama."
                    return {
                        "query": user_query,
                        "context": context,
                        "response": response_text,
                        "status": "error",
                        "model_used": self.current_model or 'Unknown'
                    }
                
                # Direct Ollama API call with better timeout handling
                ollama_url = "http://localhost:11434/api/generate"
                payload = {
                    "model": model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 1000
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