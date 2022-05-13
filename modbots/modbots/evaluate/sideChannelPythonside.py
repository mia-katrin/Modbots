from mlagents_envs.side_channel.side_channel import (
    SideChannel,
    IncomingMessage,
    OutgoingMessage,
)
import uuid
import ast

class SideChannelPythonside(SideChannel):
    def __init__(self) -> None:
        super().__init__(uuid.UUID("621f0a70-4f87-11ea-a6bf-784f4387d1f7"))
        self.created_modules = []
        self.coordinates = []

    def on_message_received(self, msg: IncomingMessage) -> None:
        recieved = msg.read_string()
        #print("[Unity]:", recieved)

        # If we recieved created modules
        if "Created modules: " in recieved and len(recieved) > len("Created modules: "):
            self.created_modules = ast.literal_eval(recieved[len("Created modules: "):])

        # If we recieved coordinates
        if recieved.startswith("Coordinates: ") and len(recieved) > len("Coordinates: "):
            self.coordinates = ast.literal_eval(recieved[len("Coordinates: "):])

    def send_string(self, data: str) -> None:
        #print("[Python]: Sending data")
        # Add the string to an OutgoingMessage
        msg = OutgoingMessage()
        msg.write_string(data)
        # We call this method to queue the data we want to send
        super().queue_message_to_send(msg)
