# <h1 align="center"><font color="gree">Kit de Desenvolvimento de Agentes (ADK) do Google: Um Guia com Projeto de Demonstração</font></h1>


<font color="pink">Senior Data Scientist.: Dr. Eddy Giusepe Chirinos Isidro</font>

Trabalho baseado no tutorial de [Aashi Dutt]().

![](https://assets.st-note.com/production/uploads/images/183502776/rectangle_large_type_2_3f267c176f6c7c90ca654dddd5f50591.png?fit=bounds&quality=85&width=1280)



![](https://media.licdn.com/dms/image/v2/D4E22AQHu478AK0uscg/feedshare-shrink_800/B4EZY_4ttJGYAg-/0/1744828554860?e=2147483647&v=beta&t=EDOOJRmpY3wMHmaAwP6m7mqDqi_ef4CJ5UY7dK2PKoI)


Aqui vamos aprender a criar um assistente de viagens multiagente usando o Agent Development Kit (`ADK`) do Google e o protocolo Agent2Agent (`A2A`).

Neste repositório, aprenderemos como criar um assistente de viagem multiagente com tecnologia de IA usando o novo `Agent Development Kit` (ADK) de código aberto do Google e o protocolo `A2A` (Agent-to-Agent) .

Usaremos `vários agentes` para gerenciar voos, hotéis e recomendações de atividades, comunicando-nos por meio de `APIs REST` e servidores `FastAPI`. No final, finalizaremos tudo com um frontend `Streamlit` limpo para uma experiência intuitiva ao usuário.


## <font color="red">O que é o Agent Development Kit (ADK) do Google?</font>

O `ADK` do Google é um framework modular e pronta para produção e para a criação de agentes com `LLM`. É o mesmo kit de ferramentas que alimenta os agentes dentro dos produtos do Google, como o `Agentspace` e o `Customer Engagement Suite`. Agora de [código aberto](https://google.github.io/adk-docs/), ele ajuda os desenvolvedores a criar aplicativos multiagentes poderosos, flexíveis e interoperáveis.

### <font color="yellow">Por que usar o Agent Development Kit (ADK)?</font>

O `ADK` oferece a flexibilidade do `Python` com estruturas integradas para gerenciamento de estado, retornos de chamada, streaming e entrada/saída estruturada. Vamos dar uma olhada em seus principais recursos:

* `Multiagente por design`: o ADK pode compor agentes em fluxos de trabalho paralelos, sequenciais ou hierárquicos.

* `Independente do modelo` (Model-agnostic): funciona com `Gemini`, `GPT-4o`, `Claude`, `Mistral` e outros via `LiteLlm`.

* `Modular e escalável`: o usuário pode definir agentes especializados e delegar de forma inteligente usando orquestração integrada.

* `Pronto para streaming`: suporta interação em tempo real, incluindo áudio/vídeo bidirecional.

* `Ferramentas integradas`: suporta `CLI` local e interface de usuário (UI) web para depuração e avaliação.

* `Suporta implantação`: o ADK conteineriza e implanta agentes facilmente em todos os ambientes.


### <font color="yellow">O que é o protocolo Agent2Agent (A2A) do Google?</font>

O protocolo `Agent2Agent` (A2A) é um padrão aberto e independente de fornecedores, desenvolvido pelo `Google` para permitir fácil comunicação e colaboração entre agentes de IA em diversas plataformas e frameworks.

Os agentes do `ADK` expõem um endpoint HTTP padrão `/run` e metadados por meio de `.well-known/agent.json`. Isso permite a descoberta de agentes e a comunicação fácil entre eles (ou até mesmo orquestradores externos como [LangGraph](https://www.datacamp.com/tutorial/langgraph-tutorial) ou [CrewAI](https://www.datacamp.com/tutorial/crew-ai)).

Embora opcional, adicionar o arquivo de metadados A2A torna seus agentes interoperáveis ​​com o ecossistema mais amplo de ferramentas de agente e orquestradores.



## <font color="red">Visão geral do projeto: Planejador de viagens com tecnologia de IA com ADK e A2A</font>

Este projeto cria um planejador de viagens que:

* Aceita destino, datas e orçamento como entrada.

* Chama três agentes separados:
  * `flight_agent`: Recomenda opções de voo.
  * `stay_agent`: Encontra hotéis dentro do orçamento.
  * `activities_agent`: Sugere atividades envolventes.

* Depois, usa uma central `host_agent` para orquestrar todas as solicitações.

* Por fim, usa uma interface de usuário `Streamlit` para interação com o usuário.

Todos os agentes são hospedados como servidores `FastAPI` separados e expõem uma endpoint `/run`. A comunicação é feita por meio do `cliente` compartilhado compatível com `A2A`.


<font color="pink">Observação</font>: 

Este projeto é executado inteiramente na sua máquina local para simplificar, mas você pode facilmente implantar cada agente e a interface do usuário em plataformas de nuvem como `Render`, `Railway` ou `Google Cloud Run` para acesso escalável.

### <font color="blue">`Etapa 1:` Pré-requisitos</font>

Vamos começar instalando as seguintes bibliotecas:


```bash
uv add google-adk litellm fastapi uvicorn httpx pydantic openai streamlit
```

Em seguida, configure sua chave de `API OpenAI` — fique à vontade para usar outro provedor de modelo. Para aprender a configurar sua chave de API OpenAI, recomendo este tutorial introdutório sobre a [API GPT-4o](https://www.datacamp.com/tutorial/gpt4o-api-openai-tutorial).

```bash
export OPENAI_API_KEY="your_key_here"
```

### <font color="blue">`Etapa 2:` Esquema e utilitários compartilhados</font>

Antes de construirmos agentes inteligentes, precisamos definir uma linguagem comum para que eles se comuniquem. Em nossa configuração, isso é feito usando:

* Um esquema compartilhado para entrada (definido via `Pydantic`)

* Um utilitário de `cliente REST` para chamar agentes

* Um wrapper de servidor REST para padronizar a endpoint `/run` em todos os agentes

Eles são colocados em pastas `shared/` e `common/` para manter o código modular. Vamos analisar cada um deles.


#### <font color="cyan">Criando um arquivo shared/schemas.py</font>

Definimos um esquema `TravelRequest` usando o `Pydantic`. Isso garante que todos os agentes concordem com a estrutura das solicitações recebidas, o que inclui o destino, as datas da viagem e o orçamento do usuário.

```python
from pydantic import BaseModel

class TravelRequest(BaseModel):
    destination: str
    start_date: str
    end_date: str
    budget: float
```

Esta `Class` ajuda em:

* Manter a entrada consistente para todos os agentes.

* Adicionando validação automática com `FastAPI`.

* Simplificando a reutilização de código.


#### <font color="cyan">Criando um arquivo common/a2a_client.py</font>

Este utilitário assíncrono leve permite que qualquer agente (especialmente o `host`) invoque outro agente usando o protocolo `A2A` chamando a endpoint `/run` de extremidade.

```python
import httpx

async def call_agent(url, payload):
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, timeout=60.0)
        response.raise_for_status()
        return response.json()
```

Este utilitário envia de forma assíncrona uma solicitação ``POST`` para a endpoint /run de outro agente usando `httpx`. Ele retorna a resposta `JSON` analisada e gera um erro se a solicitação falhar.

Usaremos esse utilitário em nosso agente host para chamar `flight_agent`, `stay_agent`, e `activities_agent`.


#### <font color="cyan">Criando um arquivo common/a2a_server.py</font>

Em vez de escrever uma rota `FastAPI` personalizada para cada agente, nós a generalizamos usando uma função `create_app(agent)`, que manipula:

* Servindo o agente em `/run`

* Recebendo uma solicitação de viagem

* Retornando uma resposta estruturada

```python
from fastapi import FastAPI
import uvicorn

def create_app(agent):
    app = FastAPI()
    @app.post("/run")
    async def run(payload: dict):
        return await agent.execute(payload)
    return app
```

Este utilitário cria um aplicativo `FastAPI` com uma `/run` rota padrão que delega a execução ao agente fornecido. Ele garante uma interface de agente para agente (`A2A`) consistente para todos os serviços usando entrada `JSON` estruturado.

Juntos, esses componentes compartilhados tornam nosso sistema multiagente mais sustentável, reutilizável e alinhado à filosofia `A2A` do `Google` de mensagens interagentes simples e estruturadas.


### <font color="blue">`Etapa 3:` Construindo o Sistema Multiagente com ADK e A2A</font>

Agora que compartilhamos contratos e utilitários, vamos começar a construir os agentes individuais. Para transformar isso em um sistema ``verdadeiramente modular`` e ``multiagente``, usaremos o protocolo ``A2A do Google`` — uma interface simples baseada em HTTP que permite que os agentes se comuniquem de forma consistente e interoperável.

O A2A (``Agent-to-Agent``) permite a coordenação ``plug-and-play`` entre agentes, sejam eles funções `Python` locais ou hospedados em redes. Cada agente expõe uma endpoint `/run` com um esquema comum e atua como um serviço.

Em nossa demonstração, temos quatro agentes:

* `host_agent`: Orquestra todos os outros agentes.

* `flight_agent`: Encontra voos adequados.

* `stay_agent`: Sugere acomodações.

* `activities_agent`: Recomenda a participação em atividades locais.

Todos os agentes são estruturados de forma semelhante, com 3 arquivos e uma subpasta:

```
agents/
├── host_agent/
│   │   ├── agent.py              # Opcional se a lógica do host for mínima
│   │   ├── task_manager.py       # Chama outros agentes e agrega respostas
│   │   ├── __main__.py           # Inicia o aplicativo FastAPI via common/a2a_server.py
│   │   └── .well-known/
│   │       └── agent.json        # Metadados do Card do agente A2A
├── flight_agent/
├── stay_agent/
└── activities_agent/
```

Cada agente usa ``google.adk.agents.Agent``, um wrapper ``LiteLlm`` de modelo, e ``Runner`` para execução. Comece criando os seguintes arquivos dentro da  pasta ``activities_agent`` e repita o mesmo para ``flight_agent`` e ``stay_agent``.

#### <font color="cyan">Criando um arquivo agent.py</font>

Vamos agora definir a lógica do nosso ``activities_agent``, que será responsável por gerar experiências locais envolventes com base no itinerário de viagem do usuário. 

##### <font color="gree">``Etapa 1:`` Importações</font>

Começamos importando módulos essenciais para configurar e executar nosso agente.

```python
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import json
```

Este agente usa componentes do ``Google ADK``, como ``Agent``, ``Runner`` e ``LiteLlm``, lida com o gerenciamento de estado usando ``InMemorySessionService``. A biblioteca ``Types`` é usada para construir prompts estruturados.


##### <font color="gree">``Etapa 2:`` Agente de atividades</font>
Agora, instanciamos o próprio agente usando a classe Agent do ADK.

```python
activities_agent = Agent(
    name="activities_agent",
    model=LiteLlm("openai/gpt-4o"),
    description="Sugere atividades interessantes para o usuário em um destino.",
    instruction=(
        "Dado um destino, datas e orçamento, sugere 2-3 atividades envolventes de turismo ou culturais. "
        "Para cada atividade, forneça um nome, uma descrição curta, estimativa de preço e duração em horas. "
        "Responda, SEMPRE, em português brasileiro (pt-BR). Mantenha-o conciso e bem formatado."
    )
)
```	

O parâmetro de instrução define o ``prompt do sistema`` que orienta o comportamento do ``LLM``. Embora este exemplo use linguagem simples, você pode ajustar a instrução para retornar `JSON` estruturado para facilitar a análise.


##### <font color="gree">``Etapa 3:`` Gerenciamento de sessão</font>
Em seguida, para monitorar as interações do usuário, configuramos um Runner junto com as informações da sessão.

```python
session_service = InMemorySessionService()

runner = Runner(
    agent=activities_agent,
    app_name="activities_app",
    session_service=session_service
)
USER_ID = "user_activities"
SESSION_ID = "session_activities"
```
O `Runner` agente gerencia a execução de uma sessão específica do aplicativo (app). Enquanto a classe `InMemorySessionService` armazena o contexto na memória. Logo, definimos os IDs de usuário e de sessão. No entanto, em produção, eles podem ser dinâmicos ou específicos do usuário. Isso garante que uma nova sessão do `ADK` exista antes de enviar qualquer prompt ao agente `LLM`.


##### <font color="gree">``Etapa 4:`` Executando a lógica do agente</font>
A função `execute()` manipula solicitações de entrada, cria um prompt, invoca o modelo e analisa a saída.

```python
async def execute(request):
    session_service.create_session(
        app_name="activities_app",
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    prompt = (
        f"Usuário está voando para {request['destination']} de {request['start_date']} até {request['end_date']}, "
        f"com um orçamento de {request['budget']}. Sugere 2-3 atividades, cada uma com nome, descrição, estimativa de preço e duração. "
        f"Responda em formato JSON usando a chave 'activities' com uma lista de objetos de atividade."
    )
    message = types.Content(role="user", parts=[types.Part(text=prompt)])
    async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=message):
        if event.is_final_response():
            response_text = event.content.parts[0].text
            try:
                parsed = json.loads(response_text)
                if "activities" in parsed and isinstance(parsed["activities"], list):
                    return {"activities": parsed["activities"]}
                else:
                    print("A chave 'activities' está ausente ou não é uma lista no JSON da resposta")
                    return {"activities": response_text}  # fallback to raw text
            except json.JSONDecodeError as e:
                print("JSON parsing failed:", e)
                print("Conteúdo da resposta:", response_text)
                return {"activities": response_text}  # fallback to raw text
```
A função `execute()` cria dinamicamente um `prompt` usando os parâmetros da solicitação recebida, como destino, datas e orçamento. Veja o que acontece nos bastidores:

* O prompt instrui o modelo a retornar um objeto `JSON` estruturado contendo uma lista de atividades.

* Um objeto `Content` é construído e passado para o `ADK Runner`, que aguarda de forma assíncrona a resposta final do modelo usando um gerador de streaming.

* Depois que a resposta final é recebida, o agente extrai a saída de texto bruto e tenta analisá-la como `JSON`.

* Se a análise for bem-sucedida e a chave de atividades esperada existir, os dados estruturados serão retornados.

* Se a chave estiver ausente ou malformada, a alternativa é retornar a resposta em texto bruto para que a interface do usuário ainda tenha uma saída utilizável.

* Essa abordagem de tratamento duplo garante uma degradação suave quando o LLM retorna texto simples em vez de `JSON` estruturado.

Essa estratégia melhora a robustez e a experiência do usuário, especialmente quando as saídas do modelo variam ligeiramente devido à `temperature` ou à interpretação do `Prompt`.


#### <font color="cyan">Criando um arquivo `task_manager.py`</font>
Depois de definir `execute()` e a lógica interna `agent.py`, agora a conectamos à configuração do servidor compatível com `ADK` usando `task_manager.py`.

```python
from .agent import execute

async def run(payload):
    return await execute(payload)
```
Este arquivo atua como um wrapper fino em torno da função `execute()` definida anteriormente. Ele torna o método `run()` disponível para módulos externos, especialmente o script do servidor em `__main__.py`.



#### <font color="cyan">Criando um arquivo `__main__.py`</font>
O arquivo `__main__.py` inicia um servidor `FastAPI` na porta `8003`, atendendo o agente no ponto de extremidade `/run`.

```python
from common.a2a_server import create_app
from .task_manager import run

app = create_app(agent=type("Agent", (), {"execute": run}))
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8003)
```
Aqui está o que está acontecendo:

* O `create_app()` (de `common/a2a_server.py`) envolve nosso agente em uma interface `FastAPI` padrão compatível com `A2A`.

* Construímos dinamicamente um objeto com o método `execute()` para que o `ADK` possa invocar `run()` corretamente.

* Essa separação nos permite manter interfaces de API sem estado enquanto reutilizamos a lógica do agente principal.


#### <font color="cyan">Criando um arquivo `.well-known/agent.json`</font>
Usamos esse arquivo `JSON` para descrever a identidade e a finalidade do agente, de acordo com o protocolo `A2A` (Agent-to-Agent).

```json
{
    "name": "activity_agent",
    "description": "Agente que fornece detalhes de atividades."
  }
```

`Observação:`

Embora o arquivo `.well-known/agent.json` não seja usado diretamente por nossos agentes neste projeto, ele adere à especificação `A2A` e é importante para descoberta, introspecção e compatibilidade futura com orquestradores como `LangGraph`, `CrewAI` ou o registro de agentes do `Google`.

<font color="gree">Uma lógica semelhante é usada para `flight_agent` e `stay_agent` também.</font>



### <font color="blue">``Etapa 4:`` Coordenação com o host_agent</font>

O `host_agent` atua como um planejador central para a demonstração. O `host_agent` exemplifica o padrão de controlador em sistemas multiagentes. Ele separa a tomada de decisão da execução, permitindo que cada agente a jusante (`downstream`) se concentre em seu nicho, centralizando a lógica de coordenação. Isso não apenas simplifica os testes e o escalonamento, como também espelha a arquitetura de microsserviços do mundo real em sistemas distribuídos.

Ele envia o mesmo `payload` para todos os três agentes usando suas `/run` APIs expostas e mescla os resultados. Vamos adicionar os seguintes arquivos à pasta `host_agent`.

#### <font color="cyan">Criando um arquivo `agent.py`</font>
Vamos começar com importações básicas.

```python
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
```

Este bloco de importação traz todos os blocos de construção principais necessários para definir e executar um agente baseado em `LLM` usando o `Google ADK`: class `Agent`, `wrapper LLM` leve, `Runner` para manipulação de execução e gerenciamento de sessão na memória.

```python
host_agent = Agent(
    name="host_agent",
    model=LiteLlm("openai/gpt-4o"),
    description="Coordena a viagem de planejamento de viagem chamando agentes de voo, hospedagem e atividades.",
    instruction="Você é o agente host responsável por orquestrar tarefas de planejamento de viagem. "
                "Você chama agentes externos para reunir voos, hospedagens e atividades, então retorna um resultado final."
)
session_service = InMemorySessionService()
runner = Runner(
    agent=host_agent,
    app_name="host_app",
    session_service=session_service
)
USER_ID = "user_host"
SESSION_ID = "session_host"
```
O código acima define um `agente ADK` de nível superior responsável por coordenar todo o plano de viagem. Embora não invoquemos subagentes do LLM nesta implementação, o prompt do sistema configura a função para uma extensão futura em que o LLM poderia potencialmente lidar com o uso de ferramentas (`tools`) e o meta-raciocínio (`meta-reasoning`).

```python
async def execute(request):
    # Ensure session exists
    session_service.create_session(
        app_name="host_app",
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    prompt = (
        f"Planeje uma viagem para {request['destination']} de {request['start_date']} até {request['end_date']} "
        f"dentro de um orçamento total de {request['budget']}. Chame os agentes de voos, hospedagens e atividades para obter resultados."
    )
    message = types.Content(role="user", parts=[types.Part(text=prompt)])
    async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=message):
        if event.is_final_response():
            return {"summary": event.content.parts[0].text}
```
Esta função `execute()` serve como o principal ponto de entrada para o `LLM do agente host`. Ela:

* Inicializa uma sessão (para suporte de `memória`, se necessário)

* Constrói dinamicamente um prompt de usuário

* Envia para o modelo usando o método `runner.run_async()` do `ADK`

* Por fim, aguarda e extrai a resposta final


#### <font color="cyan">Criando um arquivo `task_manager.py`</font>
O gerenciador de tarefas executa a lógica de orquestração chamando agentes remotos e gerenciando todo o fluxo de trabalho de planejamento de viagens. Para sua implementação prática, definimos as `URLs` de serviço para cada agente filho. Essas endpoints estão em conformidade com o protocolo `A2A` /run e esperam um esquema JSON compartilhado `TravelRequest`.

```python
from common.a2a_client import call_agent

FLIGHT_URL = "http://localhost:8001/run"
STAY_URL = "http://localhost:8002/run"
ACTIVITIES_URL = "http://localhost:8003/run"
```

Agora, definimos o `payload`:
```python
async def run(payload):
    # Imprima o que o agente host está enviando:
    print("Incoming payload:", payload)
    flights = await call_agent(FLIGHT_URL, payload)
    stay = await call_agent(STAY_URL, payload)
    activities = await call_agent(ACTIVITIES_URL, payload)
    # Log outputs
    print("flights:", flights)
    print("stay:", stay)
    print("activities:", activities)
    # Certifique-se de que todos são dicionários antes de acessar:
    flights = flights if isinstance(flights, dict) else {}
    stay = stay if isinstance(stay, dict) else {}
    activities = activities if isinstance(activities, dict) else {}
    return {
        "flights": flights.get("flights", "Nenhum voo retornado."),
        "stay": stay.get("stays", "Nenhuma opção de hospedagem retornada."),
        "activities": activities.get("activities", "Nenhuma atividade encontrada.")
    }
```
Esta função usa a função `call_agent()` auxiliar para despachar o payload para cada serviço downstream e registra entradas e saídas para visibilidade durante o desenvolvimento. Este arquivo é essencialmente onde reside a verdadeira lógica de orquestração.


#### <font color="cyan">Criando um arquivo `__main__.py`</font>



#### <font color="cyan">Criando um arquivo `.well-known/agent.json`</font>



### <font color="blue">``Etapa 5:`` Construindo a IU com Streamlit</font>









Links de estudo:

* [Agent Development Kit (ADK)](https://google.github.io/adk-docs/)

* [How to Build Multi AI Agents with Google Agent Development Kit (ADK) For Beginners](https://www.youtube.com/watch?v=cz2pKLPw994)

* [datacamp: ADK and protocolo A2A](https://www.datacamp.com/tutorial/agent-development-kit-adk)









Thank God!