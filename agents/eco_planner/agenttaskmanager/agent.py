from google.adk.agents.llm_agent import Agent
from trello import TrelloClient
from dotenv import load_dotenv
from datetime import datetime
import unicodedata
import os

load_dotenv()

# Suas credenciais
API_KEY = os.getenv('TRELLO_API_KEY')
API_SECRET = os.getenv('TRELLO_API_SECRET')
TOKEN = os.getenv('TRELLO_TOKEN')

STATUS_LIST_ALIASES = {
    'a fazer': ('A FAZER', 'TO DO', 'TODO', 'BACKLOG', 'PENDENTE', 'PENDENTES'),
    'em andamento': ('EM ANDAMENTO', 'DOING', 'IN PROGRESS', 'ANDAMENTO', 'FAZENDO'),
    'concluido': ('CONCLUIDO', 'CONCLUÍDO', 'DONE', 'FINALIZADO', 'FINALIZADA'),
}


def _normalize_text(value: str) -> str:
    normalized = unicodedata.normalize('NFKD', value or '')
    without_accents = ''.join(char for char in normalized if not unicodedata.combining(char))
    return ' '.join(without_accents.upper().split())


def _get_board(client: TrelloClient, board_name: str):
    boards = client.list_boards()
    return next((board for board in boards if _normalize_text(board.name) == _normalize_text(board_name)), None)


def _get_list_by_names(lists, *possible_names: str):
    normalized_names = {_normalize_text(name) for name in possible_names}
    return next((item for item in lists if _normalize_text(item.name) in normalized_names), None)


def get_temporal_context():
    now = datetime.now()
    return now.strftime('%Y/%m/%d %H:%M:%S')


def adicionar_tarefa(nome_da_task: str, descricao_da_task: str, due_date: str) -> str:
    try:
        client = TrelloClient(
            api_key=API_KEY,
            api_secret=API_SECRET,
            token=TOKEN
        )

        meu_board = _get_board(client, 'DIO')
        if not meu_board:
            return "❌ Board 'DIO' não encontrado. Verifique o nome do board no Trello."

        listas = meu_board.list_lists()
        minha_lista = _get_list_by_names(listas, *STATUS_LIST_ALIASES['a fazer'])

        if not minha_lista:
            nomes_listas = ', '.join(lista.name for lista in listas) or 'nenhuma lista encontrada'
            return (
                "❌ Nenhuma lista de entrada foi encontrada no board 'DIO'. "
                f"Listas disponíveis: {nomes_listas}. "
                "Crie ou renomeie uma lista para uma coluna de entrada, como 'A FAZER', 'TO DO' ou 'TODO'."
            )

        minha_lista.add_card(
            name=nome_da_task,
            desc=descricao_da_task,
            due=due_date
        )
        return f"✅ Tarefa '{nome_da_task}' criada na lista '{minha_lista.name}'."
    except Exception as error:
        return f"❌ Erro ao adicionar tarefa: {str(error)}"

def listar_tarefas(status: str = "todas"):
    client = TrelloClient(
        api_key=API_KEY,
        api_secret=API_SECRET,
        token=TOKEN
    )

    meu_board = _get_board(client, 'DIO')
    if not meu_board:
        return [{"erro": "Board 'DIO' não encontrado."}]

    listas = meu_board.list_lists()        

    if status.lower() == "todas":
        listas_filtradas = listas
    elif status.lower() in STATUS_LIST_ALIASES:
        nomes_status = {_normalize_text(name) for name in STATUS_LIST_ALIASES[status.lower()]}
        listas_filtradas = [l for l in listas if _normalize_text(l.name) in nomes_status]
    else:
        listas_filtradas = listas

    tarefas = []

    for lista in listas_filtradas:
        cards = lista.list_cards()
        for card in cards:
            tarefas.append({
                "nome": card.name,
                "descricao": card.desc,
                "vencimento": card.due,
                "status": lista.name,
                "id": card.id
            })
    
    return tarefas

def mudar_status_tarefa(nome_da_task: str, novo_status: str) -> str:
    try:
        client = TrelloClient(
            api_key=API_KEY,
            api_secret=API_SECRET,
            token=TOKEN
        )

        meu_board = _get_board(client, 'DIO')
        if not meu_board:
            return "❌ Board 'DIO' não encontrado. Verifique o nome do board no Trello."

        listas = meu_board.list_lists()
                       
        status_key = novo_status.lower()

        if status_key not in STATUS_LIST_ALIASES:
            return f"❌ Status inválido. Use: 'a fazer', 'em andamento' ou 'concluido'"
        
        # Encontrar lista de destino
        lista_destino = _get_list_by_names(listas, *STATUS_LIST_ALIASES[status_key])

        if not lista_destino:
            nomes_listas = ', '.join(lista.name for lista in listas) or 'nenhuma lista encontrada'
            return (
                f"❌ Nenhuma lista compatível com o status '{novo_status}' foi encontrada no board. "
                f"Listas disponíveis: {nomes_listas}."
            )
        
         # Buscar card em todas as listas
        card_encontrado = None
        lista_origem = None

        for lista in listas:
            cards = lista.list_cards()
            card_encontrado = next(
                (c for c in cards if c.name.lower() == nome_da_task.lower()), 
                None
            )
            if card_encontrado:
                lista_origem = lista
                break
        
        if not card_encontrado:
            return f"❌ Card '{nome_da_task}' não encontrado"
        
        # Mover
        card_encontrado.change_list(lista_destino.id)
        return f"✅ '{nome_da_task}': {lista_origem.name} → {lista_destino.name}"
    except Exception as e:
        return f"❌ Erro: {str(e)}"

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='Agente de Organização de Tarefas',
    instruction="""
        Você é um agente de organização de tarefas.     
        Sua função é receber uma tarefa e criar um card no Trello com o nome e descrição da tarefa.
        Você deve me perguntar as atividas que tenho no dia e criar um card para cada uma delas.
        Você inicia a conversa assim que for ativado, perguntando quais são as tarefas do dia.
        Sempre inicie a conversa perguntando quais são as tarefas do dia informando a data com pela tool get_temporal_context, 
        e depois vá perguntando se tem mais alguma tarefa, até que o usuário diga que não tem mais tarefas.
        Suas funções:
         1. Adicionar novas tarefas com nome e descrição
          2. Listar todas as tarefas ou filtrar por status
          3. Marcar tarefas como concluídas
          4. Remover tarefas da lista
          5. Mudar o status da tarefa (ex: de "A Fazer" para "Em Andamento" e de "Em Andamento" para "Concluído")
          6. Gerar contexto temporal (data e hora atual) para organizar as tarefas do dia
""",
    tools=[get_temporal_context, adicionar_tarefa, listar_tarefas, mudar_status_tarefa],
)