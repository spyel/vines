from typing import Any, Callable, Awaitable, MutableMapping


Scope = MutableMapping[str, Any]
Message = MutableMapping[str, Any]

Receive = Callable[[], Awaitable[Message]]
Send = Callable[[Message], Awaitable[None]]

App = Callable[[Scope, Receive, Send], Awaitable[None]]
