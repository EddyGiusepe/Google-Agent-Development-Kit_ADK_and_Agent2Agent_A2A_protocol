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


##### <font color="gree">``Etapa 1:`` Importações</font>


##### <font color="gree">``Etapa 2:`` Agente de atividades</font>


##### <font color="gree">``Etapa 3:`` Gerenciamento de sessão</font>


##### <font color="gree">``Etapa 4:`` Executando a lógica do agente</font>





#### <font color="cyan">Criando um arquivo task_manager.py</font>





#### <font color="cyan">Criando um arquivo __main__.py</font>




#### <font color="cyan">Criando um arquivo .well-known/agent.json</font>



### <font color="blue">``Etapa 4:`` Coordenação com o host_agent</font>






Links de estudo:

* [Agent Development Kit (ADK)](https://google.github.io/adk-docs/)

* [How to Build Multi AI Agents with Google Agent Development Kit (ADK) For Beginners](https://www.youtube.com/watch?v=cz2pKLPw994)

* [datacamp: ADK and protocolo A2A](https://www.datacamp.com/tutorial/agent-development-kit-adk)









Thank God!