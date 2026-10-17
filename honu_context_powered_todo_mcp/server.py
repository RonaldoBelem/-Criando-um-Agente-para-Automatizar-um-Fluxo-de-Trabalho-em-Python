import asyncio
from pathlib import Path

from fastmcp import FastMCP
from fastmcp.server import create_proxy

from honu_context_powered_todo_mcp.schema import TrelloBoardDetails, TrelloBoardCreate, TrelloLabelCreate, \
    TrelloListCreate
from honu_context_powered_todo_mcp.settings import Settings
from honu_context_powered_todo_mcp.trello_client import TrelloClient

mcp = FastMCP('Honu Context-Powered ToDo Management')

DEFAULT_LABEL_LIST = {
    'Manual': 'black',
    'Feature': 'blue',
    'Bug': 'red',
    'Chore': 'yellow',
    'Tech Debt': 'orange',
    # Priority labels
    'Priority High': 'red',
    'Priority Medium': 'yellow',
    'Priority Low': 'green',
    # Stack labels
    'Frontend': 'purple',
    'Backend': 'pink',
    'Fullstack': 'lime',
    'DevOps': 'sky',
    'Needs Clarification': 'pink',
}
DEFAULT_LIST_NAMES = [
    'Sprint Descriptions',
    'Backlog',
    'To Do',
    'In Progress',
    'QA',
    'Done',
    'On Hold',
]


@mcp.tool
async def create_trello_board_for_business(business_name: str, business_context: str) -> TrelloBoardDetails:
    """
    Create a new Trello Board for a Business to use as a Project Management Board.
    The Business Context will be included in the Board Description for context-powered collaboration and running.
    :param business_name: The name of the business, will be used to create the board
    :param business_context: Business Contextual information to be stored with the board to power collaboration.
        This context information is limited to around 16,000 characters, and should contain as much information from the following list as possible;
            - User Journey Flow from Start to Finish
            - Definition of the Minimum Viable Product
            - Potential external Product Integrations for powering the product
    :return: The details of the created board, which will be set up to match the format outlined in the playbook
    """
    client = TrelloClient(Settings.TRELLO_API_KEY, Settings.TRELLO_API_TOKEN)
    payload = TrelloBoardCreate(name=business_name, desc=business_context)
    board = await client.create_board(payload)
    lists_to_delete = await client.get_lists(board.id)
    labels_to_delete = await client.get_labels(board.id)

    # Cleanup the default lists/labels
    async with asyncio.TaskGroup() as tg:
        for t_list in lists_to_delete:
            tg.create_task(client.delete_list(t_list.id))
        for t_label in labels_to_delete:
            tg.create_task(client.delete_label(t_label.id))

    # Create the required lists/labels concurrently after cleaning up the defaults
    async with asyncio.TaskGroup() as tg:
        for label, color in DEFAULT_LABEL_LIST.items():
            tg.create_task(
                client.create_label(
                    TrelloLabelCreate(
                        name=label,
                        color=color,
                        idBoard=board.id,
                    )
                )
            )
        for list_name in DEFAULT_LIST_NAMES:
            tg.create_task(
                client.create_list(
                    TrelloListCreate(
                        idBoard=board.id,
                        name=list_name,
                        pos='bottom',
                    )
                )
            )

    return board


@mcp.tool
async def get_trello_board_management_playbook() -> str:
    """
    Fetch the playbook by which to operate when managing the Trello board using the MCP servers
    :return: The Sprint Planning Playbook. Use the provided Trello MCP tools to manage Sprints in the Trello Board associated with the current business.
    """
    with open(Path(__file__).parent / 'playbook.md') as f:
        return f.read()


@mcp.tool
async def get_business_context(trello_board_id: str) -> dict[str, str]:
    """
    Fetch the Business Context to inform future decision making.
    :param trello_board_id: The ID of the Board to fetch the name and context for
    :return: The Business Name and Business Context associated with the Board
    """
    client = TrelloClient(Settings.TRELLO_API_KEY, Settings.TRELLO_API_TOKEN)
    board = await client.get_board(trello_board_id)
    return {'business_name': board.name, 'business_context': board.desc}


@mcp.tool
async def update_business_context(trello_board_id: str, new_business_context: str):
    """
    Update the stored Business Context for a Trello Board to a new value. This tool will replace the entire Business Context on the board with the provided one
    :param trello_board_id: The ID of the Board to update the Context for
    :param new_business_context: The new Business Context for the board.
    :return: Nothing if the update was successful
    """
    client = TrelloClient(Settings.TRELLO_API_KEY, Settings.TRELLO_API_TOKEN)
    payload = TrelloBoardCreate(desc=new_business_context)
    await client.update_board(trello_board_id, payload)


if __name__ == '__main__':
    trello_proxy = create_proxy({
        'mcpServers': {
            'trello': {
                'command': 'npx',
                'args': ['@delorenj/mcp-server-trello'],
                'env': {
                    'TRELLO_API_KEY': Settings.TRELLO_API_KEY,
                    'TRELLO_TOKEN': Settings.TRELLO_API_TOKEN,
                },
            },
        },
    })
    mcp.mount(trello_proxy)
    mcp.run()
