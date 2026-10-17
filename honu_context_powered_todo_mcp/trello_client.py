import logging
from typing import Type

import httpx
from starlette import status
from tenacity import retry, stop_after_attempt, retry_if_exception_type, before_sleep_log, \
    wait_random

from .schema import TrelloType, TrelloMemberDetails, TrelloCollaborator, \
    TrelloBoardDetails, TrelloBoardCreate, TrelloListDetails, TrelloListCreate, TrelloListUpdate, TrelloCardDetails, \
    TrelloCardCreate, \
    TrelloCardUpdate, TrelloCheckListDetails, TrelloCheckListCreate, TrelloCheckItemDetails, TrelloCheckItemCreate, \
    TrelloCheckItemUpdate, TrelloLabelDetails, TrelloLabelCreate, TrelloCommentDetails, TrelloCommentCreate, \
    TrelloCommentUpdate, TrelloAttachmentDetails

TIMEOUT = 120
logger = logging.getLogger(__name__)

# HTTP methods that require JSON data in request body
METHODS_WITH_JSON_BODY = {'post', 'put'}


class TrelloClientException(Exception):

    def __init__(self, response: httpx.Response):
        self.response = response

    def __str__(self):
        return f'Invalid response code {self.response.status_code} for url {self.response.url}.\n{self.response.text}'


class TrelloRateLimitReachedException(Exception):
    def __init__(self, response: httpx.Response):
        self.response = response
        # Trello returns milliseconds in x-rate-limit-api-token-interval-ms header
        # Convert to seconds for tenacity retry logic
        retry_after_ms = int(response.headers.get("x-rate-limit-api-token-interval-ms", "10"))
        self.retry_after_header = retry_after_ms / 1000  # Convert ms to seconds

    def __str__(self):
        return f'Rate limited, while requesting {self.response.url}, try again in : {self.retry_after_header} seconds'


class TrelloClient:

    def __init__(self, api_key: str, api_token: str):
        self.api_key = api_key
        self.api_token = api_token

    @property
    def client(self):
        params = {
            'key': self.api_key,
            'token': self.api_token,
        }
        return httpx.AsyncClient(
            base_url='https://api.trello.com',
            params=params,
            headers={
                'Content-Type': 'application/json',
            },
            timeout=TIMEOUT,
        )

    @retry(
        stop=stop_after_attempt(10),  # Increased from 5 to 10 attempts
        wait=wait_random(min=10, max=30),
        retry=retry_if_exception_type(TrelloRateLimitReachedException),
        reraise=True,  # Show the original exception, not RetryError
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    async def _make_raw_request(self, method: str, resource_url: str, params: dict = {}, data: dict = {}) -> dict | \
                                                                                                             list[dict]:
        """Make HTTP request and return raw JSON response with error handling."""
        async with self.client as client:
            if method.lower() in METHODS_WITH_JSON_BODY:
                response = await getattr(client, method)(resource_url, params=params, json=data)
            else:
                response = await getattr(client, method)(resource_url, params=params)

            if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                raise TrelloRateLimitReachedException(response)
            elif response.status_code != status.HTTP_200_OK:
                raise TrelloClientException(response)

            return response.json()

    async def _make_request(self, method: str, resource_url: str, response_type: Type[TrelloType], params: dict = {},
                            data: dict = {}) -> TrelloType | list[TrelloType] | None:
        """Make HTTP request and return typed response object."""
        mapped_response = await self._make_raw_request(method, resource_url, params, data)

        if response_type is None:
            return None
        if isinstance(mapped_response, list):
            return [response_type(**item) for item in mapped_response]
        return response_type(**mapped_response)

    async def delete_project(self, board_id: str) -> None:
        await self._make_request('delete', f'/1/boards/{board_id}', None)

    async def get_board_members(self, board_id: str) -> list[TrelloMemberDetails]:
        return await self._make_request('get', f'/1/boards/{board_id}/members', TrelloMemberDetails)

    async def invite_member(self, board_id: str, collaborator: TrelloCollaborator) -> None:
        params = {
            'email': collaborator.email,
            'type': collaborator.type.value,
        }
        await self._make_request('put', f'/1/boards/{board_id}/members', None, params=params)

    async def get_board(self, board_id: str) -> TrelloBoardDetails:
        return await self._make_request('get', f'/1/boards/{board_id}', TrelloBoardDetails)

    async def create_board(self, board_create_data: TrelloBoardCreate) -> TrelloBoardDetails:
        return await self._make_request('post', '/1/boards', TrelloBoardDetails,
                                        params=board_create_data.model_dump(exclude_none=True, by_alias=True))

    async def update_board(self, board_id: str, board_data: TrelloBoardCreate):
        return await self._make_request('put', f'/1/boards/{board_id}', TrelloBoardDetails,
                                        params=board_data.model_dump(exclude_none=True, by_alias=True))

    async def delete_board(self, board_id: str) -> None:
        await self._make_request('delete', f'/1/boards/{board_id}', None)

    async def get_lists(self, board_id: str) -> list[TrelloListDetails]:
        return await self._make_request('get', f'/1/boards/{board_id}/lists', TrelloListDetails)

    async def get_list(self, list_id: str) -> TrelloListDetails:
        return await self._make_request('get', f'/1/lists/{list_id}', TrelloListDetails)

    async def create_list(self, list_create_data: TrelloListCreate) -> TrelloListDetails:
        return await self._make_request('post', f'/1/lists', TrelloListDetails,
                                        params=list_create_data.model_dump(exclude_none=True, by_alias=True))

    async def update_list(self, list_id: str, list_update_data: TrelloListUpdate) -> TrelloListDetails:
        return await self._make_request('put', f'/1/lists/{list_id}', TrelloListDetails,
                                        params=list_update_data.model_dump(exclude_none=True, by_alias=True))

    async def delete_list(self, list_id: str) -> None:
        await self.update_list(list_id, TrelloListUpdate(closed=True))
        return await self._make_request('delete', f'/1/lists/{list_id}', None)

    async def get_cards(self, list_id: str) -> list[TrelloCardDetails]:
        # Get raw data to extract badge values
        cards_data = await self._make_raw_request('get', f'/1/lists/{list_id}/cards')

        # Handle both single card (test case) and array of cards (normal case)
        if isinstance(cards_data, dict):
            # Single card returned
            cards_data = [cards_data]

        # Process each card to extract badge values
        cards = []
        for card_data in cards_data:
            # Extract badge values for easy access
            if 'badges' in card_data:
                badges = card_data['badges']
                card_data['attachmentCount'] = badges.get('attachments', 0)
                card_data['checkItems'] = badges.get('checkItems', 0)
                card_data['checkItemsChecked'] = badges.get('checkItemsChecked', 0)

            # Extract cover attachment ID
            if 'idAttachmentCover' in card_data:
                card_data['idAttachmentCover'] = card_data['idAttachmentCover']

            cards.append(TrelloCardDetails(**card_data))

        return cards

    async def get_card(self, card_id: str, include_comments: bool = True,
                       include_checklists: bool = True) -> TrelloCardDetails:
        # Early exit: simple case with no special processing needed
        if not include_comments and not include_checklists:
            # Get raw data to extract badge values
            data = await self._make_raw_request('get', f'/1/cards/{card_id}')

            # Extract badge values for easy access
            if 'badges' in data:
                badges = data['badges']
                data['attachmentCount'] = badges.get('attachments', 0)
                data['checkItems'] = badges.get('checkItems', 0)
                data['checkItemsChecked'] = badges.get('checkItemsChecked', 0)

            # Extract cover attachment ID
            if 'idAttachmentCover' in data:
                data['idAttachmentCover'] = data['idAttachmentCover']

            return TrelloCardDetails(**data)

        # Build API parameters for enhanced data
        params = {}
        if include_comments:
            params['actions'] = 'commentCard'
        if include_checklists:
            params['checklists'] = 'all'

        # Get enhanced card data and let Pydantic handle the processing
        data = await self._make_raw_request('get', f'/1/cards/{card_id}', params)

        # Rename API field to match schema field name for automatic Pydantic processing
        if include_comments and 'actions' in data:
            data['comments'] = data.pop('actions')

        # Extract badge values for easy access
        if 'badges' in data:
            badges = data['badges']
            data['attachmentCount'] = badges.get('attachments', 0)
            data['checkItems'] = badges.get('checkItems', 0)
            data['checkItemsChecked'] = badges.get('checkItemsChecked', 0)

        # Extract cover attachment ID
        if 'idAttachmentCover' in data:
            data['idAttachmentCover'] = data['idAttachmentCover']

        # Pydantic automatically handles nested model conversion and defaults
        return TrelloCardDetails(**data)

    async def create_card(self, create_data: TrelloCardCreate) -> TrelloCardDetails:
        # Get raw data to extract badge values
        data = await self._make_raw_request('post', f'/1/cards',
                                            create_data.model_dump(exclude_none=True, by_alias=True))

        # Extract badge values for easy access
        if 'badges' in data:
            badges = data['badges']
            data['attachmentCount'] = badges.get('attachments', 0)
            data['checkItems'] = badges.get('checkItems', 0)
            data['checkItemsChecked'] = badges.get('checkItemsChecked', 0)

        # Extract cover attachment ID
        if 'idAttachmentCover' in data:
            data['idAttachmentCover'] = data['idAttachmentCover']

        return TrelloCardDetails(**data)

    async def update_card(self, card_id: str, card_update_data: TrelloCardUpdate) -> TrelloCardDetails:
        # Get raw data to extract badge values
        data = await self._make_raw_request('put', f'/1/cards/{card_id}',
                                            card_update_data.model_dump(exclude_none=True, by_alias=True))

        # Extract badge values for easy access
        if 'badges' in data:
            badges = data['badges']
            data['attachmentCount'] = badges.get('attachments', 0)
            data['checkItems'] = badges.get('checkItems', 0)
            data['checkItemsChecked'] = badges.get('checkItemsChecked', 0)

        # Extract cover attachment ID
        if 'idAttachmentCover' in data:
            data['idAttachmentCover'] = data['idAttachmentCover']

        return TrelloCardDetails(**data)

    async def get_checklists(self, card_id: str) -> list[TrelloCheckListDetails]:
        return await self._make_request('get', f'/1/card/{card_id}/checklists', TrelloCheckListDetails)

    async def get_checklist(self, checklist_id: str) -> TrelloCheckListDetails:
        return await self._make_request('get', f'/1/checklists/{checklist_id}', TrelloCheckListDetails)

    async def create_checklist(self, checklist_create_data: TrelloCheckListCreate) -> TrelloCheckListDetails:
        return await self._make_request('post', f'/1/checklist', TrelloCheckListDetails,
                                        params=checklist_create_data.model_dump(exclude_none=True, by_alias=True))

    async def get_check_items(self, checklist_id: str) -> list[TrelloCheckItemDetails]:
        return await self._make_request('get', f'/1/checklists/{checklist_id}/checkItems', TrelloCheckItemDetails)

    async def get_check_item(self, checklist_id: str, checkitem_id: str) -> TrelloCheckItemDetails:
        return await self._make_request('get', f'/1/checklist/{checklist_id}/checkItems/{checkitem_id}',
                                        TrelloCheckItemDetails)

    async def create_check_item(self, checklist_id: str,
                                check_item_create_data: TrelloCheckItemCreate) -> TrelloCheckItemDetails:
        return await self._make_request('post', f'/1/checklists/{checklist_id}/checkItems', TrelloCheckItemDetails,
                                        params=check_item_create_data.model_dump(exclude_none=True, by_alias=True))

    async def update_check_item(self, card_id: str, check_item_id: str,
                                check_item_update_data: TrelloCheckItemUpdate) -> TrelloCheckItemDetails:
        return await self._make_request('put', f'/1/cards/{card_id}/checkItem/{check_item_id}', TrelloCheckItemDetails,
                                        params=check_item_update_data.model_dump(exclude_none=True, by_alias=True))

    async def delete_check_item(self, checklist_id: str, checkitem_id: str) -> None:
        return await self._make_request('delete', f'/1/checklists/{checklist_id}/checkItems/{checkitem_id}', None)

    async def get_labels(self, board_id: str) -> list[TrelloLabelDetails]:
        return await self._make_request('get', f'/1/boards/{board_id}/labels', TrelloLabelDetails)

    async def get_label(self, label_id: str) -> TrelloLabelDetails:
        return await self._make_request('get', f'/1/labels/{label_id}', TrelloLabelDetails)

    async def delete_label(self, label_id: str) -> None:
        return await self._make_request('delete', f'/1/labels/{label_id}', None)

    async def create_label(self, label_create_data: TrelloLabelCreate) -> TrelloLabelDetails:
        return await self._make_request('post', f'/1/labels/', TrelloLabelDetails,
                                        params=label_create_data.model_dump(exclude_none=True, by_alias=True))

    async def get_members(self, board_id: str) -> list[TrelloMemberDetails]:
        return await self._make_request('get', f'/1/boards/{board_id}/members', TrelloMemberDetails)

    async def get_current_user(self) -> dict:
        """
        Get information about the current authenticated user (who_am_i function).
        Returns detailed user information including username, fullName, email, etc.
        """
        return await self._make_raw_request('get', '/1/members/me')

    async def label_card(self, card_id: str, label_id: str, remove: bool) -> TrelloCardDetails:
        card = await self.get_card(card_id)
        labels = card.idLabels
        new_labels = [label_id]
        if labels is not None:
            new_labels.extend(labels)
        new_labels = list(set(new_labels))
        if remove and label_id in new_labels:
            new_labels.remove(label_id)
        return await self.update_card(card_id, TrelloCardUpdate(idLabels=new_labels))

    async def delete_card(self, card_id: str) -> None:
        """Delete a Trello card"""
        return await self._make_request('delete', f'/1/cards/{card_id}', None)

    async def get_card_comments(self, card_id: str) -> list[TrelloCommentDetails]:
        """Get all comments for a card"""
        params = {'filter': 'commentCard'}
        return await self._make_request('get', f'/1/cards/{card_id}/actions', TrelloCommentDetails, params=params)

    async def add_comment(self, card_id: str, comment_data: TrelloCommentCreate) -> TrelloCommentDetails:
        """Add a comment to a card"""
        return await self._make_request('post', f'/1/cards/{card_id}/actions/comments', TrelloCommentDetails,
                                        data=comment_data.model_dump(exclude_none=True, by_alias=True))

    async def update_comment(self, card_id: str, action_id: str,
                             comment_data: TrelloCommentUpdate) -> TrelloCommentDetails:
        """Update an existing comment"""
        return await self._make_request('put', f'/1/cards/{card_id}/actions/{action_id}/comments', TrelloCommentDetails,
                                        data=comment_data.model_dump(exclude_none=True, by_alias=True))

    async def get_card_attachments(self, card_id: str) -> list[TrelloAttachmentDetails]:
        """List all attachments on a card"""
        return await self._make_request('get', f'/1/cards/{card_id}/attachments', TrelloAttachmentDetails)

    async def get_attachment(self, card_id: str, attachment_id: str) -> TrelloAttachmentDetails:
        """Get a specific attachment details from a card"""
        return await self._make_request('get', f'/1/cards/{card_id}/attachments/{attachment_id}',
                                        TrelloAttachmentDetails)

    async def add_url_attachment(self, card_id: str, url: str, name: str | None = None) -> TrelloAttachmentDetails:
        """Add a URL attachment to a card (no file upload)"""
        params = {"url": url}
        if name:
            params["name"] = name
        return await self._make_request('post', f'/1/cards/{card_id}/attachments', TrelloAttachmentDetails,
                                        params=params)

    async def delete_attachment(self, card_id: str, attachment_id: str) -> None:
        """Delete an attachment from a card"""
        return await self._make_request('delete', f'/1/cards/{card_id}/attachments/{attachment_id}', None)

