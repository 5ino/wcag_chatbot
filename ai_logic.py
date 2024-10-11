import os
import openai
from dotenv import load_dotenv
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv()

# OpenAI API 키 설정
openai.api_key = os.getenv("OPENAI_API_KEY")

# 'guide.txt' 파일을 동일 디렉토리에서 로드
text_file_path = "guide.txt"

# 벡터 스토어 디렉토리 경로 생성
vector_store_dir = os.path.join(os.getcwd(), os.path.splitext(os.path.basename(text_file_path))[0])

def load_vector_store(directory):
    faiss_index_path = os.path.join(directory, "index.faiss")
    if os.path.exists(faiss_index_path):
        print(f"벡터 스토어가 이미 존재합니다: {faiss_index_path}")
        # FAISS 벡터 스토어 로드
        vector_store = FAISS.load_local(directory, OpenAIEmbeddings(), allow_dangerous_deserialization=True)
        return vector_store
    return None

def split_text(text, chunk_size=1000, chunk_overlap=200):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    return text_splitter.split_text(text)

def read_text_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def embed_text(text_file_path, directory):
    # 텍스트 파일 읽기
    text = read_text_file(text_file_path)
    
    # 텍스트 분할
    chunks = split_text(text)

    # OpenAI 임베딩 모델 사용 (기본적으로 text-embedding-ada-002 사용)
    embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
    
    # FAISS 벡터 스토어 생성 및 텍스트 임베딩
    vector_store = FAISS.from_texts(chunks, embedding=embeddings)
    
    # 디렉토리가 없으면 생성
    if not os.path.exists(directory):
        os.makedirs(directory)

    # 벡터 스토어를 로컬에 저장
    vector_store.save_local(directory)

    return vector_store

def load_or_create_vector_store():
    vector_store = load_vector_store(vector_store_dir)
    if vector_store:
        print(f"{os.path.basename(text_file_path)} 벡터 스토어를 로드했습니다.")
    else:
        vector_store = embed_text(text_file_path, vector_store_dir)
        print(f"{os.path.basename(text_file_path)} 텍스트를 임베딩하고 저장했습니다.")
    return vector_store

def search_vector_store(vector_store, query, k=3):
    results = vector_store.similarity_search(query, k=k)
    return "\n".join([doc.page_content for doc in results])

def generate_code(prompt, code, guidelines):
    full_prompt = f"""
당신은 웹 접근성 전문가입니다. 아래의 웹 콘텐츠 접근성 지침을 참고하여, 사용자가 제공한 HTML 코드를 '{prompt}' 요청에 따라 수정하세요.

웹 콘텐츠 접근성 지침:
{guidelines}

사용자 제공 코드:
{code}

수정된 코드만 제공하세요.
"""
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": full_prompt}],
        max_tokens=2048,
        temperature=0,
        n=1,
        stop=None,
    )
    generated_code = response.choices[0].message.content.strip()
    return generated_code

def generate_explanation(original_code, modified_code):
    explanation_prompt = f"""
다음은 사용자가 제공한 원본 코드입니다:

원본 코드:
{original_code}

그리고 다음은 수정된 코드입니다:

수정된 코드:
{modified_code}

수정 사항을 간략히 설명해주세요.
"""
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": explanation_prompt}],
        max_tokens=500,
        temperature=0,
        n=1,
        stop=None,
    )
    explanation = response.choices[0].message.content.strip()
    return explanation