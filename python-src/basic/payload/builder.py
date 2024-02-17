class BasicBuilder(object):
    def __init__(self):
        pass
        
    def encode(self, name, group, msg):
        """
        Encodes the message with the format: length,group,name,msg.
        The length field ensures the receiver knows how much data to expect.
        """
        payload = f"{group},{name},{msg}"
        return f"{len(payload):04d},{payload}"

    def decode(self, raw):
        """
        Decodes the received message back into its parts.
        Assumes the first part is the message length (not used in decoding here).
        """
        parts = raw.split(",", 3)  # Split into 4 parts at most
        if len(parts) != 4:
            raise ValueError(f"Message format error: {raw}")
        # parts[0] is the length, which we don't need for further processing
        return parts[1], parts[2], parts[3]
