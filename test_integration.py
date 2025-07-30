#!/usr/bin/env python3
"""
Script de teste para verificar a integração entre Streamlit e FastAPI
"""

import requests
import json
import time

def test_fastapi_health():
    """Testa se o FastAPI está funcionando"""
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ FastAPI está funcionando!")
            return True
        else:
            print(f"❌ FastAPI retornou status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao conectar com FastAPI: {e}")
        return False

def test_streamlit_health():
    """Testa se o Streamlit está funcionando"""
    try:
        response = requests.get("http://localhost:8501")
        if response.status_code == 200:
            print("✅ Streamlit está funcionando!")
            return True
        else:
            print(f"❌ Streamlit retornou status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao conectar com Streamlit: {e}")
        return False

def test_recommendation_api():
    """Testa a API de recomendação"""
    try:
        # Dados de teste
        test_data = {
            "usuario": "teste_integracao",
            "senha": "123456",
            "age": 28,
            "height": 175,
            "weight": 75,
            "body_type": "Masculino",
            "goal": "Emagrecimento",
            "training_days": 4,
            "training_time": 60,
            "experience_level": "Intermediário",
            "score_philanthropist": 5.5,
            "score_socialiser": 4.0,
            "score_free_spirit": 3.5,
            "score_achiever": 6.5,
            "score_player": 4.0,
            "score_disruptor": 2.5
        }
        
        response = requests.post(
            "http://localhost:8000/recomendar",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API de recomendação funcionando!")
            print(f"   - ID: {result['id']}")
            print(f"   - Total de desafios: {result['total_desafios']}")
            if result['desafios']:
                print(f"   - Primeiro desafio: {result['desafios'][0]['name']}")
            return True
        else:
            print(f"❌ API de recomendação retornou status {response.status_code}")
            print(f"   Erro: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar API de recomendação: {e}")
        return False

def test_evaluation_api():
    """Testa a API de avaliação"""
    try:
        # Dados de teste
        test_data = {
            "usuario": "teste_integracao",
            "senha": "123456",
            "success": 8,
            "streak": 7,
            "progress_pct": 80,
            "rating": 4,
            "time": 50
        }
        
        response = requests.post(
            "http://localhost:8000/avaliar",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API de avaliação funcionando!")
            print(f"   - Mensagem: {result['mensagem']}")
            print(f"   - ID: {result['id']}")
            return True
        else:
            print(f"❌ API de avaliação retornou status {response.status_code}")
            print(f"   Erro: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar API de avaliação: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("🚀 Testando Integração Squad IA")
    print("=" * 50)
    
    # Testar serviços
    fastapi_ok = test_fastapi_health()
    streamlit_ok = test_streamlit_health()
    
    if not fastapi_ok or not streamlit_ok:
        print("\n❌ Serviços não estão funcionando. Verifique se:")
        print("   - FastAPI está rodando na porta 8000")
        print("   - Streamlit está rodando na porta 8501")
        return
    
    print("\n📊 Testando APIs...")
    
    # Testar APIs
    recommendation_ok = test_recommendation_api()
    evaluation_ok = test_evaluation_api()
    
    print("\n" + "=" * 50)
    print("📋 Resumo dos Testes:")
    print(f"   FastAPI: {'✅' if fastapi_ok else '❌'}")
    print(f"   Streamlit: {'✅' if streamlit_ok else '❌'}")
    print(f"   API Recomendação: {'✅' if recommendation_ok else '❌'}")
    print(f"   API Avaliação: {'✅' if evaluation_ok else '❌'}")
    
    if all([fastapi_ok, streamlit_ok, recommendation_ok, evaluation_ok]):
        print("\n🎉 Integração completa funcionando!")
        print("\n🌐 Acesse:")
        print("   - Interface: http://localhost:8501")
        print("   - API Docs: http://localhost:8000/docs")
    else:
        print("\n⚠️  Alguns testes falharam. Verifique os logs acima.")

if __name__ == "__main__":
    main() 