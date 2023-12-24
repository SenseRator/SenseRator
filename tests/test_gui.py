# test_gui.py
import unittest
import sys
from pathlib import Path

# Add the parent directory to the sys.path
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

from gui_utils import set_layout

class TestGuiModule(unittest.TestCase):
    def test_set_layout_startup(self):
        window, layout = set_layout('startup')

        # Assertions to check if layout is correct for 'startup' state
        self.assertIsNotNone(window)
        self.assertIsNotNone(layout)
        self.assertGreater(len(layout), 0)  # Check if layout has elements

        # You can also check for specific elements in the layout if necessary

if __name__ == '__main__':
    unittest.main()
