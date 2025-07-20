# 📚 Documentação do Projeto - Links Rápidos

## 📋 **Documentos Principais**

| Documento | Descrição | Link |
|-----------|-----------|------|
| **📖 README** | Visão geral e quick start | [readme.md](readme.md) |
| **🏗️ Arquitetura** | Documentação técnica detalhada | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| **🚀 Guia Rápido** | Comandos essenciais | [docs/GUIA_RAPIDO.md](docs/GUIA_RAPIDO.md) |
| **📊 Relatórios** | Testes e coverage | [docs/REPORTS.md](docs/REPORTS.md) |

## 🎯 **Para Diferentes Perfis**

### **👨‍💼 Product Manager / Stakeholder**
1. Leia o [README.md](readme.md) - seção "Solução" e "Resultados"
2. Acesse http://localhost:8502 para ver a interface
3. Confira o dashboard em http://localhost:3000

### **👨‍💻 Desenvolvedor**
1. Leia [ARCHITECTURE.md](ARCHITECTURE.md) para entender a estrutura
2. Execute `docker-compose up -d` para subir o ambiente
3. Rode os testes com `python -m pytest tests/`

### **🔧 DevOps / SRE**
1. Confira [docker-compose.yaml](docker/docker-compose.yaml)
2. Veja métricas em http://localhost:8080/metrics
3. Monitore via Grafana em http://localhost:3000

### **📊 Data Scientist**
1. Explore [src/models/](src/models/) para o pipeline ML
2. Execute `python simulate_production_environment.py`
3. Analise drift detection com `python test_drift_simple.py`

## 🚀 **Quick Actions**

```bash
# Iniciar tudo
docker-compose up -d

# Testar API
curl -X POST http://localhost:8080/predict -H "Content-Type: application/json" -d '{"candidate":{"skills":"python","experience":"3 anos"},"vacancy":{"requirements":"python","seniority":"pleno"}}'

# Simulação de produção
python scripts/simulation/simulate_production_environment.py

# Ver logs
docker-compose logs -f api

# Parar tudo
docker-compose down
```

## 📊 **Status Atual**

- ✅ **API**: Funcionando (http://localhost:8080)
- ✅ **UI**: Funcionando (http://localhost:8502)  
- ✅ **Monitoring**: Funcionando (http://localhost:3000)
- ✅ **Testes**: 72 testes passando
- ✅ **Drift Detection**: 5 painéis operacionais
- ✅ **Performance**: 78% accuracy, <500ms latência

## 🎯 **Demonstração Completa**

Para uma demonstração completa do sistema:

1. **Deploy**: `docker-compose up -d`
2. **Simular Produção**: `python scripts/simulation/simulate_production_environment.py`
3. **Verificar Dashboard**: Acesse http://localhost:3000
4. **Testar Interface**: Acesse http://localhost:8502
5. **Verificar API**: Teste endpoints via curl ou Postman

---

**TechChallenge Fase 5 - Sistema de IA para Recrutamento**
