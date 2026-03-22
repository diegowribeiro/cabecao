# Estratégia LinkedIn — Autoridade Técnica e Liderança
> Audiência principal: C-levels, VPs de Engenharia, líderes técnicos, founders tech, liderança de produto e dados
> Objetivo: autoridade + contribuição real para a comunidade — sem expor negócio, clientes ou vulnerabilidades
> Tom: direto, denso em valor, baseado em experiência vivida — não em teoria

---

## Princípios de Conteúdo

1. **Generalizar sem perder profundidade** — os aprendizados são universais, os detalhes internos ficam fora
2. **Dado ou experiência em toda publicação** — nada genérico. Cada post tem uma âncora real
3. **Posicionar o leitor, não a empresa** — o conteúdo serve quem lê, não promove onde você trabalha
4. **Consistência > viralidade** — 2 posts por semana por 6 meses constroem mais do que 1 viral isolado
5. **Artigos aprofundam, posts provocam** — use posts para abrir conversas, artigos para fechar argumentos

---

## Posicionamento Central

> *"CTO de fintech que opera no cruzamento de engenharia, regulatório, IA e negócio — e compartilha os bastidores disso."*

Você não é mais um executivo falando de tendências.
Você é o cara que **implementou** e **errou** e **consertou** — e pode contar como.

---

## Séries e Publicações

---

### SÉRIE 1 — IA como alavanca de liderança técnica
> *Audiência: CTOs, VPs, founders, líderes de engenharia*
> *Objetivo: posicionar você como referência em uso real de IA no trabalho de CTO*

**[POST] "A maioria dos CTOs usa IA como assistente. Eu uso como sistema operacional."**
- A diferença entre usar IA para responder perguntas vs usá-la para operar
- Como estruturei contexto persistente que carrega quem eu sou, quais são as regras críticas do negócio, como quero ser comunicado
- Resultado: context switch de minutos para segundos entre 8 domínios técnicos diferentes
- *Gancho:* "Quando você para de perguntar para a IA e começa a briefar ela, tudo muda."

**[POST] "Construí um manual de mim mesmo para a IA. Aqui está o que aprendi."**
- Como um arquivo de configuração bem feito multiplica a qualidade de qualquer output
- O que precisa estar nesse contexto: quem você é, como você pensa, o que nunca pode acontecer
- Por que líderes técnicos deveriam ter isso antes de qualquer prompt sofisticado
- *Gancho:* "Você não tem um problema de prompt. Tem um problema de contexto."

**[ARTIGO] "Como estruturei um knowledge base de 300+ documentos para virar o maior ativo de IA da empresa"**
- A decisão de documentar de forma estruturada para consumo por IA (não para humanos)
- Dual schema: por que o mesmo arquivo precisa servir tanto para leitura humana quanto para RAG
- O processo de curar 15 sistemas em docs indexáveis — o que inclui, o que corta
- O pivot de portal web para skill de IA: o que muda quando o consumidor principal é um modelo
- *Sem mencionar empresa, produto ou dado interno*

**[POST] "Depois de montar o stack de IA mais avançado que eu já vi num executivo técnico, aprendi isso."**
- MCPs como extensões de capacidade (não de conveniência)
- A diferença entre ferramentas conectadas e ferramentas integradas
- O que nenhum tutorial de IA conta: o custo de manutenção de contexto distribuído
- *Tom:* honesto sobre o que não funcionou também

**[CARROSSEL] "7 formas que CTOs realmente usam IA no trabalho — além de 'escrever código'"**
1. Briefing técnico antes de reunião executiva
2. Análise de PR com contexto de negócio injetado
3. Rascunho de decisões de arquitetura com trade-offs
4. Triagem de incidentes com histórico de sistema como contexto
5. Síntese de Slack/Notion para decisão em menos de 5 min
6. Documentação de sistemas como pipeline — não como tarefa
7. Post-mortem estruturado em tempo real durante incidente

---

### SÉRIE 2 — Engenharia de produtos financeiros: bastidores
> *Audiência: líderes técnicos de fintech, VPs de produto, engenheiros sênior, founders de fintech*
> *Objetivo: mostrar o que é diferente de construir software financeiro — e por quê importa*

**[POST] "Software financeiro não falha. Ele falha de formas que destroem usuários. É diferente."**
- Por que engenharia financeira exige uma camada extra de paranoia
- Idempotência como cultura, não como técnica
- O que acontece quando um sistema de pagamento retorna um estado ambíguo — e por que isso é o pior cenário
- *Sem mencionar produto, cliente ou número interno*

**[POST] "Regulatório não é burocracia. É constraint de arquitetura."**
- Como requisitos de BACEN, COAF, PCI-DSS moldam decisões de sistema antes do código
- Por que decisões de compliance são decisões de produto — e precisam entrar no backlog assim
- A mentalidade que muda tudo: compliance como invariante, não como checklist de fim de sprint
- *Tom:* provocativo para quem trata compliance como afterthought

**[ARTIGO] "O que aprendi construindo sobre o PIX: o protocolo mais bem-sucedido de infraestrutura pública de pagamentos do mundo"**
- Arquitetura do ecossistema: o que é interno, o que é externo (JDPI, DICT)
- Por que latência em milissegundos importa diferente em pagamentos do que em outros produtos
- O que significa construir resiliência quando a janela de manutenção do Banco Central é domingo às 00h
- Padrões de circuit breaker e timeout que qualquer engenheiro de pagamentos precisa conhecer
- *Nível: educativo. Nada de arquitetura interna.*

**[POST] "Por que eu tenho 8 repositórios com stacks diferentes — e por que isso é uma decisão, não um acidente."**
- Monólito + Lambdas + Go + Terraform: como cada escolha surgiu de um problema real
- O custo real de heterogeneidade de stack (onboarding, contexto, incidentes)
- O custo real de uniformidade forçada (velocidade, fit técnico, time to market)
- A pergunta que você deveria fazer antes de padronizar: padronizar para quem?

**[CARROSSEL] "5 decisões de arquitetura que parecem técnicas mas são de negócio"**
1. Escolha de mensageria: garantia de entrega afeta SLA de contrato
2. Idempotência no processamento: é jurídico, não só técnico
3. Timeout de integração: quem absorve o risco no silêncio?
4. Schema de banco de dados: mudança de coluna pode ser mudança de produto
5. Circuit breaker: é política de relacionamento com parceiro, não só engenharia

---

### SÉRIE 3 — Gestão de complexidade em escala
> *Audiência: C-levels, VPs, líderes técnicos sênior, founders em escala*
> *Objetivo: posicionar você como alguém que opera e pensa em sistemas complexos — não só código*

**[POST] "Você não tem um problema de documentação. Tem um problema de quem é o consumidor da documentação."**
- Documentação para humano ≠ documentação para IA ≠ documentação para regulador
- Por que a maioria dos knowledge bases falha: escrito para ninguém específico
- O que muda quando você decide quem vai ler antes de escrever a primeira linha
- *Âncora: aprendizado real de construir 300+ docs estruturados*

**[POST] "Migrei um pipeline de dados crítico de região AWS sem parar a operação. Aqui estão os 3 erros que quase me quebraram."**
- Framing: lições de uma migração complexa, sem expor nada interno
- Erro 1: assumir que o mapa de recursos estava correto (não estava)
- Erro 2: subestimar dependências de schema que não estavam no código
- Erro 3: confiar em triggers automatizados sem validar o timing
- *100% transferível. Zero dado interno.*

**[ARTIGO] "Zero-downtime em sistemas críticos: o que ninguém conta sobre rotação de credenciais em produção"**
- O problema: você precisa trocar uma senha de produção sem derrubar nada
- A solução: dual-secret com fallback — conceito, não implementação específica
- O processo: como validar em ambiente de homologação antes de produção
- O que aprender disso para qualquer rotação de secret, chave ou certificado
- *Educativo, aplicável a qualquer empresa. Sem mencionar sistema interno.*

**[POST] "Schema drift silencioso quebra pipelines às 22h do sábado. Como você se defende disso."**
- O que é schema drift e por que é difícil de detectar antes de quebrar
- Por que o problema estava no código há meses e ninguém sabia
- Como estruturar validação de contrato de dados como etapa de deploy, não de incidente
- *Tom:* post-mortem educativo. Qualquer time de dados já passou por isso.

**[CARROSSEL] "6 coisas que só aparecem quando você migra infraestrutura legada"**
1. O recurso que ninguém lembra que existe até quebrar
2. A dependência que está em comentário de código, não em código
3. O job que roda todo mês e só o time de faturamento sabe
4. O bucket que nunca foi criado porque o código nunca chegou a esse path
5. A credencial que foi compartilhada entre dois sistemas sem documentação
6. O trigger que disparou no horário errado no dia da migração

---

### SÉRIE 4 — Segurança como cultura, não como time
> *Audiência: C-levels, CISOs, líderes de produto, VPs de engenharia*
> *Objetivo: posicionar como alguém que pensa segurança de forma sistêmica, não reativa*

**[POST] "Threat intelligence chegou. Em menos de 2 horas, a gente sabia se era real ou não. Aqui está o framework."**
- Como estruturar uma investigação rápida de suposta exposição de credenciais
- O que analisar primeiro (o que tem maior impacto potencial)
- Falso positivo vs verdadeiro positivo: sinais práticos de distinção
- O que fazer enquanto investiga — ação cautelar, não paralisação
- *Sem mencionar o alerta, a fonte ou qualquer detalhe da Iugu*

**[POST] "39 milhões de secrets expostos no GitHub em 2024. O que isso diz sobre como desenvolvemos software."**
- Os dados públicos são assustadores — use-os como âncora
- O problema não é o desenvolvedor que expôs. É o sistema que permitiu.
- Três camadas de defesa que qualquer empresa precisa ter antes de acontecer
- *Educativo. Dados públicos de pesquisa. Zero exposição interna.*

**[ARTIGO] "Como construir um programa de segurança ofensiva sem um time de segurança dedicado"**
- O argumento: você não pode esperar ter CISO para começar a pensar em segurança
- Monitoramento de exposição (GitHub, paste sites, breach DBs) como cultura
- Como transformar uma investigação em processo — não em heroísmo de plantão
- O mindset de "secure by default" em vez de "seguro depois de incidente"
- *Completamente genérico. Altíssimo valor para qualquer startup/scaleup.*

**[POST] "IAM com chave estática vs OIDC. Parece detalhe técnico. É decisão de risco."**
- Credentials estáticas: o que fica para trás quando o dev sai da empresa
- OIDC: credencial que expira, é rastreável, não existe no repositório
- Por que a migração vale o esforço — e o que você precisa mudar no processo
- *Educativo, aplicável a qualquer empresa com GitHub Actions/CI*

---

### SÉRIE 5 — Decisões de liderança técnica
> *Audiência: C-levels, founders, VPs — quem toma decisão, não só quem implementa*
> *Objetivo: mostrar que você pensa além de código — negócio, time, risco, estratégia*

**[POST] "A decisão técnica mais importante que um CTO toma não é de tecnologia."**
- É a decisão de o que documentar, o que manter como conhecimento tácito e o que formalizar como processo
- Conhecimento tácito em fintech mata empresas: churn de engenheiro = perda de domínio regulatório
- Como estruturar o "conhecimento da empresa" como ativo — não como consequência de documentar

**[POST] "Monólito vs microserviços: a pergunta errada. A pergunta certa é outra."**
- O que importa não é o padrão arquitetural, é o modelo de propriedade e operação
- Times pequenos em microserviços complexos: o pior dos mundos
- A decisão que você precisa tomar antes de escolher arquitetura

**[ARTIGO] "O que eu aprendi depois de 1 ano estruturando o conhecimento técnico da empresa"**
- Por que isso foi uma das iniciativas de maior retorno que executei
- O efeito no onboarding de novos engenheiros
- O efeito em incidentes: tempo de resposta menor com contexto acessível
- O efeito inesperado: IA como colega que entende o negócio
- *Posiciona o Cortex sem citar nome/empresa. O aprendizado é universal.*

**[POST] "Você contrata engenheiro ou conhecimento de domínio? São coisas diferentes."**
- Em fintech, o custo de onboarding de domínio é maior que o de stack
- Como isso muda o que você busca numa entrevista
- Como isso muda o que você faz nos primeiros 90 dias do engenheiro

**[CARROSSEL] "O que um CTO de fintech lê toda semana — e por quê"**
- Regulatório (comunicados BACEN, COAF)
- Threat intelligence (GitHub exposure reports, CISA advisories)
- Arquitetura distribuída (papers, post-mortems de grandes players)
- Produto financeiro (relatórios ABECS, BCB, Pix stats)
- Engenharia de ML aplicada (não teoria — papers de produção)

---

## Formatos e Cadência

### Formatos por tipo de impacto

| Formato | Quando usar | Alcance esperado |
|---|---|---|
| **Post curto (< 1.500 chars)** | Insight único, provocação, gancho | Alto — algoritmo favorece |
| **Carrossel (PDF 6–10 slides)** | Frameworks, listas, processos visuais | Alto — salvo, compartilhado |
| **Artigo LinkedIn** | Aprofundamento, cases, tutoriais | Médio — buscável, durável |
| **Post narrativo** | Storytelling de decisão ou incidente | Alto quando bem escrito |

### Cadência recomendada

```
Semana 1  → Post curto (gancho IA/CTO) + Carrossel (7 formas reais de usar IA)
Semana 2  → Post narrativo (migração ou incidente) + Artigo (knowledge base)
Semana 3  → Post curto (fintech/regulatório) + Post (segurança)
Semana 4  → Carrossel (decisões de arquitetura = decisões de negócio) + Artigo
...repete com novos temas das séries
```

**Meta: 2 publicações/semana por 3 meses** = ~25 publicações. Suficiente para estabelecer ritmo e posicionamento antes de escalar.

---

## O que nunca publicar

- Nomes de sistemas internos, clientes, parceiros, adquirentes
- Números de negócio (receita, volume, base de usuários)
- Vulnerabilidades específicas — mesmo que corrigidas
- Detalhes de arquitetura que mapeiem superfície de ataque
- Credenciais, endpoints, IDs de sistema — mesmo em exemplo
- Situações em que a empresa sai mal — mesmo anonimizadas com detalhes rastreáveis
- Decisões que exponham conflitos com regulador, parceiro ou time

> **Regra prática:** antes de publicar, pergunte — *"se o BACEN, um concorrente ou um atacante ler isso, algum dano é possível?"*. Se sim, reescreve.

---

## Temas evergreen para artigos longos (alta durabilidade)

1. *Como construir cultura de segurança sem time de segurança*
2. *O que ninguém conta sobre operar pagamentos no Brasil*
3. *Por que documentação técnica falha — e como estruturar para não falhar*
4. *IA como ferramenta de liderança: do hype à operação real*
5. *O custo invisível de stack heterogêneo — e quando vale a pena*
6. *Como migrar infra crítica sem parar operação: o que eu aprendi na prática*
7. *Zero-downtime em sistemas financeiros: padrões que funcionam*
8. *Como o PIX mudou a engenharia de pagamentos no Brasil*

---

## Métricas de sucesso (6 meses)

- **Alcance:** crescimento consistente de impressões por publicação
- **Conexões qualificadas:** CTOs, VPs, founders em fintech/tech
- **Inbound:** convites para falar, consultar, mentorar — são o sinal real de autoridade
- **Engajamento real:** comentários de pessoas do setor, não só likes
- **Referência:** ser citado em posts de outras pessoas como fonte

> Autoridade não se mede em seguidores. Se mede em quem te cita quando não está falando com você.

---

*Criado em 2026-03-22 — estratégia para LinkedIn focado em liderança técnica, C-level e contribuição para comunidade*
