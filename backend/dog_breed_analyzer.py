from duckduckgo_search import DDGS
import json
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def search_dog_breed(breed_name):
    # Initialize DuckDuckGo search
    ddgs = DDGS()
    
    # Search for breed information in Korean
    breed_info = list(ddgs.text(f"{breed_name} 견종 특징", max_results=5))
    
    # Search for personality information in Korean
    personality_info = list(ddgs.text(f"{breed_name} 견종 성격", max_results=5))
    
    # Return raw search results
    return {
        'characteristics': breed_info,
        'personality': personality_info
    }

def summarize_breed_info(breed_name, characteristics, personality):
    # Initialize the language model with gpt-4o-mini
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    
    # Create a prompt template
    prompt = ChatPromptTemplate.from_template(
        """당신은 전문적인 견종 분석가입니다. 
        다음 정보를 바탕으로 {breed_name}에 대한 깔끔하고 이해하기 쉬운 설명을 작성해주세요.
        
        특징 정보:
        {characteristics}
        
        성격 정보:
        {personality}
        
        다음 지침을 따라 설명을 작성해주세요:
        1. 800자 이내로 작성
        2. 깔끔하고 전문적인 말투 사용
        3. 견종의 주요 특징과 성격을 명확하게 설명
        4. 실제 사육 시 고려해야 할 점을 간단히 포함
        5. 장단점을 객관적으로 설명
        6. 불필요한 수식어나 감정적인 표현은 최소화
        
        설명:"""
    )
    
    # Create a chain using the new RunnableSequence syntax
    chain = prompt | llm
    
    # Generate the summary
    result = chain.invoke({
        "breed_name": breed_name,
        "characteristics": characteristics,
        "personality": personality
    })

    return result.content


def analyze_dog_breed(breed_name):
    try:
        # Get raw breed information
        raw_info = search_dog_breed(breed_name)
        
        # Summarize and process the information
        summary = summarize_breed_info(
            breed_name,
            raw_info['characteristics'],
            raw_info['personality']
        )
        
        # Return only the summarized information
        return summary
    except Exception as e:
        print(f"오류가 발생했습니다: {str(e)}")
        return '죄송합니다. 견종 정보를 요약하는 중 오류가 발생했습니다.'

if __name__ == "__main__":
    # Example usage
    breed = "골든 리트리버"
    summary = analyze_dog_breed(breed)
    print(summary) 