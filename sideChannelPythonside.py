from mlagents_envs.environment import UnityEnvironment
from mlagents_envs.side_channel.side_channel import (
    SideChannel,
    IncomingMessage,
    OutgoingMessage,
)
import numpy as np
import uuid

class SideChannelPythonside(SideChannel):
    def __init__(self) -> None:
        super().__init__(uuid.UUID("621f0a70-4f87-11ea-a6bf-784f4387d1f7"))
        self.created_modules = []

    def on_message_received(self, msg: IncomingMessage) -> None:
        recieved = msg.read_string()
        print("[Unity]:", recieved)

        # If we recieved created modules
        if "Created modules: " in recieved:
            self.created_modules = []
            for index in recieved[len("Created modules: "):].split(",")[:-1]:
                self.created_modules.append(int(index))

    def send_string(self, data: str) -> None:
        print("[Python]: Sending data")
        # Add the string to an OutgoingMessage
        msg = OutgoingMessage()
        msg.write_string(data)
        # We call this method to queue the data we want to send
        super().queue_message_to_send(msg)
