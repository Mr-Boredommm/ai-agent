# AI Agent - 角色扮演知识库问答系统

这是一个基于本地知识库的角色扮演AI问答系统，目前实现了"猜谜大师"角色，能够回答脑筋急转弯问题。

## 技术架构

- 前端：Vue 3 + Element Plus
- 后端：FastAPI
- 向量数据库：ChromaDB
- 大语言模型：DeepSeek API
- 向量嵌入：本地Multilingual-MiniLM-L12-v2模型
- RAG技术：使用LlamaIndex进行知识库检索

## 系统要求

- Windows 11 (x86架构)
- Python 3.12 (建议使用Conda环境)
- Node.js 18+

## 项目设置与运行

### 安装前端依赖

```sh
npm install
```

### 启动前端开发服务器

```sh
npm run dev
```

### 设置后端服务器

1. 进入server目录
2. 首次运行时执行以下命令创建Conda环境:

```sh
conda create -n py312 python=3.12
```

3. 启动后端服务器:

```sh
# 使用提供的批处理文件启动服务器
start_server.bat
```

或手动启动:

```sh
conda activate py312
pip install -r requirements.txt
python app.py
```

## 项目功能

- 角色扮演：AI扮演猜谜大师角色，回答用户的脑筋急转弯问题
- 知识库检索：使用向量数据库存储和检索相关问答
- 本地Embedding：使用本地多语言模型进行文本向量化
- 持久化存储：ChromaDB保存知识库向量，避免重复索引

## 工作原理

1. 系统启动时，LlamaIndex读取`data/riddle/data.json`文件，创建向量索引并存储在ChromaDB中
2. 用户发送问题时，后端查询向量数据库找到最相关的谜语
3. 将检索结果与用户问题一起发送给DeepSeek API进行处理
4. DeepSeek API根据上下文生成猜谜大师风格的回答
5. 前端展示生成的回答

## 注意事项

- 首次启动后端服务器时，系统会创建向量索引，可能需要一些时间
- 后续启动将直接从ChromaDB加载索引，速度更快
- 确保指定的本地embedding模型路径正确存在

## API密钥配置

后端服务使用DeepSeek API进行大语言模型调用。您可以通过以下方式配置API密钥：

1. **使用配置文件**：
   - 复制 `server/config.json.template` 到 `server/config.json`
   - 在 `config.json` 中填入您的DeepSeek API密钥

2. **使用环境变量**：
   - 设置环境变量 `DEEPSEEK_API_KEY` 为您的API密钥
   
如果没有提供有效的API密钥，系统将使用默认密钥，但可能会受到API调用限制。

## 故障排除

如果遇到API 500错误，可能原因包括：

1. DeepSeek API密钥无效或已过期
2. 网络连接问题，API服务器不可用
3. 后端索引创建失败

您可以通过以下方式诊断问题：

- 查看后端控制台日志获取详细错误信息
- 访问 `http://localhost:8000/test-deepseek` 测试API连接是否正常
- 确保已正确安装所有依赖项

## 项目扩展

目前仅实现了猜谜大师角色。可以通过以下步骤添加更多角色:

1. 在`data`目录下创建新的知识库数据
2. 在后端`app.py`中添加新的知识库索引创建和查询逻辑
3. 在前端`chat.vue`中添加新的角色配置

## 许可证

[MIT](LICENSE)
