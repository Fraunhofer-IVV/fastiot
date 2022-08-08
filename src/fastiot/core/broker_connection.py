import asyncio
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Coroutine, Dict, Union, AsyncIterator

import nats
from nats.aio.client import Client as BrokerClient, Subscription as BrokerSubscription, Msg as BrokerMsg
from pydantic import BaseModel

from fastiot.core.serialization import model_from_bin, model_to_bin
from fastiot.core.data_models import Subject
from fastiot.env import env_broker


class Subscription(ABC):
    @abstractmethod
    async def unsubscribe(self):
        """
        Cancels the subscription
        """

    @abstractmethod
    def check_pending_error(self):
        """
        Checks if an error is pending and raises it.
        """

    @abstractmethod
    async def raise_pending_error(self):
        """
        Waits for a pending error and raises it. Useful for testing.
        """


class SubscriptionImpl(Subscription):
    @dataclass
    class _StreamTaskHandler:
        time: float
        task: asyncio.Task

    def __init__(self,
                 subject: Subject,
                 on_msg_cb: Callable[[BaseModel], Union[Coroutine, AsyncIterator]],
                 send_reply_fn: Callable[[Subject, BaseModel], Coroutine],
                 max_pending_errors: int = 1000):
        self._subject = subject
        self._on_msg_cb = on_msg_cb
        self._send_reply_fn = send_reply_fn
        self._subscription = None

        self._current_stream_tasks: Dict[str, SubscriptionImpl._StreamTaskHandler] = {}

        self._stream_helper_task = None
        self._stream_helper_task_shutdown = asyncio.Event()
        if subject.stream_mode:
            self._stream_helper_task = asyncio.create_task(self._stream_helper_task_main())

        self._pending_errors = asyncio.Queue(maxsize=max_pending_errors)

    def _set_subscription(self, subscription: BrokerSubscription):
        self._subscription = subscription

    @classmethod
    def _get_time_in_s(cls) -> float:
        return time.time()

    async def _stream_helper_task_main(self):
        while self._stream_helper_task_shutdown.is_set() is False:
            to_stop = []
            stop_time = self._get_time_in_s() + env_broker.stream_timeout
            for key, value in self._current_stream_tasks.items():
                if value.time < stop_time:
                    to_stop.append(key)

            for key in to_stop:
                self._current_stream_tasks[key].task.cancel()

            for key in to_stop:
                await self._current_stream_tasks[key].task
                del self._current_stream_tasks[key]

            await asyncio.sleep(1)

    async def _received_msg_cb(self, nats_msg: BrokerMsg):
        try:
            obj = model_from_bin(self._subject.msg_cls, nats_msg.data)

            if self._subject.reply_cls is None:
                await self._on_msg_cb(nats_msg.subject, obj)
            elif self._subject.stream_mode is False:
                ans = await self._on_msg_cb(nats_msg.subject, obj)
                if not isinstance(ans, self._subject.reply_cls):
                    raise TypeError(f"Callback has not returned correct type: Expected type {self._subject.reply_cls}, "
                                    f"got {type(ans)}")
                reply_subject = Subject(
                    name=nats_msg.reply,
                    msg_cls=self._subject.reply_cls
                )
                await self._send_reply_fn(reply_subject, ans)
            else:
                if nats_msg.reply in self._current_stream_tasks:
                    self._current_stream_tasks[nats_msg.reply].time = self._get_time_in_s()
                else:
                    generator = self._on_msg_cb(nats_msg.subject, obj)
                    self._current_stream_tasks[nats_msg.reply] = SubscriptionImpl._StreamTaskHandler(
                        time=self._current_stream_tasks[nats_msg.reply].time,
                        task=asyncio.create_task(self._handle_stream_task(generator, nats_msg.reply))
                    )

        finally:
            pass

    async def _handle_stream_task(self, iterator: AsyncIterator, reply: str):
        reply_subject = Subject(
            name=reply,
            msg_cls=self._subject.reply_cls
        )
        while True:
            ans = await iterator.__anext__()
            if isinstance(ans, self._subject.reply_cls):
                raise TypeError(f"Callback has not returned correct type: Expected type {self._subject.reply_cls}, "
                                f"got {type(ans)}")
            await self._send_reply_fn(reply_subject, ans)

    async def unsubscribe(self):
        if self._stream_helper_task:
            self._stream_helper_task_shutdown.set()
            await self._stream_helper_task

        to_stop = list(self._current_stream_tasks)

        for key in to_stop:
            self._current_stream_tasks[key].task.cancel()

        for key in to_stop:
            await self._current_stream_tasks[key].task
            del self._current_stream_tasks[key]
        await self._subscription.unsubscribe()

    def check_pending_error(self):
        pass

    async def raise_pending_error(self):
        pass


class BrokerConnection(ABC):
    @abstractmethod
    async def subscribe(self,
                        subject: Subject,
                        cb: Callable[[BaseModel], Union[Coroutine, AsyncIterator]]) -> Subscription:
        pass

    async def subscribe_msg_queue(self,
                                  subject: Subject,
                                  msg_queue: asyncio.Queue) -> Subscription:
        if subject.reply_cls is not None:
            raise ValueError("Subscribe msg queue only allowed for empty reply_cls")

        async def cb(_, msg):
            nonlocal msg_queue
            await msg_queue.put(msg)

        return await self.subscribe(subject=subject, cb=cb)

    @abstractmethod
    async def send(self, subject: Subject, msg: BaseModel, reply: Subject = None):
        pass

    async def publish(self, subject: Subject, msg: Any):
        if subject.reply_cls is not None:
            raise ValueError("Publish only allowed for empty reply_cls")
        await self.send(subject=subject, msg=msg)

    async def request(self, subject: Subject, msg: Any, timeout: float = env_broker.default_timeout) -> Any:
        if subject.reply_cls is None:
            raise ValueError("Expected reply cls for request")
        if subject.stream_mode is True:
            raise ValueError("Expected stream mode to be false for request")
        inbox = subject.make_generic_reply_inbox()
        msg_queue = asyncio.Queue()
        sub = await self.subscribe_msg_queue(subject=inbox, msg_queue=msg_queue)
        try:
            await self.send(subject=subject, msg=msg, reply=inbox)
            result = await asyncio.wait_for(msg_queue.get(), timeout=timeout)
        finally:
            await sub.unsubscribe()
        return result

    async def beat(self, subject: Subject, msg: Any):
        if subject.stream_mode is False:
            raise ValueError("Expected stream mode to be true for beat")
        await self.send(subject=subject, msg=msg)


class BrokerConnectionImpl(BrokerConnection):

    @classmethod
    async def connect(cls) -> "BrokerConnectionImpl":
        client = await nats.connect(f"nats://{env_broker.host}:{env_broker.port}")
        return cls(
            client=client
        )

    def __init__(self, client: BrokerClient):
        self._client = client

    async def close(self):
        await self._client.close()

    async def subscribe(self,
                        subject: Subject,
                        cb: Callable[[BaseModel], Union[Coroutine, AsyncIterator]]) -> Subscription:
        impl = SubscriptionImpl(
            subject=subject,
            on_msg_cb=cb,
            send_reply_fn=self.send
        )
        subscription = await self._client.subscribe(
            subject=subject.name,
            cb=impl._received_msg_cb
        )
        impl._set_subscription(subscription=subscription)
        return impl

    async def send(self, subject: Subject, msg: BaseModel, reply: Subject = None):
        payload = model_to_bin(msg)
        reply_str = '' if reply is None else reply.name
        await self._client.publish(
            subject=subject.name,
            payload=payload,
            reply=reply_str
        )


class BrokerConnectionTestImpl(BrokerConnection):

    def __init__(self):
        self._sublist = []

    @abstractmethod
    async def subscribe(self, subject: Subject, cb: Callable[..., Coroutine]) -> Subscription:
        pass

    @abstractmethod
    async def send(self, subject: Subject, msg: BaseModel, reply: Subject = None):
        pass
