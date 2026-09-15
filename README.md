# Sistema de Agendamento

Mini sistema web de agendamento desenvolvido como teste técnico para uma vaga de Estágio Full Stack.

A aplicação permite consultar horários disponíveis para uma determinada data, considerando dias úteis, feriados e horários já ocupados, além de criar e consultar agendamentos persistidos em banco de dados.

## Funcionalidades

- Seleção de uma data para consulta.
- Consulta de horários disponíveis em tempo real.
- Bloqueio de finais de semana.
- Bloqueio de feriados nacionais utilizando a API pública Nager.Date.
- Horário de funcionamento das 08:00 às 18:00.
- Consultas com duração de 1 hora.
- Bloqueio de horários já ocupados.
- Criação de agendamentos.
- Consulta dos agendamentos cadastrados.
- Validação de dados no backend.
- Persistência dos dados em Oracle Database.
- Tratamento de conflitos de agendamento.
- Interface web responsiva.

## Tecnologias

### Backend

- Python
- Flask
- REST API
- `python-oracledb`
- Requests

### Frontend

- HTML5
- CSS3
- JavaScript

### Banco de dados

- Oracle Database
- Oracle SQL Developer para administração e consultas

### API externa

- Nager.Date — API pública de feriados

## Arquitetura

A aplicação segue uma separação simples de responsabilidades:

```text
Frontend
   │
   ▼
Flask REST API
   │
   ├── Routes
   │     ├── /available
   │     └── /appointments
   │
   ▼
Services
   │
   ├── Validação de agenda
   └── Consulta de feriados
   │
   ├───────────────┐
   ▼               ▼
Oracle          Nager.Date
Database        API
```

Fluxo principal:

```text
Usuário escolhe uma data
        ↓
Frontend chama GET /available
        ↓
Backend consulta a API Nager.Date
        ↓
Backend verifica finais de semana e feriados
        ↓
Backend consulta horários ocupados no Oracle
        ↓
Retorna horários disponíveis
        ↓
Usuário seleciona um horário
        ↓
Frontend envia POST /appointments
        ↓
Backend valida novamente
        ↓
Agendamento é salvo no Oracle
        ↓
Frontend exibe a confirmação
```

A validação é feita no backend, portanto as regras de negócio não dependem apenas da interface.

## Regras de negócio

### Horário de funcionamento

O sistema funciona das:

```text
08:00 às 18:00
```

Como cada consulta possui duração de 1 hora, os horários disponíveis são:

```text
08:00
09:00
10:00
11:00
12:00
13:00
14:00
15:00
16:00
17:00
```

O horário `18:00` não é aceito como início de consulta, pois representa o encerramento do expediente.

### Dias não permitidos

Não é possível realizar agendamentos em:

- Sábados;
- Domingos;
- Feriados;
- Datas anteriores ao dia atual.

### Horários ocupados

Um horário já agendado não é retornado como disponível.

Além da validação no backend, o banco possui uma restrição `UNIQUE` para impedir dois agendamentos para a mesma data e horário, inclusive em situações de concorrência.

## API de feriados

O backend utiliza a API pública Nager.Date para consultar os feriados nacionais do Brasil.

Endpoint utilizado:

```text
https://date.nager.at/api/v3/PublicHolidays/2026/BR
```

A consulta é realizada pelo backend, e não diretamente pelo frontend.

Os dados de feriados são armazenados em cache em memória por ano durante a execução da aplicação, evitando requisições desnecessárias à API externa.

## Endpoints

### `GET /available`

Retorna os horários disponíveis para uma determinada data.

Exemplo:

```http
GET /available?date=2026-09-17
```

Exemplo de resposta para um dia útil:

```json
{
  "date": "2026-09-17",
  "available": true,
  "slots": [
    "08:00",
    "09:00",
    "10:00",
    "11:00",
    "12:00",
    "13:00",
    "14:00",
    "15:00",
    "16:00",
    "17:00"
  ]
}
```

Para uma data indisponível, o backend informa o motivo.

Exemplo:

```json
{
  "date": "2026-09-19",
  "available": false,
  "reason": "Fim de semana",
  "slots": []
}
```

### `POST /appointments`

Cria um novo agendamento.

Exemplo de requisição:

```json
{
  "patient_name": "Vitor",
  "patient_phone": "11999999999",
  "appointment_date": "2026-09-17",
  "appointment_time": "10:00"
}
```

Em caso de sucesso, a API retorna `201 Created`.

O backend também valida novamente:

- nome obrigatório;
- tamanho máximo do nome;
- tamanho máximo do telefone;
- formato da data;
- formato do horário;
- horário dentro do expediente;
- data não passada;
- final de semana;
- feriado;
- horário já ocupado.

### `GET /appointments`

Retorna os agendamentos cadastrados.

```http
GET /appointments
```

Também é possível filtrar por data:

```http
GET /appointments?date=2026-09-17
```

## Banco de dados

O projeto utiliza Oracle Database para persistência.

A tabela principal é:

```text
APPOINTMENTS
```

Estrutura:

| Campo | Tipo | Descrição |
|---|---|---|
| `ID` | NUMBER | Identificador do agendamento |
| `PATIENT_NAME` | VARCHAR2(150) | Nome do paciente |
| `PATIENT_PHONE` | VARCHAR2(20) | Telefone do paciente |
| `APPOINTMENT_DATE` | DATE | Data da consulta |
| `APPOINTMENT_TIME` | VARCHAR2(5) | Horário da consulta |
| `STATUS` | VARCHAR2(20) | Status do agendamento |
| `CREATED_AT` | TIMESTAMP | Data e hora de criação |

A combinação:

```text
APPOINTMENT_DATE + APPOINTMENT_TIME
```

possui uma restrição `UNIQUE`, evitando que dois agendamentos ocupem o mesmo horário.

O script de criação da tabela está disponível em:

```text
backend/sql/schema.sql
```

## Configuração do ambiente

### 1. Clonar o repositório

```bash
git clone https://github.com/vitorrodrigues-dev/teste-agendamento.git
cd teste-agendamento
```

### 2. Criar e ativar o ambiente virtual

No Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Instalar as dependências

```powershell
cd backend
pip install -r requirements.txt
```

### 4. Configurar as variáveis de ambiente

Crie um arquivo:

```text
backend/.env
```

baseado no arquivo:

```text
backend/.env.example
```

Exemplo:

```env
ORACLE_USER=seu_usuario
ORACLE_PASSWORD=sua_senha
ORACLE_DSN=oracle.fiap.com.br:1521/ORCL
NAGER_API_BASE=https://date.nager.at/api/v3
FLASK_DEBUG=true
```

> Não versione o arquivo `.env`. Ele contém credenciais do banco e já está incluído no `.gitignore`.

### 5. Configurar o banco

Execute o script:

```text
backend/sql/schema.sql
```

no Oracle Database.

Depois, confirme se a tabela `APPOINTMENTS` foi criada.

## Executando a aplicação

Com o ambiente virtual ativado e dentro de `backend/`:

```powershell
python app.py
```

A aplicação ficará disponível em:

```text
http://127.0.0.1:5000
```

O frontend é servido pelo próprio Flask, portanto não é necessário iniciar um segundo servidor para a interface.

## Estrutura do projeto

```text
teste-agendamento/
│
├── backend/
│   ├── models/
│   │   ├── __init__.py
│   │   └── appointment.py
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── appointments.py
│   │   └── available.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── holidays_service.py
│   │   └── schedule_service.py
│   │
│   ├── sql/
│   │   └── schema.sql
│   │
│   ├── .env.example
│   ├── app.py
│   ├── config.py
│   ├── db.py
│   ├── requirements.txt
│   ├── test_audit_fixes.py
│   ├── test_connection.py
│   └── test_persistence.py
│
├── frontend/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── app.js
│   └── index.html
│
└── .gitignore
```

## Testes e validações

Durante o desenvolvimento foram realizados testes envolvendo:

- Conexão com o Oracle;
- Inserção e consulta de registros;
- Limpeza dos dados de teste;
- Consulta de dia útil;
- Consulta de final de semana;
- Consulta de feriado real;
- Consulta de data passada;
- Horário fora do expediente;
- Horário ocupado;
- Conflito de agendamento;
- Requisições simultâneas para o mesmo horário;
- Nome vazio;
- Data inválida;
- Nome acima do limite permitido;
- Telefone acima do limite permitido;
- Nome exatamente no limite permitido;
- Indisponibilidade simulada da API Nager;
- Consulta de todos os agendamentos;
- Filtro de agendamentos por data;
- Fluxo completo pelo frontend.

Também foram realizados testes de regressão com Oracle e Nager reais após os ajustes finais.

## Tratamento de erros

A API utiliza códigos HTTP para representar diferentes situações:

| Status | Situação |
|---|---|
| `200` | Consulta realizada com sucesso |
| `201` | Agendamento criado |
| `400` | Dados inválidos |
| `409` | Conflito de agendamento ou data indisponível |
| `503` | Serviço externo de feriados indisponível |

Quando a API Nager não está disponível, o sistema não assume que a data é válida. A operação é interrompida e o backend retorna `503`.

## Decisões técnicas

### Backend em Flask

Flask foi utilizado por ser suficiente para o escopo do teste, permitindo implementar uma API REST pequena sem adicionar complexidade desnecessária.

### Oracle Database

Oracle foi utilizado como banco de dados relacional para persistência dos agendamentos, incluindo uma restrição de unicidade para proteção contra conflitos.

### Frontend sem framework

O frontend utiliza HTML, CSS e JavaScript puro. Para o escopo da aplicação, isso mantém a solução simples e reduz dependências sem comprometer a interação necessária.

### Validação no backend

As regras de negócio são verificadas no servidor mesmo quando também existe validação visual no frontend. Dessa forma, uma requisição direta à API não consegue ignorar as regras do sistema.

## Objetivo do projeto

O objetivo foi desenvolver uma solução pequena, porém completa, aplicando conceitos de desenvolvimento Full Stack:

- desenvolvimento de API REST;
- integração entre frontend e backend;
- persistência relacional;
- consumo de API externa;
- validação de regras de negócio;
- tratamento de conflitos;
- organização em camadas;
- configuração por variáveis de ambiente;
- testes de integração e comportamento.

---

## Autor

**Vitor Rodrigues**

Estudante de Análise e Desenvolvimento de Sistemas — FIAP

GitHub: [vitorrodrigues-dev](https://github.com/vitorrodrigues-dev)
