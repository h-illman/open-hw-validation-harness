"""
Hardware Backend stub implementation.

This backend will eventually provide an interface for interacting with 
physical hardware (e.g., an FPGA over PCIe or UART).
"""

class HardwareBackendStub:
    """
    Hardware validation backend stub.
    """
    
    def __init__(self):
        """Initialize the hardware backend stub."""
        pass
        
    def connect(self):
        """Connect to the physical hardware target."""
        raise NotImplementedError("connect() not implemented for Phase 1")
        
    def program(self, bitstream_path):
        """Program the FPGA with a bitstream."""
        raise NotImplementedError("program() not implemented for Phase 1")
        
    def reset(self):
        """Issue a reset to the physical hardware target."""
        raise NotImplementedError("reset() not implemented for Phase 1")
