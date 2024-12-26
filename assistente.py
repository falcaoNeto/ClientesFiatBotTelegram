from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains.conversation.base import ConversationChain
from bd import bd_pool
from dotenv import load_dotenv

load_dotenv()
memoria = ConversationBufferWindowMemory(k=5)

def get_llm():
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    return llm
 
def assistente_geral(question):  
    if question[0] == "0" or question[0] == "1":
        resposta = gerar_resposta_inicio(question)
        return resposta
    resp = tipo_pergunta(question)
    tipo = resp.strip()  
    
    if tipo == "CONVERSA":
        resposta = gerar_resposta(question)
        return resposta
    elif tipo == "CONFIGURACAO":
        resposta = gerar_resp_confg(question)
        return resposta
    else:
        queryResposta = gerar_query(question)
        try:
            prompt = PromptTemplate.from_template(
    template="""
        Você é um assistente virtual para os funcionários de uma loja da Fiat, com acesso a um banco de dados. 
        Seu objetivo é analisar o histórico de conversas fornecido e o input no formato (pergunta//resultado da query) do funcionário, 
        para formular uma resposta clara, estruturada e otimizada para o Telegram.
        Regras de formatação:
        - Divida a resposta em seções claras e organizadas.
        - Use marcadores e listas para facilitar a leitura.
        - Nao coloque asteriscos para marcar, pois não é compatível com o Telegram.
        - Converta números de telefone em links clicáveis para o WhatsApp (exemplo: https://wa.me/55[telefone]).
        - Use emojis para destacar informações importantes (exemplo: 📞 para telefone, 📅 para datas, etc.).
        - Nunca inclua a query SQL ou detalhes técnicos na resposta.
        Utilize as informações disponíveis na sessão apenas se forem relevantes para responder à solicitação.
        ### Histórico de Conversas:  
        {history}
        ### Pergunta do Funcionário e Resultado da Query:  
        {input}
        - Se o input vier ALTERA/DELETA, diga ooperacoes de alteração e exclusão sao realizadas somente no site https://clientesfiat.onrender.com/
        Formule uma resposta estruturada e direta que atenda à solicitação do funcionário de forma eficiente.
    """
)      
            chain = ConversationChain(
                llm=get_llm(),
                memory=memoria,
                prompt=prompt
            ) 
            pergunta = f'{question}//{queryResposta}'
            resposta = chain.predict(input=pergunta)    
            return resposta
        except Exception as e:
            return f"Erro ao acessar a LLM: {str(e)}"
    
def gerar_query(question):
    try:
        prompt = PromptTemplate.from_template(
    template="""
        Gere apenas uma query SQL, sem usar markdown, para o banco de dados PostgreSQL, baseada na pergunta abaixo:
        {input}
        Contexto da conversa:
        {history}
        Estrutura das tabelas:
        - **Funcionario**: (id_func, cpf, nome, senha)
        - **Cliente**: (id_clien, id_funcionario, nome, cpf, telefone, nome_conjuge, data_nascimento, data_casamento, data_aniver_conjuge, data_compra, revisoes_pendentes, data_ultima_revisao)
        - **Filho**: (id_filho, id_cliente, nome, data_nascimento)
        Notas importantes:
        - Se for um query que **altera** ou **deleta** alguma coisa do BD, retorne apenas: ALTERA/DELETA
        - Ignore o conteúdo da sessão, mas inclua-o na resposta exatamente como recebido na pergunta.
        - Use **apenas** as tabelas fornecidas.
        - Considere que clientes solteiros possuem `nome_conjuge = 'Solteiro(a)'`.
        - Se um CPF for informado no formato `00000000000`, transforme-o para o formato `000.000.000-00`.
    """
)

        
        chain = ConversationChain(
            llm=get_llm(),
            memory=memoria,
            prompt=prompt
        )
        
        resposta = chain.predict(input=question)
        
        query = resposta.strip()
        print(query)
        connect = bd_pool.getconn()
        cursor = connect.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        if cursor:
            cursor.close()
        if connect:
            bd_pool.putconn(connect)

def tipo_pergunta(question):
    prompt = PromptTemplate.from_template(
    template="""
        Regras de resposta:
        - Se a pergunta aparentar requerer uma consulta ao banco de dados (BD), retorne apenas: CONSULTA.
        - Se a pergunta não precisar de uma consulta ou se a informação na sessão responder à questão, retorne apenas: CONVERSA.
        - Se o usuário desejar trocar de usuário ou ajustar o horário das verificações/alertas diários, retorne apenas: CONFIGURACAO.
        - Ignore o conteúdo da sessão, mas inclua-o na resposta exatamente como recebido na pergunta.
        Contexto da conversa:
        {history}
        Pergunta do usuário:
        {input}
    """
)

    chain = ConversationChain(
        llm=get_llm(),
        memory=memoria,
        prompt=prompt,
        verbose=True
    )
    resposta = chain.predict(input=question)
    return resposta

def gerar_resposta(question):
    prompt = PromptTemplate.from_template(
    template="""
        Você é um assistente virtual exclusivo para funcionários de uma loja da Fiat. 
        Sua tarefa é ser gentil e eficiente, ajudando no que for necessário.
        Diretrizes:
        - Utilize as informações da sessão apenas se forem relevantes para a solicitação do usuário.
        - Nunca compartilhe diretamente o conteúdo da sessão.
        - Nunca inclua queries SQL na resposta ao usuário.
        - Mantenha suas respostas diretas e objetivas, sem perder a cordialidade.
        Contexto da conversa:
        {history}
        Pergunta do funcionário:
        {input}
    """
)

    
    chain = ConversationChain(
        llm=get_llm(),
        memory=memoria,
        prompt=prompt,
    )
    
    resposta = chain.predict(input=question)  
    return resposta

def formatar_dados(dados):
    prompt = PromptTemplate.from_template(
    template="""
        {history}
        Todos os dias você recebe uma lista de alertas para verificação.
        Regras de formatação:
        - Estruture as informações em seções claras e organizadas para facilitar a leitura no Telegram.
        - Nao coloque asteriscos para marcar, pois não é compatível com o Telegram.
        - Utilize emojis para destacar informações importantes (exemplo: 👤 para nomes, 📞 para telefones, 📅 para datas, etc.).
        - Converta números de telefone em links clicáveis para o WhatsApp (exemplo: https://wa.me/55[phone]).
        - Caso não haja alertas, responda apenas: "Hoje não houve alertas de verificação."
        - Liste cada alerta de forma separada, numerando ou utilizando marcadores para identificação.

        Dados recebidos (um dicionário com tipos de verificação como chaves e respostas como valores):
        {input}
    """
)
    chain = ConversationChain(
        llm=get_llm(),
        memory=memoria,
        prompt=prompt
    )
    resposta = chain.predict(input=dados)
    return resposta

def gerar_resp_confg(question):
    prompt = PromptTemplate.from_template(
    template="""
    Sempre o usuário quiser saber sobre, instrua da seguinte forma:
    - Para trocar de usuário, clique em /start.
    - Para alterar o horário, clique em /definirHorario.
    Utilize as informações da sessão apenas se forem solicitadas pelo usuário e relevantes para a resposta.
    Regras:
    - Nao passe a sessão diretamente, apenas as informacoes nela.
    - Nunca inclua queries SQL diretamente na resposta ao usuário.
    - Responda de forma clara, natural e amigável, considerando o contexto abaixo.
    Contexto da conversa:
    {history}
    Pergunta do usuário:
    {input}
    """
)
    
    chain = ConversationChain(
        llm=get_llm(),
        memory=memoria,
        prompt=prompt
    )
    
    resposta = chain.predict(input=question)  
    return resposta

def gerar_resposta_inicio(question):
    prompt = PromptTemplate.from_template(
    template="""
    O input vem no formato "0" ou "1" // sessao
    Você é um assistente virtual para uma loja da Fiat, exclusivamente para funcionários. Seja cortês e direto.
    Se receber 1, o CPF está validado e o funcionário está cadastrado. Diga as boas-vindas com o nome do funcionário icluso sa sessao e informe que é um assistente virtual.
    Se receber 0, peça para o funcionário informar o CPF corretamente.
    Utilize a sessão (informações do usuário) para personalizar a resposta, se necessário.Nunca passe a sessão diretamente, apenas as informações nela.
    {history}
    human:
    {input}
    """
)    
    chain = ConversationChain(
        llm=get_llm(),
        memory=memoria,
        prompt=prompt
    ) 
    resposta = chain.predict(input=question)  
    return resposta

if __name__ == "__main__":
    pass