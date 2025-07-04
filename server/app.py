from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import uvicorn
import json
from typing import List, Dict, Any, Optional
import requests
import traceback  # 添加traceback模块
from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.core.settings import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb

app = FastAPI()

# 添加CORS中间件，允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应限制为实际域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 加载本地embedding模型
EMBEDDING_MODEL_PATH = r"C:\Users\Boredommm\.cache\modelscope\hub\models\sentence-transformers\paraphrase-multilingual-MiniLM-L12-v2"

# 定义全局变量，用于存储索引实例
riddle_index = None
chroma_client = None
riddle_collection = None

# 数据目录
DATA_DIR = "../data"
PERSIST_DIR = "./chroma_db"

# 定义聊天请求模型
class ChatRequest(BaseModel):
    model: str
    messages: List[Dict[str, str]]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 2048

# 尝试从环境变量或配置文件中读取API Key
def get_api_key():
    # 首先尝试从环境变量获取
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    
    # 如果环境变量中没有，尝试从config.json读取
    if not api_key:
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    api_key = config.get("DEEPSEEK_API_KEY")
                    if api_key:
                        print("成功从config.json读取API密钥")
            except Exception as e:
                print(f"读取配置文件出错: {e}")
    
    # 如果还是没有，使用默认值
    if not api_key:
        api_key = "sk-cf33434e04a24ceb99c20e9d99c846ff"  # 使用与前端相同的默认API密钥
        print("警告: 使用默认API密钥，建议替换为您自己的密钥")
        print("您可以通过创建config.json文件或设置DEEPSEEK_API_KEY环境变量来配置自己的API密钥")
    
    return api_key

# 初始化函数，用于加载或创建向量索引
def init_index():
    global riddle_index, chroma_client, riddle_collection
    
    # 创建embedding模型
    embed_model = HuggingFaceEmbedding(model_name=EMBEDDING_MODEL_PATH)
    
    # 初始化Chroma客户端
    chroma_client = chromadb.PersistentClient(path=PERSIST_DIR)
    
    # 设置全局Settings
    Settings.embed_model = embed_model
    # 注意：我们不再设置LLM，因为我们不使用查询引擎，而是直接使用检索器
    
    # 判断是否已经存在索引
    index_exists = False
    if os.path.exists(PERSIST_DIR):
        try:
            # 尝试获取collection
            if "riddles" in [col.name for col in chroma_client.list_collections()]:
                # 检查索引文件是否存在
                if os.path.exists(os.path.join(PERSIST_DIR, "docstore.json")):
                    index_exists = True
        except Exception as e:
            print(f"检查索引时出错: {e}")
            index_exists = False
    
    if index_exists:
        # 加载已存在的索引
        print("正在加载已存在的索引...")
        try:
            riddle_collection = chroma_client.get_collection("riddles")
            chroma_vector_store = ChromaVectorStore(chroma_collection=riddle_collection)
            storage_context = StorageContext.from_defaults(vector_store=chroma_vector_store, persist_dir=PERSIST_DIR)
            riddle_index = load_index_from_storage(storage_context)
            print("索引加载完成")
        except Exception as e:
            print(f"加载索引时出错: {e}")
            index_exists = False  # 如果加载失败，重新创建索引
    
    if not index_exists:
        # 第一次运行，创建索引
        print("正在创建新索引...")
        # 确保数据目录存在
        riddle_data_path = os.path.join(DATA_DIR, "riddle")
        
        # 删除已存在的collection（如果有）
        try:
            if "riddles" in [col.name for col in chroma_client.list_collections()]:
                print("发现已存在的riddles集合，正在删除...")
                chroma_client.delete_collection("riddles")
                print("已删除旧集合")
        except Exception as e:
            print(f"尝试删除旧集合时出错: {e}")
        
        # 读取JSON文件并准备文档
        with open(os.path.join(riddle_data_path, "data.json"), "r", encoding="utf-8") as f:
            riddles_data = json.load(f)
        
        # 将JSON数据转换为文本文档
        documents = []
        from llama_index.core.schema import Document
        for idx, riddle in enumerate(riddles_data):
            doc_text = f"问题: {riddle['instruction']}\n回答: {riddle['output']}"
            documents.append(Document(text=doc_text, id=f"riddle_{idx}"))
        
        # 创建向量存储和索引
        riddle_collection = chroma_client.create_collection("riddles")
        chroma_vector_store = ChromaVectorStore(chroma_collection=riddle_collection)
        storage_context = StorageContext.from_defaults(vector_store=chroma_vector_store)
        # 不再需要传递service_context
        riddle_index = VectorStoreIndex.from_documents(
            documents, 
            storage_context=storage_context
        )
        
        # 保存索引
        storage_context.persist(persist_dir=PERSIST_DIR)
        print("索引创建完成")

# 在应用启动时执行初始化
@app.on_event("startup")
async def startup_event():
    init_index()

# 查询接口
@app.post("/query")
async def query_riddle(query: str):
    global riddle_index
    
    try:
        if riddle_index is None:
            raise HTTPException(status_code=500, detail="索引尚未初始化")
        
        # 直接使用向量检索，不依赖LLM进行查询
        # 创建一个检索器而不是查询引擎
        retriever = riddle_index.as_retriever(similarity_top_k=3)
        print(f"执行查询: {query}")
        # 获取最相关的文档节点
        nodes = retriever.retrieve(query)
        
        # 提取检索到的文档内容
        result_texts = []
        for node in nodes:
            result_texts.append(node.get_content())
        
        response_text = "\n\n".join(result_texts)
        print(f"查询结果: {response_text}")
        
        return {"response": response_text}
    except Exception as e:
        error_detail = traceback.format_exc()
        print(f"查询过程出错: {str(e)}")
        print(f"详细错误: {error_detail}")
        raise HTTPException(status_code=500, detail=f"查询处理出错: {str(e)}")

# DeepSeek API接口
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_API_KEY = get_api_key()  # 使用获取的API密钥

@app.post("/chat/completions")
async def chat_completions(request: ChatRequest):
    # 角色1是猜谜大师，需要从本地知识库获取相关内容
    if "你是模型A，猜谜大师" in request.messages[0]["content"]:
        # 获取用户的最后一条消息
        user_query = next((msg["content"] for msg in reversed(request.messages) if msg["role"] == "user"), None)
        
        if user_query:
            try:
                # 查询本地知识库
                query_response = await query_riddle(user_query)
                context = query_response["response"]
                
                # 限制上下文长度，避免超出API限制
                if len(context) > 2000:
                    print(f"上下文过长 ({len(context)} 字符)，截断至2000字符")
                    context = context[:1997] + "..."
                
                # 创建给猜谜大师的提示，包含从知识库检索的相关内容
                system_prompt = f"""你是一位猜谜大师，精通各种脑筋急转弯和谜语。
                基于以下参考内容回答用户的问题，如果找到了准确匹配的谜语，请用生动有趣的方式给出答案。
                如果没有找到准确匹配的谜语，可以基于你的知识创造性地回答。
                
                参考内容：
                {context}
                """
                
                # 更新系统提示
                updated_messages = [{"role": "system", "content": system_prompt}]
                # 添加用户查询
                updated_messages.append({"role": "user", "content": user_query})
                
                # 调用DeepSeek API
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
                }
                
                # 为DeepSeek构建正确的消息格式
                payload = {
                    "model": "deepseek-chat",  # 使用DeepSeek Chat模型
                    "messages": updated_messages,
                    "temperature": request.temperature,
                    "max_tokens": request.max_tokens
                }
                
                print(f"发送到DeepSeek API的请求: {DEEPSEEK_API_URL}")
                print(f"消息内容: {updated_messages}")
                response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=30)  # 添加超时设置
                
                if response.status_code != 200:
                    print(f"DeepSeek API返回错误，状态码: {response.status_code}")
                    print(f"错误详情: {response.text}")
                    raise Exception(f"DeepSeek API返回错误 (状态码: {response.status_code}): {response.text}")
                
                response_json = response.json()
                print(f"DeepSeek API响应成功")
                return response_json
                
            except Exception as e:
                error_detail = traceback.format_exc()
                print(f"处理猜谜请求时出错: {str(e)}")
                print(f"详细错误: {error_detail}")
                raise HTTPException(status_code=500, detail=f"处理猜谜请求时出错: {str(e)}")
    
    # 其他模型直接转发到DeepSeek API
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
        }
        
        # 确保消息格式正确
        messages = request.messages
        
        payload = {
            "model": request.model,
            "messages": messages,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens
        }
        
        print(f"转发到DeepSeek API，模型: {request.model}")
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=30)  # 添加超时设置
        
        if response.status_code != 200:
            print(f"DeepSeek API返回错误，状态码: {response.status_code}")
            print(f"错误详情: {response.text}")
            raise Exception(f"DeepSeek API返回错误 (状态码: {response.status_code}): {response.text}")
        
        response_json = response.json()
        print(f"DeepSeek API响应成功")
        return response_json
        
    except Exception as e:
        error_detail = traceback.format_exc()
        print(f"调用DeepSeek API时出错: {str(e)}")
        print(f"详细错误: {error_detail}")
        raise HTTPException(status_code=500, detail=f"调用DeepSeek API时出错: {str(e)}")

# 测试DeepSeek API连接
@app.get("/test-deepseek")
async def test_deepseek_api():
    """测试DeepSeek API是否可用"""
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "你好，这是一个测试请求。"},
                {"role": "user", "content": "你好吗？"}
            ],
            "temperature": 0.7,
            "max_tokens": 100
        }
        
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)
        
        if response.status_code != 200:
            return {
                "status": "error",
                "code": response.status_code,
                "message": response.text
            }
        
        return {
            "status": "success",
            "response": response.json()
        }
    except Exception as e:
        error_detail = traceback.format_exc()
        return {
            "status": "error",
            "message": str(e),
            "detail": error_detail
        }

if __name__ == "__main__":
    print("正在启动服务器，监听地址: http://127.0.0.1:8000")
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
