# src/emrpy/telegrambot.py
"""
Telegram Trading Bot Module

A lightweight, async-first Telegram bot client optimized for trading notifications.
Built on top of python-telegram-bot library for reliability and ease of use.
"""

import asyncio
import logging
from typing import List, Optional

from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError

# Configure logging
logger = logging.getLogger(__name__)


class TelegramTradingBot:
    """
    Lightweight Telegram bot for trading notifications.

    Features:
    -----------
    - Async-first design for minimal latency impact
    - Simple message sending
    - Formatted trade alerts with emoji
    - Bulk notifications support
    - Built-in error handling and logging
    """

    def __init__(self, bot_token: str, chat_id: str, chat_name: Optional[str] = None):
        """
        Initialize a TelegramTradingBot instance.

        Parameters:
        -----------
        bot_token : str
            Your Telegram bot token from @BotFather.
        chat_id : str
            Target chat ID (user ID or group chat ID).
        chat_name : Optional[str], default None
            Human-readable name for the chat; if not provided, defaults to `chat_id`.

        Returns:
        --------
        None

        Examples:
        ---------
        >>> bot = TelegramTradingBot(
        ...     bot_token="123:ABC",
        ...     chat_id="987654321"
        ... )
        """
        self.bot = Bot(token=bot_token)
        self.chat_id = chat_id
        self.chat_name = chat_name or chat_id  # Use chat_id as fallback name

    async def send_message(
        self, text: str, parse_mode: Optional[str] = None, disable_notification: bool = False
    ) -> bool:
        """
        Send a text message to the configured Telegram chat asynchronously.

        Parameters:
        -----------
        text : str
            Content of the message to send.
        parse_mode : Optional[str], default None
            Formatting mode: 'HTML' or 'Markdown'. No formatting if None.
        disable_notification : bool, default False
            If True, send silently without notification sound.

        Returns:
        --------
        bool
            True if the message was sent successfully; False otherwise.

        Examples:
        ---------
        >>> success = await bot.send_message(
        ...     "Bot is now live 🚀",
        ...     parse_mode="Markdown"
        ... )
        """
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=text,
                parse_mode=parse_mode,
                disable_notification=disable_notification,
            )
            logger.debug(f"Message sent successfully to {self.chat_name}")
            return True

        except TelegramError as e:
            logger.error(f"Failed to send message to {self.chat_name}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending message: {e}")
            return False

    async def send_trade_alert(
        self,
        symbol: str,
        action: str,
        price: float,
        quantity: float,
        profit_loss: Optional[float] = None,
        disable_notification: bool = False,
    ) -> bool:
        """
        Send a formatted trade alert with structured layout and emoji indicators.

        Parameters:
        -----------
        symbol : str
            Trading symbol (e.g., 'BTCUSD', 'AAPL').
        action : str
            Trade action: 'BUY', 'SELL', or 'CLOSE'.
        price : float
            Execution price of the trade.
        quantity : float
            Quantity or size of the trade.
        profit_loss : Optional[float], default None
            Profit or loss amount; if provided, shows 📈 for profit or 📉 for loss.
        disable_notification : bool, default False
            If True, send silently without notification sound.

        Returns:
        --------
        bool
            True if the alert was sent successfully; False otherwise.

        Examples:
        ---------
        >>> await bot.send_trade_alert(
        ...     symbol="ETHUSD",
        ...     action="BUY",
        ...     price=1820.50,
        ...     quantity=1.2,
        ...     profit_loss=45.75
        ... )
        """
        # Choose emoji based on action and P/L
        if profit_loss is not None:
            pl_text = f"<b>P/L:</b> ${profit_loss:+.2f}"
            emoji = "📈" if profit_loss >= 0 else "📉"
        else:
            pl_text = ""
            if action.upper() == "BUY":
                emoji = "🟢"
            elif action.upper() == "SELL":
                emoji = "🔴"
            else:
                emoji = "💰"

        # Format the trade alert message
        message = f"""
                    {emoji} <b>TRADE ALERT</b>
                    <b>Symbol:</b> {symbol}
                    <b>Action:</b> {action.upper()}
                    <b>Price:</b> ${price:.4f}
                    <b>Quantity:</b> {quantity}
                    {pl_text}
                            """.strip()

        return await self.send_message(
            text=message, parse_mode=ParseMode.HTML, disable_notification=disable_notification
        )

    async def send_bulk_notifications(
        self,
        messages: List[str],
        parse_mode: Optional[str] = None,
        disable_notification: bool = False,
    ) -> List[bool]:
        """
        Send multiple messages concurrently to improve throughput.

        Parameters:
        -----------
        messages : List[str]
            List of message texts to send.
        parse_mode : Optional[str], default None
            Formatting mode for all messages: 'HTML' or 'Markdown'.
        disable_notification : bool, default False
            If True, send all messages silently without notification sound.

        Returns:
        --------
        List[bool]
            List of booleans indicating success status for each message.

        Examples:
        ---------
        >>> statuses = await bot.send_bulk_notifications(
        ...     ["Alert 1", "Alert 2"],
        ...     parse_mode="HTML"
        ... )
        """
        if not messages:
            logger.warning("Empty message list provided to send_bulk_notifications")
            return []

        # Create tasks for concurrent execution
        tasks = [self.send_message(msg, parse_mode, disable_notification) for msg in messages]

        try:
            # Execute all messages concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Convert exceptions to False, keep boolean results
            success_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Bulk message {i} failed: {result}")
                    success_results.append(False)
                else:
                    success_results.append(result)

            logger.info(
                f"Bulk notifications: {sum(success_results)}/{len(messages)} sent successfully"
            )
            return success_results

        except Exception as e:
            logger.error(f"Unexpected error in bulk notifications: {e}")
            return [False] * len(messages)
