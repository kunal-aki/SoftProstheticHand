import unittest

from finger import Finger


class FingerTorqueTests(unittest.TestCase):
    def test_calculate_mcp_torque_returns_numeric_value(self):
        finger = Finger("Index", 3.0, 2.5, 2.0)
        finger.update_from_tendon_force(5.0)

        torque = finger.calculate_mcp_torque()

        self.assertIsInstance(torque, float)
        self.assertGreaterEqual(torque, 0.0)


if __name__ == "__main__":
    unittest.main()
