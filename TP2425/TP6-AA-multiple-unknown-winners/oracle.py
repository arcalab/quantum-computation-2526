import pennylane as qml
import json
import base64

class QuantumOracle:
    def __init__(self, input_registers, n_qubits, config_file):
        """
        Initialize the quantum oracle.

        Args:
            input_registers (list): The list of wires corresponding to the input register.
            n_qubits (int): Number of qubits in the register.
            config_file (str): Path to the JSON configuration file.
        """
        self.input_registers = input_registers
        self.n_qubits = n_qubits
        self.marked_states, self.solutions = self._load_config(config_file)

    def _load_config(self, config_file):
        """
        Load and decode marked states and solutions from the JSON configuration file.

        Args:
            config_file (str): Path to the JSON file containing the oracle configuration.

        Returns:
            tuple: Decoded list of marked states and solutions.
        """
        with open(config_file, "r") as f:
            data = json.load(f)

        # Decode Base64-encoded marked states and solutions into binary strings
        marked_states = [self._decode_base64(state) for state in data["marked_states"]]
        solutions = [self._decode_base64(solution) for solution in data["solutions"]]
        return marked_states, solutions

    def _decode_base64(self, encoded_str):
        """
        Decode a Base64-encoded string into a binary string.

        Args:
            encoded_str (str): The Base64-encoded string.

        Returns:
            str: Decoded binary string.
        """
        return bin(int(base64.b64decode(encoded_str).decode("utf-8")))[2:].zfill(self.n_qubits)

    def apply_oracle(self):
        """
        Apply the oracle to the quantum circuit based on the marked states.
        """
        # Increment the register
        qml.Adder(1, self.input_registers, 2**self.n_qubits)
        
        # Apply the oracle logic for each marked state
        for state in self.marked_states:
            # Apply X gates to flip qubits matching the target state
            for i, bit in enumerate(state):
                if bit == "0":
                    qml.PauliX(wires=self.input_registers[i])
            # Apply a multi-controlled Z gate
            qml.ControlledQubitUnitary(qml.PauliZ(self.input_registers[-1]), control_wires=self.input_registers[:-1])
            # Undo the X gates
            for i, bit in enumerate(state):
                if bit == "0":
                    qml.PauliX(wires=self.input_registers[i])

        # Decrement the register
        qml.Adder(-1, self.input_registers, 2**self.n_qubits)

    def is_solution(self, x):
        """
        Check if a given input is a solution based on the solutions entry.

        Args:
            x (int): The input value to check.

        Returns:
            int: 1 if the input is a solution, 0 otherwise.
        """
        binary_x = "".join(bin(i)[2:] for i in x) 
        return 1 if binary_x in self.solutions else 0