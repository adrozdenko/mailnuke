#!/usr/bin/env python3
"""Email deletion service"""

import asyncio
from googleapiclient.errors import HttpError
from typing import List, Tuple
from constants import MAX_RETRY_ATTEMPTS, BACKOFF_BASE_DELAY, USER_ID


class EmailDeleter:
    """Handles email deletion operations"""
    
    def __init__(self, gmail_client):
        self.gmail_client = gmail_client
        self.rate_limit_counter = 0
        self.lock = asyncio.Lock()
    
    async def delete_email_batch(self, message_ids: List[str]) -> Tuple[int, int]:
        """Delete batch of emails"""
        service = await self.gmail_client.get_service()
        
        # Try batch API first for better performance
        if await self._try_batch_delete(service, message_ids):
            return len(message_ids), 0
        
        # Fallback to individual deletion
        return await self._delete_individually(service, message_ids)
    
    async def _try_batch_delete(self, service, message_ids: List[str]) -> bool:
        """Attempt batch deletion using Gmail API"""
        for attempt in range(MAX_RETRY_ATTEMPTS):
            try:
                service.users().messages().batchModify(
                    userId=USER_ID,
                    body={
                        'ids': message_ids,
                        'addLabelIds': ['TRASH']
                    }
                ).execute()
                return True
            except HttpError as e:
                if not self._is_rate_limit_error(e):
                    return False
                if not await self._handle_rate_limit_retry(attempt):
                    return False
            except Exception:
                if not await self._handle_generic_retry(attempt):
                    return False
        return False
    
    async def _delete_individually(self, service, message_ids: List[str]) -> Tuple[int, int]:
        """Fallback individual email deletion"""
        deleted_count = 0
        error_count = 0
        
        for message_id in message_ids:
            if await self._delete_single_email(service, message_id):
                deleted_count += 1
            else:
                error_count += 1
        
        return deleted_count, error_count
    
    async def _delete_single_email(self, service, message_id: str) -> bool:
        """Delete single email with retry logic"""
        for attempt in range(MAX_RETRY_ATTEMPTS):
            try:
                service.users().messages().trash(userId=USER_ID, id=message_id).execute()
                return True
            except HttpError as e:
                if not self._is_rate_limit_error(e):
                    return False
                if not await self._handle_rate_limit_retry(attempt):
                    return False
            except Exception:
                if not await self._handle_generic_retry(attempt):
                    return False
        return False
    
    def _is_rate_limit_error(self, error: HttpError) -> bool:
        """Check if error is rate limit related"""
        error_str = str(error)
        return "429" in error_str or "403" in error_str
    
    async def _handle_rate_limit_retry(self, attempt: int) -> bool:
        """Handle rate limit with backoff"""
        await self._increment_rate_limit_counter()
        if attempt < MAX_RETRY_ATTEMPTS - 1:
            delay = self._calculate_backoff_delay(attempt)
            await asyncio.sleep(delay)
            return True
        return False
    
    async def _handle_generic_retry(self, attempt: int) -> bool:
        """Handle generic errors with retry"""
        if attempt < MAX_RETRY_ATTEMPTS - 1:
            await asyncio.sleep(0.1)
            return True
        return False
    
    async def _increment_rate_limit_counter(self):
        """Thread-safe rate limit counter increment"""
        async with self.lock:
            self.rate_limit_counter += 1
    
    def _calculate_backoff_delay(self, attempt: int) -> float:
        """Calculate exponential backoff delay"""
        return BACKOFF_BASE_DELAY * (attempt + 1) * min(self.rate_limit_counter, 5)