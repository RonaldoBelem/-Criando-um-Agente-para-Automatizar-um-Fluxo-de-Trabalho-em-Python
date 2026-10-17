import re
from enum import Enum
from typing import Union, Annotated

from pydantic import BaseModel, AfterValidator, ConfigDict


def trello_id_validator(trello_id: str) -> str:
    expr = re.compile('^[0-9a-fA-F]{24}$')
    if not expr.fullmatch(trello_id):
        raise ValueError(f"Id {trello_id} is not a valid id (doesn't match ^[0-9a-fA-F]{24}$ expression)")
    return trello_id


def _to_camel(alias_source: str) -> str:
    """Convert snake_case to camelCase; return as-is if already camelCase."""
    if '_' not in alias_source:
        return alias_source
    parts = alias_source.split('_')
    return parts[0] + ''.join(p.capitalize() for p in parts[1:])

class TrelloMemberTypes(str, Enum):
    ADMIN = 'admin'
    NORMAL = 'normal'
    OBSERVER = 'observer'


class TrelloCollaborator(BaseModel):
    email: str
    type: TrelloMemberTypes = TrelloMemberTypes.NORMAL


class TrelloCollaborators(BaseModel):
    collaborators: list[TrelloCollaborator]


class TrelloBoardCreate(BaseModel):
    name: str | None = None
    desc: str | None = None


class TrelloBoardDetails(BaseModel):
    id: Annotated[str, AfterValidator(trello_id_validator)]
    name: str
    desc: str | None = None
    url: str


class TrelloListCreate(BaseModel):
    name: str
    idBoard: Annotated[str, AfterValidator(trello_id_validator)]
    idListSource: Annotated[str, AfterValidator(trello_id_validator)] | None = None
    pos: str | float | None = None


class TrelloListUpdate(BaseModel):
    name: str | None = None
    closed: bool | None = None
    idBoard: Annotated[str , AfterValidator(trello_id_validator)] | None = None
    pos: str | float | None = None
    subscribed: bool | None = None


class TrelloListDetails(BaseModel):
    id: str
    name: str | None = None
    closed: bool | None = None
    idBoard: Annotated[str , AfterValidator(trello_id_validator)] | None = None
    pos: str | float | None = None
    subscribed: bool | None = None
    color: str | None = None
    softLimit: str | None = None
    type: str | None = None
    datasource: dict | None = None


class TrelloCardUpdate(BaseModel):
    # Allow snake_case input while emitting camelCase when by_alias=True
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)
    name: str | None = None
    desc: str | None = None
    pos: str | float | None = None
    url: str | None = None
    due: str | None = None
    start: str | None = None
    dueComplete: bool | None = None
    idList: Annotated[str , AfterValidator(trello_id_validator)] | None = None
    idMembers: list[Annotated[str , AfterValidator(trello_id_validator)]] | None = None
    idLabels: list[Annotated[str , AfterValidator(trello_id_validator)]] | None = None
    urlSource: str | None = None
    fileSource: str | None = None
    mimeType: str | None = None
    idCardSource: Annotated[str , AfterValidator(trello_id_validator)] | None = None
    keepFromSource: str | None = None
    address: str | None = None
    locationName: str | None = None
    coordinates: str | None = None


class TrelloCommentDetails(BaseModel):
    id: Annotated[str, AfterValidator(trello_id_validator)]
    idMemberCreator: Annotated[str, AfterValidator(trello_id_validator)]
    data: dict
    date: str
    type: str
    memberCreator: dict | None = None


class TrelloCommentCreate(BaseModel):
    text: str


class TrelloCommentUpdate(BaseModel):
    text: str


class TrelloCardCreate(BaseModel):
    # Allow snake_case input while emitting camelCase when by_alias=True
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)
    name: str | None = None
    desc: str | None = None
    pos: str | float = "bottom"
    url: str | None = None
    due: str | None = None
    start: str | None = None
    dueComplete: bool = False
    idList: Annotated[str , AfterValidator(trello_id_validator)]
    idMembers: list[Annotated[str , AfterValidator(trello_id_validator)]] | None = None
    idLabels: list[Annotated[str , AfterValidator(trello_id_validator)]] | None = None
    urlSource: str | None = None
    fileSource: str | None = None
    mimeType: str | None = None
    idCardSource: Annotated[str , AfterValidator(trello_id_validator)] | None = None
    keepFromSource: str | None = None
    address: str | None = None
    locationName: str | None = None
    coordinates: str | None = None


class TrelloCheckItemDetails(BaseModel):
    id: Annotated[str , AfterValidator(trello_id_validator)]
    idChecklist: Annotated[str , AfterValidator(trello_id_validator)]
    name: str
    idChecklistSource: Annotated[str , AfterValidator(trello_id_validator)] | None = None
    nameData: dict | None = None
    pos: str | float | None = None
    state: str
    due: str | None = None
    due_reminder: str | None = None
    idMember: Annotated[str , AfterValidator(trello_id_validator)] | None


class TrelloCheckItemCreate(BaseModel):
    name: str
    pos: str | float | None = None
    checked: bool = False
    due: str | None = None
    dueReminder: str | None = None
    idMember: Annotated[str , AfterValidator(trello_id_validator)] | None = None


class TrelloCheckItemUpdate(BaseModel):
    name: str | None = None
    state: str | None = None
    due: str | None = None
    dueReminder: str | None = None


class TrelloCheckListDetails(BaseModel):
    id: Annotated[str , AfterValidator(trello_id_validator)]
    name: str
    idBoard: Annotated[str , AfterValidator(trello_id_validator)]
    idCard: Annotated[str , AfterValidator(trello_id_validator)]
    pos: str | float | None = None
    checkItems: list[TrelloCheckItemDetails]


class TrelloCardDetails(BaseModel):
    # Allow snake_case input while emitting camelCase when by_alias=True
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)
    # Core card fields
    id: Annotated[str , AfterValidator(trello_id_validator)]
    name: str | None = None
    desc: str | None = None
    pos: str | float = "bottom"
    url: str | None = None
    due: str | None = None
    start: str | None = None
    dueComplete: bool = False
    idList: Annotated[str , AfterValidator(trello_id_validator)] | None = None
    idMembers: list[Annotated[str , AfterValidator(trello_id_validator)]] | None = None
    idLabels: list[Annotated[str , AfterValidator(trello_id_validator)]] | None = None
    urlSource: str | None = None
    fileSource: str | None = None
    mimeType: str | None = None
    idCardSource: Annotated[str , AfterValidator(trello_id_validator)] | None = None
    keepFromSource: str | None = None
    address: str | None = None
    locationName: str | None = None
    coordinates: str | None = None
    # Extended fields
    comments: list[TrelloCommentDetails] = []
    checklists: list[TrelloCheckListDetails] = []
    # Badge-derived fields for quick access
    attachmentCount: int = 0
    checkItems: int = 0
    checkItemsChecked: int = 0
    idAttachmentCover: str | None = None


class TrelloCheckListCreate(BaseModel):
    idCard: Annotated[str , AfterValidator(trello_id_validator)]
    name: str
    idChecklistSource: Annotated[str , AfterValidator(trello_id_validator)] | None = None
    pos: str | float | None = None


class TrelloMemberDetails(BaseModel):
    id: Annotated[str , AfterValidator(trello_id_validator)]
    fullName: str
    username: str


class TrelloLabelDetails(BaseModel):
    id: Annotated[str, AfterValidator(trello_id_validator)]
    idBoard: Annotated[str, AfterValidator(trello_id_validator)]
    name: str
    color: str
    users: int = 0

class TrelloLabelCreate(BaseModel):
    name: str
    color: str
    idBoard: Annotated[str , AfterValidator(trello_id_validator)]


class TrelloAttachmentPreview(BaseModel):
    id: Annotated[str, AfterValidator(trello_id_validator)] | None = None
    url: str | None = None
    bytes: int | None = None
    height: int | None = None
    width: int | None = None
    scaled: bool | None = None


class TrelloAttachmentDetails(BaseModel):
    id: Annotated[str, AfterValidator(trello_id_validator)]
    name: str | None = None
    url: str
    bytes: int | None = None
    mimeType: str | None = None
    date: str | None = None
    isUpload: bool | None = None
    pos: str | float | None = None
    idMember: Annotated[str, AfterValidator(trello_id_validator)] | None = None
    previews: list[TrelloAttachmentPreview] | None = None


TrelloType = Union[TrelloBoardDetails | TrelloListDetails | TrelloCardDetails | TrelloCheckItemDetails | TrelloCheckListDetails | TrelloMemberDetails | TrelloLabelDetails | TrelloCommentDetails | TrelloAttachmentDetails | None]


